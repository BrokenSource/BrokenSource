import functools
import time
from threading import Thread
from typing import Any, Callable, Dict, List

from attr import define

from Broken import last_locals


@define
class BrokenThreadPool:
    threads: List[Thread] = []
    max:     int          = 1

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
        pool: str=None,
        max: int=1,
        daemon: bool=False,
        locals: bool=False,
        self: bool=False,
        callback: Callable=None,
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
            pool:   Name of the pool to append the thread to, see BrokenThreadPool
            max:    Maximum threads in the pool
            daemon: When the main thread exits, daemon threads are also terminated

        Advanced:
            locals:   Whether to pass the current scope locals to the callable or not
            self:     Include "self" in the locals if locals=True
            callback: Function to call after the thread finishes

        Returns:
            The created Thread object
        """

        # Update kwargs with locals
        if locals: kwargs.update(last_locals(level=2, self=self))
        the_target = target

        # Wrap the callback in a loop
        @functools.wraps(target)
        def looped(*args, **kwargs):
            while True:
                target(*args, **kwargs)
        the_target = (looped if loop else the_target)

        # Wrap the target in a callback
        @functools.wraps(target)
        def callbacked(*args, **kwargs):
            target(*args, **kwargs)
            if callback is not None:
                callback()
        the_target = (callbacked if callback else the_target)

        # Create Thread object
        parallel = Thread(
            target=the_target,
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
