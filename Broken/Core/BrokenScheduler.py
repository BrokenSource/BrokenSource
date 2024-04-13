import contextlib
import functools
import inspect
import time
from threading import Lock
from typing import Any, Callable, Dict, Iterable, List, Self

from attr import Factory, define, field

from Broken import BIG_BANG
from Broken.Types import Hertz, Seconds


@define
class BrokenTask:
    """
    Client configuration for BrokenScheduler

    # Function:
    - callback:   Function callable to call every synchronization
    - args:       Arguments to pass to callback
    - kwargs:     Keyword arguments to pass to callback
    - output:     Output of callback (returned value)
    - context:    Context to use when calling callback (with statement)
    - lock:       Lock to use when calling callback (with statement)
    - enabled:    Whether to enable this client or not
    - once:       Whether to call this client only once or not

    # Synchronization
    - frequency:  Frequency of callback calls
    - frameskip:  Constant deltatime mode (False) or real deltatime mode (True)
    - decoupled:  "Rendering" mode, do not sleep on real time, implies frameskip False

    # Timing:
    - next_call:  Next time to call callback (initializes $now+next_call, value in now() seconds)
    - last_call:  Last time callback was called (initializes $now+last_call, value in now() seconds)
    - started:    Time when client was started (initializes $now+started, value in now() seconds)
    - time:       Whether to pass time (time since first call) to callback
    - dt:         Whether to pass dt (time since last call) to callback
    """

    # Callback
    callback: callable       = None
    args:     List[Any]      = field(factory=list, repr=False)
    kwargs:   Dict[str, Any] = field(factory=dict, repr=False)
    output:   Any            = field(default=None, repr=False)
    context:  Any            = None
    lock:     Lock           = None
    enabled:  bool           = True
    once:     bool           = False

    # Synchronization
    frequency:  Hertz = 60.0
    frameskip:  bool  = True
    decoupled:  bool  = False
    precise:    bool  = False

    # Timing
    started:   Seconds = Factory(lambda: time.bang_counter())
    next_call: Seconds = None
    last_call: Seconds = None
    _time:     bool    = False
    _dt:       bool    = False

    def __attrs_post_init__(self):
        signature = inspect.signature(self.callback)
        self._dt   = ("dt"   in signature.parameters)
        self._time = ("time" in signature.parameters)

        # Assign idealistic values for decoupled
        if self.decoupled: self.started = BIG_BANG
        self.last_call = (self.last_call or self.started)
        self.next_call = (self.next_call or self.started)

        # Note: We could use numpy.float128 for the most frametime precision on the above..
        #       .. But the Client code is smart enough to auto adjust itself to sync

    # # Useful properties

    @property
    def fps(self) -> Hertz:
        return self.frequency

    @fps.setter
    def fps(self, value: Hertz):
        self.frequency = value

    @property
    def period(self) -> Seconds:
        return 1/self.frequency

    @period.setter
    def period(self, value: Seconds):
        self.frequency = 1/value

    @property
    def should_delete(self) -> bool:
        return self.once and (not self.enabled)

    # # Sorting

    def __lt__(self, other: Self) -> bool:
        return self.next_call < other.next_call

    def __gt__(self, other: Self) -> bool:
        return self.next_call > other.next_call

    # # Implementation

    def next(self, block: bool=True) -> None | Any:

        # Time to wait for next call if block
        # - Next call at 110 seconds, now=100, wait=10
        # - Positive means to wait, negative we are behind
        wait = (self.next_call - time.bang_counter())

        if self.decoupled:
            pass
        elif block:
            if self.precise:
                time.precise_sleep(wait)
            else:
                time.sleep(max(0, wait))
        elif wait > 0:
            return None

        # The assumed instant the code below will run instantly
        now = self.next_call if self.decoupled else time.bang_counter()
        if self._dt:   self.kwargs["dt"]   = (now - self.last_call)
        if self._time: self.kwargs["time"] = (now - self.started)

        # Enter or not the given context, call callback with args and kwargs
        with (self.lock or contextlib.nullcontext()):
            with (self.context or contextlib.nullcontext()):
                self.output = self.callback(*self.args, **self.kwargs)

        # Fixme: This is a better way to do it, but on decoupled it's not "dt perfect"
        # self.next_call = self.period * (math.floor(now/self.period) + 1)

        # Update future and past states
        self.last_call = now
        while self.next_call <= now:
            self.next_call += self.period

        # (Disabled && Once) clients gets deleted
        self.enabled = not self.once

        return self

@define
class BrokenScheduler:
    clients: List[BrokenTask] = Factory(list)

    def add_task(self, client: BrokenTask) -> BrokenTask:
        """Adds a client to the manager with immediate next call"""
        self.clients.append(client)
        return client

    def new(self, *a, **k) -> BrokenTask:
        """Wraps around BrokenVsync for convenience"""
        return self.add_task(BrokenTask(*a, **k))

    def once(self, *a, **k) -> BrokenTask:
        """Wraps around BrokenVsync for convenience"""
        return self.add_task(BrokenTask(*a, **k, once=True))

    def partial(self, callable: Callable, *a, **k) -> BrokenTask:
        """Wraps around BrokenVsync for convenience"""
        return self.once(callable=functools.partial(callable, *a, **k))

    # # Filtering

    @property
    def enabled_tasks(self) -> Iterable[BrokenTask]:
        """Returns a list of enabled clients"""
        for client in self.clients:
            if client.enabled:
                yield client

    @property
    def next_task(self) -> BrokenTask | None:
        """Returns the next client to be called"""
        return min(self.enabled_tasks)

    def _sanitize(self) -> None:
        """Removes disabled 'once' clients"""
        length = len(self.clients)
        for i, client in enumerate(reversed(self.clients)):
            if client.should_delete:
                del self.clients[length - i - 1]

    # # Actions

    def next(self, block=True) -> None | Any:
        try:
            if (client := self.next_task):
                return client.next(block=block)
        finally:
            self._sanitize()

    def all_once(self) -> None:
        """Calls all 'once' clients. Useful for @partial calls on the main thread"""
        for client in self.clients:
            if client.once:
                client.next()
        self._sanitize()

    # # Block-free next

    __work__: bool = False

    def smart_next(self) -> None | Any:
        # Note: Proof of concept. The frametime Ticking might be enough for ShaderFlow

        # Too close to the next known call, call blocking
        if abs(time.bang_counter() - self.next_task.next_call) < 0.005:
            return self.next(block=True)

        # By chance any "recently added" client was added
        if (call := self.next(block=False)):
            self.__work__ = True
            return call

        # Next iteration, wait for work but don't spin lock
        if not self.__work__:
            time.sleep(0.001)

        # Flag that there was not work done
        self.__work__ = False
