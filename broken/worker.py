# Some multiprocessing classes are variables
# pyright: reportInvalidTypeForm=false

import functools
import inspect
import math
import time
from abc import abstractmethod
from collections.abc import Callable, Iterable
from multiprocessing import Condition as ProcessCondition
from multiprocessing import JoinableQueue as ProcessQueue
from multiprocessing import Manager, Process
from queue import Queue as ThreadQueue
from threading import Condition as ThreadCondition
from threading import Lock, Thread
from time import perf_counter as now
from typing import Any, Self, TypeAlias, Union
from uuid import UUID, uuid4

from attrs import Factory, define, field

WorkerType: TypeAlias = Union[Thread, Process]
"""Any stdlib concurrency primitive"""

# ---------------------------------------------------------------------------- #

@define(eq=False)
class WorkerTask:
    payload: Any
    created: float = Factory(now)

    @classmethod
    def get(cls, object: Union[Self, Any]) -> Self:
        if isinstance(object, WorkerTask):
            return object
        return cls(payload=object)

    uuid: UUID = Factory(uuid4)

    def __hash__(self) -> int:
        return self.uuid.int

    def __eq__(self, other: Self) -> bool:
        return (hash(self) == hash(other))

# ---------------------------------------------------------------------------- #

@define
class BrokenWorker:
    """
    A complete Thread and Process pool manager for easy parallelization primitives,
    task queueing, inheritance, results handling, self healing and more.

    References (Independently developed):
    - https://en.wikipedia.org/wiki/Thread_pool
    """

    # -------------------------------------------|
    # Static utilities

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
        """Easier threading.Thread() interface"""
        return cls._spawn(*args, **kwargs, _type=Thread)

    @classmethod
    @functools.wraps(_spawn)
    def process(cls, *args, **kwargs) -> Process:
        """Easier multiprocessing.Process() interface"""
        return cls._spawn(*args, **kwargs, _type=Process)

    @staticmethod
    @functools.cache
    def easy_lock(method: Callable) -> Callable:
        """Wrap a method with a common threading.Lock"""
        common_lock = Lock()

        @functools.wraps(method)
        def wrapped(*args, **kwargs) -> Any:
            with common_lock:
                return method(*args, **kwargs)

        return wrapped

    # -------------------------------------------|
    # Initialization

    def _type_setter(self, attribute, value):
        raise AttributeError("Worker type can't be changed after initialization")

    type: WorkerType = field(default=Thread, on_setattr=_type_setter)
    """The concurrency primitive to use, can't be changed after initialization"""

    size: int = field(default=1, converter=int)
    """How many workers to keep alive executing tasks"""

    def __attrs_post_init__(self):

        # Raise on non-generator main method implementation
        if not inspect.isgeneratorfunction(self.main):
            raise TypeError(f"{type(self).__name__}.{self.main.__name__}() function must 'yield' results")

        # Create internal structures
        self._signal  = self.condition_type()
        self._phoenix = self.condition_type()
        self._results = self.results_type()
        self._queue   = self.queue_type()
        BrokenWorker.thread(self._keep_alive)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *ignore) -> None:
        self.close()

    # -------------------------------------------|
    # Worker management

    _workers: set[WorkerType] = Factory(set)
    """The set of spawned workers, active or not"""

    @property
    def _alive(self) -> Iterable[WorkerType]:
        """Yields all active workers"""
        for worker in self._workers:
            if worker.is_alive():
                yield worker

    @property
    def _stopped(self) -> Iterable[WorkerType]:
        """Yields all inactive workers"""
        for worker in self._workers:
            if not worker.is_alive():
                yield worker

    @property
    def _still_alive(self) -> int:
        """Believe me, I am still alive"""
        return sum(1 for _ in self._alive)

    @property
    def _any_alive(self) -> bool:
        """Fast check if any worker is alive"""
        for _ in self._alive:
            return True
        return False

    def _sanitize(self) -> None:
        """Removes inactive workers on the set"""
        self._workers -= set(self._stopped)

    def join(self) -> None:
        """Waits for all pending tasks to finish processing"""
        self._queue.join()

    def close(self) -> None:
        """Wait tasks to finish and stops all workers"""
        self.join()
        self.size = 0

        # Stop all workers
        while self._any_alive:
            while (self._queue.qsize() > 0):
                if (not self._any_alive):
                    break
                time.sleep(0.005)
            self._queue.put(None)

        # Avoid queue leftovers next use
        self._queue = self.queue_type()

    # -------------------------------------------|
    # Tasks

    @property
    def condition_type(self) -> Union[ThreadCondition, ProcessCondition]:
        """The condition variable class compatible with worker type"""
        if (self.type is Thread):
            return ThreadCondition
        return ProcessCondition

    _signal: Union[ThreadCondition, ProcessCondition] = None
    """Signaling for when tasks are done"""

    _phoenix: Union[ThreadCondition, ProcessCondition] = None
    """Signaling for when any worker stops and needs to be replaced"""

    @property
    def queue_type(self) -> Union[ThreadQueue, ProcessQueue]:
        """The queue class compatible with worker type"""
        if (self.type is Thread):
            return ThreadQueue
        return ProcessQueue

    _queue: Union[ThreadQueue, ProcessQueue] = None
    """List of pending tasks to be processed"""

    manager: Manager = Factory(Manager)
    """Shared multiprocessing manager"""

    @property
    def results_type(self) -> dict:
        """The results container class compatible with worker type"""
        # Warn: Must use hash(task) if Process as it pickles than __hash__
        return (dict if (self.type is Thread) else self.manager.dict)

    _results: dict = None

    def clear_results(self) -> None:
        self._results.clear()

    # Inserters

    def put(self, task: Any) -> WorkerTask:
        """Submit a new task to the queue"""
        return (self._queue.put(task := WorkerTask.get(task)) or task)

    def extend(self, *tasks: Any) -> list[WorkerTask]:
        """Submit a list of tasks to the queue"""
        return list(map(self.put, tasks))

    def call(self, method: Callable, *args, **kwargs) -> WorkerTask:
        """Submit a new task to call a method with args and kwargs"""
        return self.put(functools.partial(method, *args, **kwargs))

    partial = call

    def map(self, method: Callable, inputs: Iterable, **kwargs) -> list[WorkerTask]:
        """Submit tasks to call a method on each item in inputs"""
        return list(self.call(method, item, **kwargs) for item in inputs)

    # Getters

    def get(self,
        task: Union[WorkerTask, Iterable[WorkerTask]],
        block: bool=False,
        timeout: float=None,
        poll: float=0.01,
        _start: float=None,
    ) -> Union[Any, list[Any], None, Exception, TimeoutError]:

        # Internal timer for timeouts
        _start: float = (_start or now())

        # Handle multiple tasks
        if isinstance(task, Iterable):
            return [BrokenWorker.get(**locals()) for task in task]

        key = hash(task)

        # Wait until the task is done
        while block and (key not in self._results):
            if (now() - _start) > (timeout or math.inf):
                return TimeoutError(task)
            with self._signal:
                self._signal.wait(poll)

        return self._results.pop(key, None)

    get_blocking = functools.partialmethod(get, block=True)

    # -------------------------------------------|
    # Internal stuff

    def store(self, task: WorkerTask, result: Any) -> None:
        with self._signal:
            self._results[hash(task)] = result
            self._signal.notify_all()

    def _keep_alive(self) -> None:
        """Ensures 'size' workers are running at any time"""
        while True:
            while (self._still_alive < self.size):
                self._workers.add(self._spawn(
                    target=self._supervisor,
                    _type=self.type,
                ))
            with self._phoenix:
                self._phoenix.wait(0.5)
            self._sanitize()

    def _supervisor(self) -> None:
        """Automatically handle getting tasks and storing results"""
        task: WorkerTask = None

        # Tracks new current task, stops on poison
        def iter_tasks() -> Iterable[Any]:
            nonlocal task

            while True:
                try:
                    if (task := self._queue.get(block=True)) is not None:
                        yield task.payload
                        continue
                    return
                finally:
                    self._queue.task_done()

        try:
            # Wrap 'main' outputs and store results
            for result in self.main(iter_tasks()):
                self.store(task, result)
        except GeneratorExit:
            pass
        except Exception as error:
            self.store(task, error)

        with self._phoenix:
            self._phoenix.notify_all()

    # -------------------------------------------|
    # Specific implementations

    @abstractmethod
    def main(self, tasks: Iterable[Callable]) -> Iterable[Any]:
        """A worker get tasks and yields results, calls them by default"""
        print(f"Callable {self.type.__name__} worker started")

        for task in tasks:
            yield task()

# ---------------------------------------------------------------------------- #

class __PyTest__:
    ...
