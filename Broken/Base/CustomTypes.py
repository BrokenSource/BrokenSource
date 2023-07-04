from . import *

# # Custom types, some Rust inspiration

# PIL.Image is a module, PIL.Image.Image is the class
PilImage  = PIL.Image.Image

# Stuff that accepts "anything that can be converted to X"
URL       = str

# def divide(a, b) -> Option[float, ZeroDivisionError]:
Option = Union
Ok     = True
Error  = False
Result = Union[Ok, Error]
Self   = Any
