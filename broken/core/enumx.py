import contextlib
import enum
import functools
from typing import Any, Optional, Self, Union

import attrs
from aenum import MultiValueEnum


class BrokenEnumBase:

    @classmethod
    @functools.cache
    def get(cls,
        value: Union[str, enum.Enum, Any],
        default: Any=None
    ) -> Optional[Self]:
        """Get enum members from their value, name or themselves"""

        # Value is already a member of the enum
        if isinstance(value, cls):
            return value

        # Attempt to get by value
        with contextlib.suppress(ValueError):
            return cls(value)

        # Attempt to get by key
        with contextlib.suppress(KeyError):
            return cls[value]

        return default

    # Values

    @classmethod
    def options(cls) -> tuple[enum.Enum]:
        """Get all options (Class.A, Class.B, ...) of the enum"""
        return tuple(cls)

    @classmethod
    def values(cls) -> tuple[Any]:
        """Get all 'values' of the enum (name=value)"""
        return tuple(member.value for member in cls)

    # Dict-like

    @classmethod
    def keys(cls) -> tuple[str]:
        """Get all 'keys' of the enum (key=value)"""
        return tuple(member.name for member in cls)

    @classmethod
    def items(cls) -> tuple[tuple[str, Any]]:
        """Get the tuple of (name, value) of all members of the enum"""
        return tuple((member.name, member.value) for member in cls)

    def __getitem__(self, index: int) -> enum.Enum:
        return self.members[index]

    @classmethod
    def as_dict(cls) -> dict[str, Any]:
        """Get the dictionary of all key=value of the enum"""
        return dict(cls.items())

    # # Smart methods

    @functools.cache
    def next(self, value: Union[str, enum.Enum]=None, *, offset: int=1) -> Self:
        """Get the next enum member defined in the class"""
        cls   = type(self)
        value = cls.get(value or self)
        return cls.options()[(cls.options().index(value) + offset) % len(cls)]

    def __next__(self) -> Self:
        return self.next()

    @functools.cache
    def previous(self, value: Union[str, enum.Enum]=None, *, offset: int=1) -> Self:
        """Get the previous enum member defined in the class"""
        cls   = type(self)
        value = cls.get(value or self)
        return cls.options()[(cls.options().index(value) - offset) % len(cls)]

    # # Advanced functions

    def field(self, **kwargs: dict[str, Any]) -> attrs.Attribute:
        """Get an attrs.field() with this option as default and Enum.get as converter"""
        return attrs.field(
            default=self,
            converter=type(self).get,
            **kwargs
        )

    @classmethod
    def extend(cls, name: str, value: Any) -> Self:
        """Dynamically extend the enum with a new member (name=value)"""
        raise NotImplementedError("This method is not implemented yet")

class BrokenEnum(BrokenEnumBase, enum.Enum):
    ...

class MultiEnum(BrokenEnumBase, MultiValueEnum):
    ...

# ------------------------------------------------------------------------------------------------ #

class __PyTest__:

    def get_fruits(self) -> BrokenEnum:
        class Fruits(BrokenEnum):
            Apple  = "Maçã"
            Banana = "Banana"
            Orange = "Laranja"
        return Fruits

    # # Basic usage

    def test_initialization(self):
        Fruits = self.get_fruits()
        assert Fruits("Maçã") == Fruits.Apple

    def test_options(self):
        Fruits = self.get_fruits()
        assert Fruits.options() == (Fruits.Apple, Fruits.Banana, Fruits.Orange)

    def test_values(self):
        Fruits = self.get_fruits()
        assert Fruits.values() == ("Maçã", "Banana", "Laranja")

    def test_keys(self):
        Fruits = self.get_fruits()
        assert Fruits.keys() == ("Apple", "Banana", "Orange")

    def test_names(self):
        Fruits = self.get_fruits()
        assert Fruits.keys() == ("Apple", "Banana", "Orange")

    def test_items(self):
        Fruits = self.get_fruits()
        assert Fruits.items() == (
            ("Apple", Fruits.Apple.value),
            ("Banana", Fruits.Banana.value),
            ("Orange", Fruits.Orange.value),
        )

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

    def test_get(self):
        Multivalue = self.get_multivalue()
        assert Multivalue.get("blue")           == Multivalue.Color
        assert Multivalue.get(Multivalue.Color) == Multivalue.Color
        assert Multivalue.get("Height")         == Multivalue.Height
        assert Multivalue.get(9000)             == Multivalue.Age

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
