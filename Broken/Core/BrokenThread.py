from __future__ import annotations

import functools
import time
from abc import abstractmethod
from collections.abc import Callable, Hashable, Iterable
from multiprocessing import Process, Queue
from pathlib import Path
from threading import Lock, Thread
from typing import Any, Optional, Self, TypeAlias, Union

from attrs import Factory, define
from diskcache import Cache as DiskCache

from Broken.Core import StaticClass
from Broken.Types import MB

# ------------------------------------------------------------------------------------------------ #

class BrokenThread(StaticClass):

    @staticmethod
    def new(
        target: Callable, /,
        *args: Any,
        start: bool=True,
        join: bool=False,
        loop: float=0.0,
        daemon: bool=True,
        **kwargs,
    ) -> Thread:
        """
        Create a thread on a callable, yeet whatever you think it works

        Args:
            target: The function to call, consider using functools.partial or this kwargs
            args:   Arguments to pass to the function (positional, unnamed)
            kwargs: Keyword arguments to pass to the function
            start:  Start the thread immediately after creation
            join:   Wait for the thread to finish after creation
            loop:   Time to wait between function calls (0 for no loop)
            daemon: When the main thread exits, daemon threads are also terminated

        Returns:
            The created Thread object
        """

        @functools.wraps(target)
        def looped(*args, **kwargs):
            while True:
                target(*args, **kwargs)
                time.sleep(loop)

        # Optional override target with loop wrap
        target = (looped if loop else target)

        # Create Thread object
        task = Thread(
            target=target,
            daemon=daemon,
            kwargs=kwargs,
            args=args,
        )

        if (start):
            task.start()

        # Useful if need action on another thread
        if (join and start):
            task.join()

        return task

    _easy_locks: dict[str, Callable] = dict()

    @staticmethod
    def easy_lock(method: Callable) -> Callable:
        """Get a wrapper with a common Lock for a method"""
        shared_lock = Lock()

        @functools.wraps(method)
        def wrapper(*args, **kwargs) -> Any:
            with shared_lock:
                return method(*args, **kwargs)

        return BrokenThread._easy_locks.setdefault(method, wrapper)

# ------------------------------------------------------------------------------------------------ #

Worker: TypeAlias = Union[Thread, Process]
"""A parallelizable object"""

@define
class WorkerPool:

    size: int = 0
    """Target number of workers in the pool"""

    type: Worker = Thread
    """Type of worker to use"""

    workers: set[Worker] = Factory(set)
    """Collection of workers in the pool"""

    # # Utilities

    @property
    def alive(self) -> Iterable[Worker]:
        for worker in self.workers:
            if worker.is_alive():
                yield worker

    @property
    def still_alive(self, count: int=0) -> int:
        """Believe me I am still alive"""
        for _ in self.alive:
            count += 1
        return count

    # # Actions

    def sanitize(self) -> None:
        self.workers = set(self.alive)

    def add_worker(self, worker: Worker, *, poll: float=0.01) -> Worker:
        while (self.still_alive >= self.size):
            time.sleep(poll)
        worker.start()
        self.workers.add(worker)
        self.sanitize()
        return worker

    def join(self, timeout: Optional[float]=None) -> None:
        for worker in self.workers:
            worker.join(timeout)

    # # Automation

    def keep_alive(self, method: Callable) -> Self:
        """Ensure 'size' workers are always running 'method'"""
        BrokenThread.new(self._keep_alive, method)
        return self

    def _keep_alive(self, method: Callable) -> None:
        while True:
            self.add_worker(self.type(
                target=method,
                daemon=True
            ), poll=0.5)

# ------------------------------------------------------------------------------------------------ #

@define
class ParallelQueue(WorkerPool):

    tasks: Queue = Factory(Queue) # Todo: PriorityQueue on Process?
    """Queue of tasks to be processed by the workers"""

    cache_data: DiskCache = None
    cache_path: Path = None
    cache_size: int = 500
    """Maximum size of the cache in megabytes"""

    def __attrs_post_init__(self):

        # Thread and process safe data cache
        if (self.cache_size and self.cache_path):
            self.cache_data = DiskCache(
                directory=Path(self.cache_path),
                size_limit=int(self.cache_size)*MB,
            )
        else:
            raise NotImplementedError("In-memory cache not implemented")

    # # Abstract methods

    @abstractmethod
    def worker(self) -> None:
        """Worker function that processes tasks from the queue"""
        ...

    def next(self) -> Any:
        """A worker shall get a new task from here"""
        return self.tasks.get(block=True)

    def done(self, task: Hashable, result: Any) -> None:
        """A worker shall send the final result here"""
        self.cache_data[hash(task)] = result

    # # User actions

    def start(self) -> Self:
        return self.keep_alive(self.worker)

    def put(self, task: Hashable, *, timeout: int=30) -> None:
        """Queue a new task for processing, multi-call safe"""
        if (task not in self.cache_data):
            self.cache_data.set(task, None, expire=timeout)
            self.tasks.put(task)

    def get(self, task: Hashable) -> Union[Any, Exception, None]:
        """Get the result of a task, or None if it's still in progress"""
        result = self.cache_data.get(hash(task), None)

        # Allow for new equal tasks to be queued
        if isinstance(result, Exception):
            return self.cache_data.pop(hash(task))

        return result

    def get_blocking(self, task: Hashable, *, poll: float=0.1) -> Union[Any, Exception, None]:
        """Get the result of a task, blocking until it's finished"""
        while not (result := self.get(hash(task))):
            time.sleep(poll)
        return result

    def remove(self, task: Hashable) -> None:
        """Remove a task from the cache"""
        self.cache_data.pop(hash(task))

# ------------------------------------------------------------------------------------------------ #
