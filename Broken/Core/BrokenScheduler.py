import contextlib
import inspect
import time
from collections import deque
from collections.abc import Callable, Iterable
from threading import Lock
from typing import Any, Optional, Self

from attrs import Factory, define, field

# ------------------------------------------------------------------------------------------------ #

def precise(sleep: float, *, error: float=0.001) -> None:
    """A precise alternative of time.sleep(), low cpu near-end thread spin. Increases CPU usage."""
    start = time.perf_counter()

    # Sleep close to the due time
    if (ahead := max(0, sleep - error)):
        time.sleep(ahead)
    else:
        return

    # Spin the thread until the time is up (precise Sleep)
    while (time.perf_counter() - start) < sleep:
        pass

time.precise = precise

# ------------------------------------------------------------------------------------------------ #

NULL_CONTEXT = contextlib.nullcontext()

@define
class SchedulerTask:

    # # Basic

    task: Callable = None
    """Function callable to call every synchronization. Automatically sends a 'time' or 'dt'
    argument if the function's signature contains it"""

    args: list[Any] = field(factory=list, repr=False)
    """Method's positional arguments"""

    kwargs: dict[str, Any] = field(factory=dict, repr=False)
    """Method's keyword arguments"""

    output: Any = field(default=None, repr=False)
    """Method's return value of the last call"""

    context: Any = None
    """Context to use when calling task (with statement)"""

    lock: Lock = None
    """Threading Lock to use when calling task (with statement)"""

    enabled: bool = True
    """Whether to enable this client or not"""

    once: bool = False
    """Client will be removed after next call"""

    # # Synchronization

    frequency: float = 60.0
    """Ideal frequency of task calls"""

    frameskip: bool = True
    """Constant deltatime mode (False) or real deltatime mode (True)"""

    freewheel: bool = False
    """"Rendering" mode, do not sleep on real time, exact virtual frametimes"""

    precise: bool = False
    """Use precise time sleeping for near-perfect frametimes"""

    # # Timing

    started: float = Factory(lambda: time.absolute())
    """Time when client was started (initializes $now+started, value in now() seconds)"""

    next_call: float = None
    """Next time to call task (initializes $now+next_call, value in now() seconds)"""

    last_call: float = None
    """Last time task was called (initializes $now+last_call, value in now() seconds)"""

    # # Flags

    _dt: bool = False

    def __attrs_post_init__(self):
        signature = inspect.signature(self.task)
        self._dt = ("dt" in signature.parameters)

        # Assign idealistic values for decoupled
        if self.freewheel: self.started = time.zero
        self.last_call = (self.last_call or self.started) - self.period
        self.next_call = (self.next_call or self.started)

    # # Useful properties

    @property
    def fps(self) -> float:
        return self.frequency

    @fps.setter
    def fps(self, value: float):
        self.frequency = value

    @property
    def period(self) -> float:
        return (1.0 / self.frequency)

    @period.setter
    def period(self, value: float):
        self.frequency = (1 / value)

    @property
    def should_delete(self) -> bool:
        return (self.once and (not self.enabled))

    @property
    def should_live(self) -> bool:
        return (not self.should_delete)

    # # Sorting (prioritizes 'once' clients)

    def __lt__(self, other: Self) -> bool:
        if (self.once and not other.once):
            return True
        return (self.next_call < other.next_call)

    def __gt__(self, other: Self) -> bool:
        if (not self.once and other.once):
            return True
        return (self.next_call > other.next_call)

    # # Implementation

    def next(self, block: bool=True) -> Self:

        # Time to wait for next call if block
        wait = max(0, (self.next_call - time.absolute()))

        # Rendering is instant
        if self.freewheel:
            pass

        # Block until due
        elif block:
            if self.precise:
                time.precise(wait)
            else:
                time.sleep(wait)

        # Non-blocking not due yet
        elif wait > 0:
            return None

        # The assumed instant the code below will run instantly
        now = (self.next_call if self.freewheel else time.absolute())

        if (self._dt):
            self.kwargs["dt"] = (now - self.last_call)

            # Frameskip limits maximum dt to period
            if (not self.frameskip):
                self.kwargs["dt"] = min(self.kwargs["dt"], self.period)

        self.last_call = now

        # Enter contexts, call task with args and kwargs
        with (self.lock or NULL_CONTEXT):
            with (self.context or NULL_CONTEXT):
                self.output = self.task(*self.args, **self.kwargs)

        # Find a future multiple of period
        while (self.next_call <= now):
            self.next_call += self.period

        # (Disabled && Once) clients gets deleted
        self.enabled = (not self.once)
        return self

# ------------------------------------------------------------------------------------------------ #

@define
class BrokenScheduler:
    tasks: deque[SchedulerTask] = Factory(deque)

    def add(self, task: SchedulerTask) -> SchedulerTask:
        """Adds a task to the scheduler with immediate next call"""
        self.tasks.append(task)
        return task

    def new(self, task: Callable, **options) -> SchedulerTask:
        """Add a new task to the scheduler"""
        return self.add(SchedulerTask(task=task, **options))

    def once(self, task: Callable, **options) -> SchedulerTask:
        """Add a new task that shall only run once and immediately"""
        return self.add(SchedulerTask(task=task, **options, once=True))

    def delete(self, task: SchedulerTask) -> None:
        """Removes a task from the scheduler"""
        self.tasks.remove(task)

    def clear(self) -> None:
        """Removes all tasks"""
        self.tasks.clear()

    @property
    def enabled_tasks(self) -> Iterable[SchedulerTask]:
        for task in self.tasks:
            if task.enabled:
                yield task

    @property
    def next_task(self) -> Optional[SchedulerTask]:
        """Returns the next client to be called"""
        return min(self.enabled_tasks, default=None)

    def _sanitize(self) -> None:
        """Removes disabled 'once' clients"""
        # Optimization: Replace first N clients with valid ones, then pop remaining pointers
        move = 0
        for task in self.tasks:
            if task.should_live:
                self.tasks[move] = task
                move += 1
        for _ in range(len(self.tasks) - move):
            self.tasks.pop()

    def next(self, block=True) -> Optional[SchedulerTask]:
        if (task := self.next_task) is None:
            return None
        try:
            return task.next(block=block)
        finally:
            if task.should_delete:
                self._sanitize()

    def all_once(self) -> None:
        """Calls all 'once' clients. Useful for @partial calls on the main thread"""
        for task in self.tasks:
            if task.once:
                task.next()
        self._sanitize()
