import enum
import functools
from typing import Any, Dict, Optional, Self, Tuple, Union

import attrs


class BrokenEnum(enum.Enum):

    # # Initialization

    @classmethod
    @functools.lru_cache()
    def from_name(cls, name: str, *, lowercase: bool=True) -> Optional[enum.Enum]:
        """
        Get enum members from their name (name=value)

        Example:
            ```python
            class Fruits(BrokenEnum):
                Apple  = "Maçã"
                Banana = "Banana"
                Orange = "Laranja"

            Fruits.from_name("Apple") # Fruits.Apple
            Fruits.from_name("apple") # Fruits.Apple
            ```

        Args:
            name: Name of the member to get
            lowercase: Whether to lowercase the name and key before matching

        Returns:
            The enum member with the given name if found, None otherwise
        """
        if not isinstance(name, str):
            raise TypeError(f"Expected str, got {type(name).__name__} on BrokenEnum.from_name()")

        # Optionally lowercase name for matching
        name = name.lower() if lowercase else name

        # Search for the member by key
        for key, value in cls._member_map_.items():
            if (key.lower() if lowercase else key) == name:
                return value

    @classmethod
    @functools.lru_cache()
    def from_value(cls, value: Any) -> Optional[enum.Enum]:
        """
        Get enum members from their value (name=value)

        Example:
            ```python
            class Fruits(BrokenEnum):
                Apple  = "Maçã"
                Banana = "Banana"
                Orange = "Laranja"

            Fruits.from_value("Maçã")   # Fruits.Apple
            Fruits.from_value("Banana") # Fruits.Banana
            ```

        Args:
            value: Value of the member to get

        Returns:
            The enum member with the given value if found, None otherwise
        """
        # Scroll through all members, match by value
        for option in cls:
            if value == option.value:
                return option

    # # Utilities properties

    # Values

    @classmethod
    def members(cls) -> Tuple[enum.Enum]:
        """
        Get all members of the enum

        Example:
            ```python
            class Fruits(BrokenEnum):
                Apple  = "Maçã"
                Banana = "Banana"
                Orange = "Laranja"

            # (Fruits.Apple, Fruits.Banana, Fruits.Orange)
            Fruits.members()
            ```
        """
        return tuple(cls)

    @classmethod
    def options(cls) -> Tuple[enum.Enum]:
        """
        Get all members of the enum

        Example:
            ```python
            class Fruits(BrokenEnum):
                Apple  = "Maçã"
                Banana = "Banana"
                Orange = "Laranja"

            # (Fruits.Apple, Fruits.Banana, Fruits.Orange)
            Fruits.options()
            ```
        """
        return cls.members()

    @classmethod
    def values(cls) -> Tuple[Any]:
        """
        Get all values of the enum (name=value)

        Example:
            ```python
            class Fruits(BrokenEnum):
                Apple  = "Maçã"
                Banana = "Banana"
                Orange = "Laranja"

            # ("Maçã", "Banana", "Laranja")
            Fruits.values()
            ```
        """
        return tuple(member.value for member in cls)

    # Key/names properties

    @classmethod
    def keys(cls) -> Tuple[str]:
        """
        Get all 'keys' of the enum (key=value)

        Example:
            ```python
            class Fruits(BrokenEnum):
                Apple  = "Maçã"
                Banana = "Banana"
                Orange = "Laranja"

            # ("Apple", "Banana", "Orange")
            Fruits.keys()
            ```
        """
        return tuple(member.name for member in cls)

    # Items and dict-like

    @classmethod
    def items(cls) -> Tuple[Tuple[str, Any]]:
        """
        Get the tuple of (name, value) of all members of the enum

        Example:
            ```python
            class Fruits(BrokenEnum):
                Apple  = "Maçã"
                Banana = "Banana"
                Orange = "Laranja"

            # (("Apple", "Maçã"), ("Banana", "Banana"), ("Orange", "Laranja"))
            Fruits.items()
            ```
        """
        return tuple((member.name, member.value) for member in cls)

    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        """
        Get the dictionary of key: value of all members of the enum

        Example:
            ```python
            class Fruits(BrokenEnum):
                Apple  = "Maçã"
                Banana = "Banana"
                Orange = "Laranja"

            # {"Apple": "Maçã", "Banana": "Banana", "Orange": "Laranja"}
            Fruits.as_dict()
            ```
        """
        return dict(cls.items())

    def __getitem__(self, index: int) -> enum.Enum:
        return self.members[index]

    @classmethod
    def first(cls) -> enum.Enum:
        return cls.members()[0]

    # # Smart methods

    @classmethod
    @functools.lru_cache()
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
            Multivalue.get("blue")   # Multivalue.Color
            Multivalue.get(False)    # Multivalue.Hat
            Multivalue.get("Height") # Multivalue.Height
            Multivalue.get("height") # Multivalue.Height

            # Use from a member itself
            Multivalue.get(Multivalue.Color) # Multivalue.Color
            ```

        Args:
            value: Value to get the enum member from, can be the member's name or value

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

    @functools.lru_cache()
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
            Platform.next("linux")   # Platform.Windows
            Platform.next("windows") # Platform.MacOS
            Platform.next("macos")   # Platform.Linux
            (...)
            ```

        Args:
            value: Value to get the next enum member from, can be the Option's name or value

        Returns:
            The next enum member (in position) from the given value
        """
        cls   = type(self)
        value = cls.get(value or self)
        return cls.options()[(cls.options().index(value) + offset) % len(cls)]

    def __next__(self) -> Self:
        return self.next()

    @functools.lru_cache()
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
            Platform.previous("linux")   # Platform.MacOS
            Platform.previous("windows") # Platform.Linux
            Platform.previous("macos")   # Platform.Windows
            (...)
            ```

        Args:
            value: Value to get the previous enum member from, can be the Option's name or value

        Returns:
            The previous enum member (in position) from the given value
        """
        cls   = type(self)
        value = cls.get(value or self)
        return cls.options()[(cls.options().index(value) - offset) % len(cls)]

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
            name:  Name of the new member
            value: Value of the new member

        Returns:
            Fluent interface, the class that was extended
        """
        raise NotImplementedError("This method is not implemented yet")

    def field(self, **kwargs: Dict[str, Any]) -> attrs.Attribute:
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
            kwargs: Keyword arguments to pass to the field, may override default and converter
        """
        return attrs.field(default=self, converter=self.__class__.get, **kwargs)

# ------------------------------------------------------------------------------------------------ #
# Test

class _PyTest:

    # # Basic usage

    def get_fruits(self) -> BrokenEnum:
        # A translation enum example
        class Fruits(BrokenEnum):
            Apple  = "Maçã"
            Banana = "Banana"
            Orange = "Laranja"
        return Fruits

    # Test inheritance
    def test_inheritance(self):
        self.get_fruits()
        assert True

    # Test initialization
    def test_initialization(self):
        Fruits = self.get_fruits()
        assert Fruits("Maçã") == Fruits.Apple

    # Test .from_name
    def test_from_name(self):
        Fruits = self.get_fruits()
        assert Fruits.from_name("Apple")  == Fruits.Apple
        assert Fruits.from_name("apple")  == Fruits.Apple
        assert Fruits.from_name("Maçã")   is None

    # Test .options property
    def test_options(self):
        Fruits = self.get_fruits()
        assert Fruits.options() == (Fruits.Apple, Fruits.Banana, Fruits.Orange)

    # Test .values property
    def test_values(self):
        Fruits = self.get_fruits()
        assert Fruits.values() == ("Maçã", "Banana", "Laranja")

    # Test .keys property
    def test_keys(self):
        Fruits = self.get_fruits()
        assert Fruits.keys() == ("Apple", "Banana", "Orange")

    # Test .names property
    def test_names(self):
        Fruits = self.get_fruits()
        assert Fruits.keys() == ("Apple", "Banana", "Orange")

    # Test .items
    def test_items(self):
        Fruits = self.get_fruits()
        assert Fruits.items() == (
            ("Apple", Fruits.Apple.value),
            ("Banana", Fruits.Banana.value),
            ("Orange", Fruits.Orange.value),
        )

    # Test .as_dict
    def test_as_dict(self):
        Fruits = self.get_fruits()
        assert Fruits.as_dict() == dict(
            Apple="Maçã",
            Banana="Banana",
            Orange="Laranja",
        )

    # # Advanced usage

    def get_multivalue(self) -> BrokenEnum:
        # This is a bad example of usage
        # - Multi options with False will collide
        class Multivalue(BrokenEnum):
            Color  = "blue"
            Hat    = False
            Age    = 9000
            Height = 1.41
            Emoji  = "🔱"
        return Multivalue

    # Test .from_value
    def test_from_value(self):
        Multivalue = self.get_multivalue()
        assert Multivalue.from_value("blue")  == Multivalue.Color
        assert Multivalue.from_value(False)   == Multivalue.Hat
        assert Multivalue.from_value(9000)    == Multivalue.Age
        assert Multivalue.from_value(1.41)    == Multivalue.Height
        assert Multivalue.from_value("🔱")    == Multivalue.Emoji
        assert Multivalue.from_value("color") is None

    # Test .get
    def test_get(self):
        Multivalue = self.get_multivalue()
        assert Multivalue.get("blue")           == Multivalue.Color
        assert Multivalue.get(Multivalue.Color) == Multivalue.Color
        assert Multivalue.get("height")         == Multivalue.Height
        assert Multivalue.get("Height")         == Multivalue.Height
        assert Multivalue.get(9000)             == Multivalue.Age

    # Test .next
    def test_next_previous(self):
        Multivalue = self.get_multivalue()

        # Cycling through options with .next
        value = Multivalue.Color
        assert (value := value.next()) == Multivalue.Hat
        assert (value := value.next()) == Multivalue.Age
        assert (value := value.next()) == Multivalue.Height
        assert (value := value.next()) == Multivalue.Emoji
        assert (value := value.next()) == Multivalue.Color

        # Cycling through options with .previous
        value = Multivalue.Color
        assert (value := value.previous()) == Multivalue.Emoji
        assert (value := value.previous()) == Multivalue.Height
        assert (value := value.previous()) == Multivalue.Age
        assert (value := value.previous()) == Multivalue.Hat
        assert (value := value.previous()) == Multivalue.Color
