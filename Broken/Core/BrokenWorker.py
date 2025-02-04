from __future__ import annotations

import copy
import functools
import inspect
import time
from abc import abstractmethod
from collections.abc import Callable, Hashable, Iterable
from multiprocessing import JoinableQueue as ProcessQueue
from multiprocessing import Manager, Process
from pathlib import Path
from queue import Queue
from queue import Queue as ThreadQueue
from threading import Lock, Thread
from typing import Any, Generator, List, Optional, Self, TypeAlias, Union

import dill
from attrs import Factory, define, field
from diskcache import Cache as DiskCache

from Broken import flatten, log
from Broken.Core import easyloop
from Broken.Types import MB

WorkerType: TypeAlias = Union[Thread, Process]
"""Any stdlib parallelizable primitive"""

MANAGER = Manager()
"""Global multiprocessing manager"""


@define(eq=False)
class BrokenWorker:
    """
    A semi-complete Thread and Process manager for easy parallelization primitives, smart task
    queueing, caching results and more.

    References:
    - Independently reinvented https://en.wikipedia.org/wiki/Thread_pool
    """

    # # Static utilities

    @staticmethod
    def _spawn(
        target: Callable,
        *args: Any,
        daemon: bool=True,
        _type: WorkerType=Thread,
        **kwargs,
    ) -> WorkerType:
        worker = _type(
            target=target,
            daemon=daemon,
            kwargs=kwargs,
            args=args,
        )
        worker.start()
        return worker

    @classmethod
    @functools.wraps(_spawn)
    def thread(cls, *args, **kwargs) -> Thread:
        return cls._spawn(*args, **kwargs, _type=Thread)

    @classmethod
    @functools.wraps(_spawn)
    def process(cls, *args, **kwargs) -> Process:
        return cls._spawn(*args, **kwargs, _type=Process)

    # # Easy lock

    @staticmethod
    @functools.cache
    def easy_lock(method: Callable) -> Callable:
        """Get a wrapper with a common threading.Lock for a method, multi-call safe"""

        shared_lock = Lock()

        @functools.wraps(method)
        def wrapped(*args, **kwargs) -> Any:
            with shared_lock:
                return method(*args, **kwargs)

        return wrapped

    # # Initialization

    type: WorkerType = Thread
    """The primitive to use for parallelization"""

    size: int = field(default=1, converter=int)
    """How many workers to keep alive"""

    workers: set[WorkerType] = Factory(set)
    """The currently alive workers"""

    queue: Union[ThreadQueue, ProcessQueue] = None
    """The list of tasks to be processed"""

    @property
    def queue_type(self) -> type[Queue]:
        if (self.type is Thread):
            return ThreadQueue
        return ProcessQueue

    @property
    def diskcache_enabled(self) -> bool:
        return (self.cache_size and self.cache_path)

    @property
    def cache_dict_type(self) -> type[dict]:
        return (dict if (self.type is Thread) else MANAGER.dict)

    def __attrs_post_init__(self):

        # Initialize DiskCache or dict cache
        if (self.diskcache_enabled):
            self.cache_data = DiskCache(
                directory=Path(self.cache_path),
                size_limit=int(self.cache_size)*MB,
            )
        else:
            self.cache_data = self.cache_dict_type()

        # Initialize remaining items
        self.queue = self.queue_type()
        BrokenWorker.thread(self.keep_alive_thread)

    # # Worker management

    @property
    def alive(self) -> Iterable[WorkerType]:
        """Iterates over the alive workers"""
        for worker in self.workers:
            if worker.is_alive():
                yield worker

    @property
    def still_alive(self) -> int:
        """Believe me, I am still alive"""
        return sum(1 for _ in self.alive)

    def sanitize(self) -> None:
        """Removes dead workers on the set"""
        self.workers = set(self.alive)

    def join_workers(self, timeout: Optional[float]=None) -> None:
        """Waits for all workers to finish"""
        for worker in copy.copy(self.workers):
            worker.join(timeout)

    # # Caching

    cache_data: Union[dict, DiskCache] = None
    """The cached results database"""

    cache_path: Path = None
    """(DiskCache) Path to the cache directory, disabled if None"""

    cache_size: int = 500
    """(DiskCache) Maximum size of the cache in megabytes"""

    def clear_cache(self) -> None:
        self.cache_data.clear()

    # # Serde middleware for Process

    def __serialize__(self, object: Any) -> Any:
        if (self.type is Process):
            return dill.dumps(object, recurse=True)
        return object

    def __deserialize__(self, object: Any) -> Any:
        if (self.type is Process):
            return dill.loads(object)
        return object

    # # Tasks

    def join_tasks(self) -> None:
        """Waits for all tasks to finish"""
        self.queue.join()

    def put(self, task: Hashable) -> Hashable:
        """Submit a new task directly to the queue"""
        return (self.queue.put(self.__serialize__(task)) or task)

    @abstractmethod
    def get(self, task: Hashable) -> Optional[Any]:
        """Get the result of a task, keeping it on cache (non-blocking)"""
        result = self.cache_data.get(hash(task), None)

        # Remove errors from cache to allow re-queueing
        if isinstance(result, Exception):
            return self.pop(task)

        return result

    def get_blocking(self, task: Hashable) -> Any:
        """Get the result of a task, keeping it on cache (waits to finish)"""
        while (result := self.get(hash(task))) is None:
            time.sleep(0.1)
        return result

    def pop(self, task: Hashable) -> Any:
        """Get the result of a task, removing it from cache"""
        return self.cache_data.pop(hash(task))

    def call(self, method: Callable, *args, **kwargs) -> Hashable:
        """Submit a new task to call a method with args and kwargs"""
        return self.put(functools.partial(method, *args, **kwargs))

    def get_smart(self, task: Hashable) -> Any:
        """Queues the task if not on cache, returns the result (blocking)"""
        if (result := self.get(task)) is None:
            return self.get_blocking(self.put(task))
        return result

    def map(self, *tasks: Hashable) -> List:
        """Puts all tasks in the queue and returns the results in order"""
        tasks = flatten(tasks)

        # Queues tasks not present in cache
        for task, result in zip(tasks, map(self.get, tasks)):
            if (result is None):
                self.put(task)

        # Returns the results in order
        return list(map(self.get_blocking, tasks))

    def map_call(self, method: Callable, inputs: Iterable, **kwargs) -> List:
        """Maps a method to a list of inputs, returns the results in order"""
        return self.map((
            functools.partial(method, item, **kwargs)
            for item in inputs
        ))

    # # Context

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def close(self) -> None:
        self.join_tasks()
        self.size = 0

        # Poison pill until it all ends
        while self.still_alive:
            while (self.queue.qsize() > 0):
                if (not self.still_alive):
                    break
                time.sleep(0.001)
            self.queue.put(None)

        # Avoid queue leftovers next use
        self.queue = self.queue_type()
        self.join_workers()

    # # Automation

    @easyloop
    def keep_alive_thread(self) -> None:
        """Ensures 'size' workers are running the supervisor"""
        while (self.still_alive < self.size):
            self.workers.add(self._spawn(
                target=self.__supervisor__,
                _type=self.type
            ))
        time.sleep(0.5)

    def __supervisor__(self) -> None:
        """Automatically handle getting tasks and storing results"""
        task: Any = None

        # Tracks new current 'task's, stops on None
        def get_tasks() -> Generator:
            nonlocal task

            while True:
                try:
                    if (task := self.queue.get(block=True)) is not None:
                        yield (task := self.__deserialize__(task))
                        continue
                    break
                finally:
                    self.queue.task_done()

        # Optional results are 'yielded', fail on non-generator main
        if not inspect.isgeneratorfunction(self.main):
            raise TypeError((
                f"{type(self).__name__}.main() function must be a generator, "
                "either 'yield result' or 'yield None' on the code."
            ))

        try:
            # Wraps 'main' outputs and store results
            for result in self.main(get_tasks()):
                self.store(task, result)
        except GeneratorExit:
            pass
        except Exception as error:
            self.store(task, error)
            raise error

    def store(self, task: Hashable, result: Optional[Any]) -> None:
        if (result is not None):
            self.cache_data[hash(task)] = result

    # # Specific implementations

    @abstractmethod
    def main(self, tasks: Iterable) -> Generator:
        """A worker gets tasks and yields optional results to be cached"""
        log.success(f"Worker {self.type.__name__} started")

        for task in tasks:
            yield task()
