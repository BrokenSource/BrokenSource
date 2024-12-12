from __future__ import annotations

import functools
import time
from collections.abc import Callable, Iterable
from multiprocessing import Process
from threading import Lock, Thread
from typing import Any, TypeAlias, Union

from attrs import Factory, define

Worker: TypeAlias = Union[Thread, Process]
"""A parallelizable object"""

POOLS: dict[str, WorkerPool] = dict()
"""Global worker pools tracker"""

@define
class WorkerPool:
    workers: set[Worker] = Factory(set)
    size: int = 1

    @property
    def alive(self) -> Iterable[Worker]:
        for worker in self.workers:
            if worker.is_alive():
                yield worker

    @property
    def n_alive(self) -> int:
        return len(self.alive)

    def sanitize(self) -> None:
        self.workers = set(self.alive)

    def append(self, worker: Worker) -> Worker:
        while (self.n_alive >= self.size):
            time.sleep(0.01)
        self.workers.append(worker)
        self.sanitize()
        worker.start()
        return worker

    def join(self) -> None:
        for worker in self.workers:
            worker.join()

@define
class BrokenThread:
    def __new__(cls, *args, **kwargs):
        raise RuntimeError("This class is not meant to be instantiated directly")

    @staticmethod
    def pool(name: str) -> WorkerPool:
        return POOLS.setdefault(name, WorkerPool())

    @staticmethod
    def join_all_pools() -> None:
        for pool in POOLS.values():
            pool.join()

    @staticmethod
    def new(
        target: Callable, /,
        *args: Any,
        start: bool=True,
        join: bool=False,
        loop: bool=False,
        period: float=0.0,
        pool: str=None,
        max: int=10,
        daemon: bool=True,
        **kwargs: dict[str, Any],
    ) -> Thread:
        """
        Create a thread on a callable, yeet whatever you think it works
        • Support for a basic Thread Pool, why no native way?

        Args:
            target: The function to call, consider using functools.partial or this kwargs
            args:   Arguments to pass to the function (positional, unnamed)
            kwargs: Keyword arguments to pass to the function
            start:  Start the thread immediately after creation
            join:   Wait for the thread to finish after creation
            loop:   Wrap the target callable in a loop
            period: Time in seconds to wait between calls in loop=True
            pool:   Name of the pool to append the thread to, see BrokenThreadPool
            max:    Maximum threads in the pool
            daemon: When the main thread exits, daemon threads are also terminated

        Returns:
            The created Thread object
        """

        @functools.wraps(target)
        def looped(*args, **kwargs):
            while True:
                target(*args, **kwargs)
                time.sleep(period)

        target = (looped if loop else target)

        # Create Thread object
        parallel = Thread(
            target=target,
            daemon=daemon,
            args=args,
            kwargs=kwargs
        )

        # Maybe wait for the pool to be free
        if pool and (pool := BrokenThread.pools.setdefault(pool, WorkerPool())):
            pool.max = max
            pool.append(parallel)
        if start:
            parallel.start()
        if (join and start):
            parallel.join()
        return parallel

    @staticmethod
    def easy_lock(method: Callable) -> Callable:
        lock = Lock()

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            with lock:
                return method(*args, **kwargs)

        return wrapper
