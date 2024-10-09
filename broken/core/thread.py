import functools
import time
from threading import Thread
from typing import Any, Callable, Dict, List

from attrs import define


@define
class BrokenThreadPool:
    threads: List[Thread] = []
    max: int = 1

    @property
    def alive(self) -> List[Thread]:
        return [thread for thread in self.threads if thread.is_alive()]

    @property
    def n_alive(self) -> int:
        return len(self.alive)

    def sanitize(self) -> None:
        self.threads = self.alive

    def append(self, thread: Thread, wait: float=0.01) -> Thread:
        while self.n_alive >= self.max:
            time.sleep(wait)
        self.sanitize()
        self.threads.append(thread)
        return thread

    def join(self) -> None:
        for thread in self.threads:
            thread.join()

@define
class BrokenThread:
    pools = {}

    def __new__(cls, *args, **kwargs) -> Thread:
        return cls.new(*args, **kwargs)

    @staticmethod
    def pool(name: str) -> BrokenThreadPool:
        return BrokenThread.pools.setdefault(name, BrokenThreadPool())

    @staticmethod
    def join_all_pools() -> None:
        for pool in BrokenThread.pools.values():
            pool.join()

    @staticmethod
    def new(
        target: Callable,
        *args: List[Any],
        start: bool=True,
        join: bool=False,
        loop: bool=False,
        period: float=0.0,
        pool: str=None,
        max: int=10,
        daemon: bool=False,
        **kwargs: Dict[str, Any],
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
        if pool and (pool := BrokenThread.pools.setdefault(pool, BrokenThreadPool())):
            pool.max = max
            pool.append(parallel)
        if start:
            parallel.start()
        if join and start:
            parallel.join()
        return parallel
