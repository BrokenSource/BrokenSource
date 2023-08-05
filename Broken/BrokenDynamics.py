from . import *


@attrs.define
class BrokenSecondOrderDynamics:
    """
    Simulate on time domain a progressive second order system

    # Equations
    A second order system is defined by the following equation:
    $$ y + k1*y' + k2*y'' = x + k3*x' $$

    This can be rewritten based on "intuitive" parameters:
    $$ f = 1/(2*pi*sqrt(k2)) $$
    $$ z = k1/(2*sqrt(k2)) $$
    $$ r = 2*k3/k1 $$

    Where the meaning of each term is:

    - f: Natural frequency of the system in Hertz, "the speed the system responds to a change in input"
    Also is the frequency the system tends to vibrate at, doesn't affect shape of the resulting motion

    - z: Damping coefficient, z=0 vibration never dies, z=1 is the critical limit where the sytem
    does not overshoot, z>1 increases this effect and the system takes longer to settle

    - r: Defines the initial response "time" of the system, when r=1 the system responds instantly
    to changes on the input, when r=0 the system takes a bit to respond (smoothstep like), when r<0
    the system "anticipates" motion

    These terms are rearranged into some smart math I don't understand using semi-implicit Euler method

    Hence why, most of this code is a Python-port of the code saw in the video

    # Sources:
    - https://www.youtube.com/watch?v=KPoeNZZ6H4s <- Code mostly took from here, thanks @t3ssel8r
    - https://en.wikipedia.org/wiki/Semi-implicit_Euler_method
    - Control System classes on my university which I got 6/10 final grade

    # FIXME: It's fast for builtin floats but slower on any numpy object?
    """

    # # State variables
    y:  float = 0

    # # Parameters
    frequency: float = 1
    zeta     : float = 1
    response : float = 0

    # # Internal variables
    _previous_x: float = 0
    _y_speed    : float = 0

    # # Properties and math that are subset of the parameters

    @property
    def k1(self) -> float:
        """Y velocity coefficient"""
        return self.zeta/(math.pi * self.frequency)

    @property
    def k2(self) -> float:
        """Y acceleration coefficient"""
        return 1/(self.radians*self.radians)

    @property
    def k3(self) -> float:
        """X velocity coefficient"""
        return (self.response * self.zeta) / (math.tau * self.frequency)

    @property
    def radians(self) -> float:
        """Natural frequency in radians per second"""
        return 2*math.pi*self.frequency

    @property
    def damping(self) -> float:
        """Damping ratio of some sort"""
        return self.radians * (abs(self.zeta*self.zeta - 1.0))**0.5

    # # Implementation of the second order system itself

    # Get super main instance class of BrokenGL
    def __init__(self, initial_value=None, *args, **kwargs) -> None:
        self.__attrs_init__(*args, **kwargs)
        self._set_initial_value(initial_value)

    def _set_initial_value(self, value: float) -> None:
        """Set initial value of the system"""
        if self.y is None:
            self._previous_x = value
            self.y           = value

    def update(self, target: float, dt: float, velocity=None) -> float:
        """
        Update the system with a new target value

        # Parameters
        - target  : Next target value to reach
        - dt      : Time delta since last update
        - velocity: Optional velocity to use instead of calculating it from previous values
        """
        self._set_initial_value(target)

        # Estimate velocity
        if velocity is None:
            velocity         = (target - self._previous_x)/dt
            self._previous_x = target

        # Clamp k2 to stable values without jitter
        if (self.radians * dt < self.zeta):
            k1 = self.k1
            k2 = max((self.k2, 0.5*(self.k1 + dt)*dt, self.k1*dt))

        # "Use pole matching when the system is very fast" <- This ought be the case with ShaderFlow
        else:
            t1    = exp(-self.zeta * self.radians * dt)
            alpha = 2 * t1 * (cos if self.zeta <= 1 else cosh)(self.damping*dt)
            t2    = 1/(1 + t1*t1 - alpha) * dt
            k1    = t2 * (1 - t1*t1)
            k2    = t2 * dt

        # Integrate position with velocity
        self.y += self._y_speed * dt

        # Integrate velocity with acceleration
        self._y_speed += (target + self.k3*velocity - self.y - k1*self._y_speed)/k2 * dt

        return self.y

    def next(self, target: float, dt: float, velocity=None) -> float:
        """Alias for update"""
        return self.update(target, dt, velocity)
