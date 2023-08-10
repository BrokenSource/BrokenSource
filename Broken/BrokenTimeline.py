from . import *


class Interpolation:
    """An interpolation function defines points in betwee (t=0, a) (t=1, b)"""
    def lerp(a, b, t, clamp=True):
        """Linear interpolation, a line"""
        return a + (b - a) * (t if not clamp else clip(t, 0, 1))

    def smoothstep(a, b, t, clamp=True):
        """Smooth interpolation with a cubic curve"""
        return Interpolation.lerp(a, b, t*t*(3 - 2*t), clamp)

    def sine(a, b, t, clamp=True):
        """Smooth interpolation with the shape of a sine wave"""
        return Interpolation.lerp(a, b, sin(t*pi/2), clamp)

    def step(a, t):
        """Steps to 1 at t >= a else zero"""
        return 1 if t >= a else 0

    def istep(a, t):
        """Steps to 0 at t >= a else one"""
        return 1 - Interpolation.step(a, t)

    def heaviside(a, b, t):
        """Steps to 1 when on the interval [a, b] else zero"""
        return Interpolation.step(a, t) * Interpolation.istep(b, t)

    def iheaviside(a, b, t):
        """Steps to 0 when on the interval [a, b] else one"""
        return 1 - Interpolation.heaviside(a, b, t)


class Continuous:
    """Generic and useful functions are defined here for keyframes"""

    # Trigonometric

    def sine(T: float, frequency: float=1, amplitude: float=1, offset: float=0) -> float:
        """Standard well known generic sine wave. Range: [-1, 1]"""
        return amplitude * sin(2*pi*frequency*T + offset)

    # # Basic waves

    def sawtooth(T: float, frequency: float=1, amplitude: float=1, offset: float=0) -> float:
        """Standard generic sawtooth wave. Range: [0, 1], starts at 0"""
        return amplitude * (2*T*frequency + offset) % 1

    def square(T: float, frequency: float=1, amplitude: float=1, offset: float=0) -> float:
        """Standard generic square wave. Range [-1, 1], starts at 1"""
        return amplitude * sign(sin(2*pi*frequency*T + offset))

    def triangle(T: float, frequency: float=1, amplitude: float=1, offset: float=0) -> float:
        """Standard generic triangle wave. Range [0, 1], starts at 0"""
        return 1 - 2 * amplitude * abs(Continuous.sawtooth(T, frequency, amplitude, offset)*2 - 1)

# -------------------------------------------------------------------------------------------------|

class BrokenKeyframe(ABC):
    """
    Defines a keyframe base class with common utils and optimizations
    - t: Normalized time between 0 and 1
    - T: Global time in seconds
    - tau: Time since start

    # Usage

    ```python
    class CustomKeyframe(BrokenKeyframe):
        def __init__(self, your, variables, here):
            ...

    # Initialize them with
    keyframe = CustomKeyFrame(...) @ (start, end)
    keyframe = CustomKeyFrame(...) @ start
    ```

    We use the @ operator so we can define own self initialization apart
    """
    def __matmul__(self, times: Union[float, Tuple[float, float]]) -> Self:
        """Define the time of a keyframe with @ (start, end)"""
        if isinstance(times, float):
            times = (times, inf)

        # Unpack tuple, show info, return
        self.start, self.end = times
        log.info(f"• Created Keyframe ({self.start:5.2f}s - {self.end:5.2f}s): [{self.__class__.__name__}] ")
        return self

    def _normalized_time(self, T: float) -> float:
        """Returns the normalized time between 0 and 1 relative to start and end"""
        return (T - self.start) / (self.end - self.start)

    def _smart_call(self, variables: DotMap, T: float) -> Option[DotMap, None]:
        """Smart calls .next() if in range with arguments, otherwise returns None"""

        # Do nothing if not in range
        if not (self.start <= T <= self.end):
            return None

        # Call the keyframe function
        return self.__call__(variables, T, self._normalized_time(T), T - self.start)

    @abstractmethod
    def __call__(self, variables: DotMap, T: float, t: float, tau: float) -> None:
        """Modifies variables based on time for this keyframe"""
        ...

# -------------------------------------------------------------------------------------------------|

class BrokenTimeline:
    def __init__(self, initial_variables: DotMap=None):
        self.keyframes = intervaltree.IntervalTree()
        self.initial_variables = initial_variables or DotMap()

    def add_keyframe(self, keyframe: BrokenKeyframe) -> None:
        """Adds a keyframe to the timeline"""
        self.keyframes.addi(keyframe.start, keyframe.end, keyframe)

    def at(self, T: float) -> DotMap:
        """Get variables values at time T"""
        variables = self.initial_variables

        # Iterate over all keyframes that affects this T
        # FIXME: Ideally keyframes[T], but older keyframes might leave some value unchanged?
        # FIXME: Tho it shouldn't be that slow applying hundreds of keyframes...
        for interval in self.keyframes[0:T]:
            keyframe = interval.data
            keyframe._smart_call(variables, T)

        return variables

    def __matmul__(self, T: float) -> DotMap:
        """Syntax sugar for (timeline @ T)"""
        return self.at(T)

# -------------------------------------------------------------------------------------------------|

def test_timeline():

    class CustomKeyframeA(BrokenKeyframe):
        def __call__(self, variables, T, t, tau):
            variables.A = Interpolation.lerp(a=0, b=1, t=t)
            variables.B = Interpolation.smoothstep(a=0, b=1, t=t)
            variables.C = Interpolation.heaviside(0.4, 0.6, t)

    class CustomKeyframeB(BrokenKeyframe):
        def __call__(self, variables, T, t, tau):
            variables.D = Continuous.triangle(tau, frequency=2, amplitude=0.5)

    # Create Timeline
    timeline = BrokenTimeline()

    # Add keyframes
    timeline.add_keyframe( CustomKeyframeA() @ (0.0, 1.0) )
    timeline.add_keyframe( CustomKeyframeB() @ 0.0 )

    # Import plotly
    import plotly.graph_objects as go

    # Axis
    X = linspace(0, 1, 1001)
    Y = dict()

    for T in X:
        success(f"• Time: {T:.2f}s", )
        variables = timeline.at(T)

        for key, value in variables.items():
            log.info(f"├─ {key.ljust(20)} = {value}")
            Y.setdefault(key, []).append(value)

    # Create plot
    fig = go.Figure()
    for key, value in Y.items():
        fig.add_trace(go.Scatter(x=X, y=value, name=key))
    fig.show()
