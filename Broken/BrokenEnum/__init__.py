import enum
import functools
from typing import Any
from typing import Dict
from typing import Optional
from typing import Self
from typing import Tuple
from typing import Union

import attrs


class BrokenEnum(enum.Enum):

    # # Initialization

    @classmethod
    @functools.lru_cache(typed=True)
    def from_name(cls, name: str, *, lowercase: bool=True, must: bool=False) -> Optional[enum.Enum]:
        """
        Get enum members from their name

        Example:
            ```python
            class Fruits(BrokenEnum):
                Apple  = "Maçã"
                Banana = "Banana"
                Orange = "Laranja"

            Fruits.from_name("Apple")  -> Fruits.Apple
            Fruits.from_name("apple")  -> Fruits.Apple
            ```

        Args:
            name: Name of the member to get
            lowercase: Whether to lowercase the name and key before matching
            must: Whether to raise an error if the member is not found

        Returns:
            The enum member with the given name if found, None otherwise
        """
        # Key value must be a string
        if not isinstance(name, str):
            raise TypeError(f"Expected str, got {type(name).__name__} on BrokenEnum.from_name()")

        # Optionally lowercase name for matching
        name = name.lower() if lowercase else name

        # Search for the member by key
        for key, value in cls._member_map_.items():
            if (key.lower() if lowercase else key) == name:
                return value

        # Raise an error if the member was not found
        if must: raise ValueError(f"Member with name '{name}' not found on BrokenEnum.from_name()")

    @classmethod
    @functools.lru_cache(typed=True)
    def from_value(cls, value: Any, *, must: bool=False) -> Optional[enum.Enum]:
        """
        Get enum members from their value (name=value)

        Example:
            ```python
            class Fruits(BrokenEnum):
                Apple  = "Maçã"
                Banana = "Banana"
                Orange = "Laranja"

            Fruits.from_value("Maçã")   -> Fruits.Apple
            Fruits.from_value("Banana") -> Fruits.Banana
            ```

        Args:
            `value`: Value of the member to get
            `must`:  Whether to raise an error if the member is not found

        Returns:
            The enum member with the given value if found, None otherwise
        """
        # Scroll through all members, match by value
        for option in cls:
            if value == option.value:
                return option

        # Raise an error if the member was not found
        if must: raise ValueError(f"Member with value '{value}' not found on BrokenEnum.from_value()")

    # # Utilities properties

    # Values

    @classmethod
    @property
    @functools.lru_cache(typed=True)
    def members(cls) -> Tuple[enum.Enum]:
        """Get all members of the enum"""
        return tuple(cls)

    @classmethod
    @property
    @functools.lru_cache(typed=True)
    def options(cls) -> Tuple[enum.Enum]:
        """Get all members of the enum"""
        return cls.members

    @classmethod
    @property
    @functools.lru_cache(typed=True)
    def values(cls) -> Tuple[Any]:
        """Get all values of the enum (name=value)"""
        return tuple(member.value for member in cls)

    # Key/names properties

    @classmethod
    @property
    @functools.lru_cache(typed=True)
    def keys(cls) -> Tuple[str]:
        """Get all 'keys' of the enum (key=value)"""
        return tuple(member.name for member in cls)

    @classmethod
    @property
    @functools.lru_cache(typed=True)
    def names(cls) -> Tuple[str]:
        """Get all names of the enum (name=value)"""
        return cls.keys

    @classmethod
    @property
    @functools.lru_cache(typed=True)
    def names_lower(cls) -> Tuple[str]:
        """Get all names of the enum (name=value) in lowercase"""
        return tuple(name.lower() for name in cls.keys)

    # Items and dict-like

    @classmethod
    @property
    @functools.lru_cache(typed=True)
    def items(cls) -> Tuple[Tuple[str, Any]]:
        """Get the tuple of (name, value) of all members of the enum"""
        return tuple((member.name, member.value) for member in cls)

    @classmethod
    @property
    @functools.lru_cache(typed=True)
    def as_dict(cls) -> Dict[str, Any]:
        """Get the dictionary of key: value of all members of the enum"""
        return dict(cls.items)

    @classmethod
    @functools.lru_cache(typed=True)
    def to_dict(cls) -> Dict[str, Any]:
        """Alias for .as_dict, but as a method"""
        return cls.as_dict

    # # Smart methods

    @classmethod
    @functools.lru_cache(typed=True)
    def get(cls, value: Union[str, enum.Enum, Any], *, lowercase: bool=True) -> Optional[Self]:
        """
        Get enum members from their value, name or themselves

        Example:
            ```python
            # Inherit from this package
            class Multivalue(BrokenEnum):
                Color  = "blue"
                Hat    = False
                Age    = 9000
                Height = 1.41
                Emoji  = "🔱"

            # Use the .get method
            Multivalue.get("blue")   -> Multivalue.Color
            Multivalue.get(False)    -> Multivalue.Hat
            Multivalue.get("Height") -> Multivalue.Height
            Multivalue.get("height") -> Multivalue.Height

            # Use from a member itself
            Multivalue.get(Multivalue.Color) -> Multivalue.Color
            ```

        Args:
            `value`: Value to get the enum member from, can be the member's name or value

        Returns:
            The enum member with the given value if found, None otherwise
        """

        # Value is already a member of the enum
        if isinstance(value, cls):
            return value

        # Value is a string
        elif isinstance(value, str):
            return cls.from_name(value, lowercase=lowercase) or cls.from_value(value)

        # Search by value
        return cls.from_value(value)

    @functools.lru_cache(typed=True)
    def next(self, value: Union[str, enum.Enum]=None, offset: int=1) -> Self:
        """
        Get the next enum member (in position) from their value, name or themselves

        Example:
            ```python
            # Inherit from this package
            class Platform(BrokenEnum):
                Linux   = "linux"
                Windows = "windows"
                MacOS   = "macos"

            # Cycle through options
            Platform.next("linux")   -> Platform.Windows
            Platform.next("windows") -> Platform.MacOS
            Platform.next("macos")   -> Platform.Linux
            (...)
            ```

        Args:
            `value`: Value to get the next enum member from, can be the Option's name or value

        Returns:
            The next enum member (in position) from the given value
        """
        cls   = type(self)
        value = cls.get(value or self)
        return cls.options[(cls.options.index(value) + offset) % len(cls)]

    def __next__(self) -> Self:
        """Alias for .next, but as a method"""
        return self.next()

    @functools.lru_cache(typed=True)
    def previous(self, value: Union[str, enum.Enum]=None, offset: int=1) -> Self:
        """
        Get the previous enum member (in position) from their value, name or themselves

        Example:
            ```python
            # Inherit from this package
            class Platform(BrokenEnum):
                Linux   = "linux"
                Windows = "windows"
                MacOS   = "macos"

            # Cycle through options
            Platform.previous("linux")   -> Platform.MacOS
            Platform.previous("windows") -> Platform.Linux
            Platform.previous("macos")   -> Platform.Windows
            (...)
            ```

        Args:
            `value`: Value to get the previous enum member from, can be the Option's name or value

        Returns:
            The previous enum member (in position) from the given value
        """
        cls   = type(self)
        value = cls.get(value or self)
        return cls.options[(cls.options.index(value) - offset) % len(cls)]

    # # Advanced functions

    @classmethod
    def extend(cls, name: str, value: Any) -> Self:
        """
        Dynamically extend the enum with a new member (name=value)

        Example:
            ```python
            # Inherit from this package
            class Platform(BrokenEnum):
                ...

            # Extend the enum
            Platform.extend("Android", "android")

            # Use the new member
            platform = Platform.Android
            ```

        Args:
            `name`:  Name of the new member
            `value`: Value of the new member

        Returns:
            Fluent interface, the class that was extended
        """
        raise NotImplementedError("This method is not implemented yet")

    def field(self, **kwargs) -> attrs.Attribute:
        """
        Make a attrs.field() with this member as default and enum class's get method as converter

        Example:
            ```python
            class Platform(BrokenEnum):
                Linux   = "linux"
                Windows = "windows"
                MacOS   = "macos"

            @define
            class Computer:
                os: Platform = Platform.Linux.field()

            # Any setattr will be redirected to the enum's get method
            computer = Computer()
            computer.os = "linux" # Ok
            computer.os = "dne"   # Not ok
            ```

        Args:
            `kwargs`: Keyword arguments to pass to the field, may override default and converter
        """
        return attrs.field(default=self, converter=self.__class__.get, **kwargs)
