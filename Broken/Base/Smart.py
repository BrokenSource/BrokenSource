from . import *

# FIXME: I really don't know how to name this file and what other "smart" functions there might be

class BrokenSmart:
    def load_image(image: Union[PilImage, PathLike, URL], pixel="RGB", cache=True, echo=True) -> Option[PilImage, None]:
        """Smartly load 'SomeImage', a path, url or PIL Image"""

        # Nothing to do if already a PIL Image
        if isinstance(image, PilImage):
            return image

        try:
            # Load image if a path or url is supplied
            if any([isinstance(image, T) for T in (PathLike, str)]):
                if (path := BrokenPath.true_path(image)).exists():
                    info(f"Loading image from Path [{path}]", echo=echo)
                    return PIL.Image.open(path).convert(pixel)
                else:
                    info(f"Loading image from (maybe) URL [{image}]", echo=echo)
                    try:
                        requests = BROKEN_REQUESTS_CACHE if cache else requests
                        return PIL.Image.open(BytesIO(requests.get(image).content)).convert(pixel)
                    except Exception as e:
                        error(f"Failed to load image from URL or Path [{image}]: {e}", echo=echo)
                        return None
            else:
                error(f"Unknown image parameter [{image}], must be a PIL Image, Path or URL", echo=echo)
                return None

        # Can't open file
        except PIL.UnidentifiedImageError as e:
            error(f"Failed to load image [{image}]: {e}", echo=echo)
            return None

        except Exception:
            return None

class BrokenEasy:
    def Recurse(function: callable, **variables) -> Any:
        """
        Calls some function with the previous scope locals() updated by variables

        Use case are functions that are called recursively and need to be called with the same arguments

        ```python
        def function(with, many, arguments, and, only=3, one=True, modification="Nice"):
            ...
            if recurse_condition:
                BrokenEasy.Recurse(function, many=True)
        ```
        """

        # Get the previous scope locals() and update it with the variables
        previous_locals = inspect.currentframe().f_back.f_locals
        previous_locals.update(variables)

        # Filter out variables that are not in the function arguments
        previous_locals = {
            k: v for k, v in previous_locals.items()
            if k in inspect.getfullargspec(function).args
        }

        # Call and return the same function
        return function(**previous_locals)

    # A class inside a class, huh
    class CountTime():
        """
        Context Manager that counts the time it took to run

        ```python
        with BrokenEasy.CountTime() as counter:
            took_so_far = counter.took
            ...

        # Stays at (finish - start) time after exiting
        print(counter.took)
        ```
        """
        def __enter__(self):
            self.start = time.time()
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.end = time.time()

        @property
        def took(self):
            return getattr(self, "end", time.time()) - self.start

    def Benchmark(
        function: callable,
        benchmark_name: str=None,
        benchmark_method: Option["duration", "executions"]="duration",

        # Duration arguments
        benchmark_duration: float=5,
        benchmark_executions: int=100,

        # Callable arguments
        *args, **kwargs
    ):
        frametimes = []

        with tqdm(
            total=benchmark_duration if benchmark_method == "duration" else benchmark_executions,
            unit="s" if benchmark_method == "duration" else "it",
            unit_scale=True,
            leave=False,
        ) as progress_bar:

            with BrokenEasy.CountTime() as counter:
                while True:

                    # Call Function to benchmark
                    with BrokenEasy.CountTime() as call_time:
                        function(*args, **kwargs)
                        frametimes.append(call_time.took)

                    # Update progress bar and check finish conditions
                    if benchmark_method == "duration":
                        progress_bar.n = min(counter.took, benchmark_duration)
                        if counter.took > benchmark_duration:
                            break

                    elif benchmark_method == "executions":
                        progress_bar.update(1)
                        if len(frametimes) > benchmark_executions:
                            break

                    # Update progress bar description
                    progress_bar.set_description(f"Benchmarking: {benchmark_name or function.__name__} ({len(frametimes)/sum(frametimes):.3f} it/s)")

        # # Get a few status
        frametimes = numpy.array(frametimes)

        f = lambda x: f"{x:.3f} it/s"
        info(f"• Benchmark Results for {benchmark_name or function.__name__}: [Average {f(1.0/frametimes.mean())}] [Max {f(1.0/frametimes.min())}] [Min {f(1.0/frametimes.max())}] [Std {f((1/frametimes).std())}]")

