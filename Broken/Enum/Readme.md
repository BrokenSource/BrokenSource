<div align="justify">

<div align="center">
  <h1>♻️ BrokenEnum ♻️</h1>

  **Smarter** Python **Enum classes** with builtin **Automation** and **Safety**
</div>

<br>

# 🔥 Description

This package adds lots of utilities to the standard `Enum` class in Python

- **Convenient**: Find members by name or value (or both)
- **Cycling**: You can cycle through the options of an enum
- **Fast**: Functions are cached with `functools.lru_cache`

<br>

# 🚀 Examples
```python
# Import package
from Broken import BrokenEnum

# Define a render quality enum
class Quality(BrokenEnum):
    Low    = 0
    Medium = 1
    High   = 2

# Get values from key or name
assert Quality.get(0)     == Quality.Low
assert Quality.get("Low") == Quality.Low
assert Quality.get("low") == Quality.Low
assert Quality(2)         == Quality.High

# It is safe to .get(member) themselves
assert Quality.get(Quality.Low) == Quality.Low

# If you want to search only by value or name
assert Quality.from_value(0)       == Quality.Low
assert Quality.from_value("low")   == None
assert Quality.from_name("medium") == Quality.Medium
Quality.from_name(2) # Raises ValueError

# Cycling through the options
assert Quality.Low.next()         == Quality.Medium
assert Quality.High.next()        == Quality.Low
assert Quality.Low.next(offset=2) == Quality.High

# Can cycle through the options in reverse and from member
value = Quality.Low
assert value.previous() == Quality.High
assert (value := value.previous(2)) == Quality.Medium

# Getting list of members or names, keys
assert Quality.values  == (0, 1, 2)
assert Quality.names   == ("Low", "Medium", "High")
assert Quality.keys    == ("Low", "Medium", "High")
assert Quality.options == (
    Quality.Low,
    Quality.Medium,
    Quality.High,
)

# Get tuples or key, value
assert Quality.items == (
    ("Low",    0),
    ("Medium", 1),
    ("High",   2),
)

# Get options as a dictionary
assert Quality.dict == dict(Low=0, Medium=1, High=2)
```

</div>