from Broken import *

# -------------------------------------------------------------------------------------------------|
# Basic usage

def get_fruits():
    # A translation enum example
    class Fruits(BrokenEnum):
        Apple  = "Maçã"
        Banana = "Banana"
        Orange = "Laranja"
    return Fruits

# Test inheritance
def test_inheritance():
    get_fruits()
    assert True

# Test initialization
def test_initialization():
    Fruits = get_fruits()
    assert Fruits("Maçã") == Fruits.Apple

# Test .from_name
def test_from_name():
    Fruits = get_fruits()
    assert Fruits.from_name("Apple")  == Fruits.Apple
    assert Fruits.from_name("apple")  == Fruits.Apple
    assert Fruits.from_name("Maçã")   == None

# Test .options property
def test_options():
    Fruits = get_fruits()
    assert Fruits.options == (Fruits.Apple, Fruits.Banana, Fruits.Orange)

# Test .values property
def test_values():
    Fruits = get_fruits()
    assert Fruits.values == ("Maçã", "Banana", "Laranja")

# Test .keys property
def test_keys():
    Fruits = get_fruits()
    assert Fruits.keys == ("Apple", "Banana", "Orange")

# Test .names property
def test_names():
    Fruits = get_fruits()
    assert Fruits.names == ("Apple", "Banana", "Orange")

# Test .names_lower property
def test_names_lower():
    Fruits = get_fruits()
    assert Fruits.names_lower == ("apple", "banana", "orange")

# Test .items
def test_items():
    Fruits = get_fruits()
    assert Fruits.items == (
        ("Apple", Fruits.Apple.value),
        ("Banana", Fruits.Banana.value),
        ("Orange", Fruits.Orange.value),
    )

# Test .as_dict
def test_as_dict():
    Fruits = get_fruits()
    assert Fruits.as_dict == dict(
        Apple="Maçã",
        Banana="Banana",
        Orange="Laranja",
    )

# -------------------------------------------------------------------------------------------------|
# Advanced usage

def get_multivalue():
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
def test_from_value():
    Multivalue = get_multivalue()
    assert Multivalue.from_value("blue")  == Multivalue.Color
    assert Multivalue.from_value(False)   == Multivalue.Hat
    assert Multivalue.from_value(9000)    == Multivalue.Age
    assert Multivalue.from_value(1.41)    == Multivalue.Height
    assert Multivalue.from_value("🔱")    == Multivalue.Emoji
    assert Multivalue.from_value("color") == None

# Test .get
def test_get():
    Multivalue = get_multivalue()
    assert Multivalue.get("blue")           == Multivalue.Color
    assert Multivalue.get(Multivalue.Color) == Multivalue.Color
    assert Multivalue.get("height")         == Multivalue.Height
    assert Multivalue.get("Height")         == Multivalue.Height
    assert Multivalue.get(9000)             == Multivalue.Age

# Test .next
def test_next_previous():
    Multivalue = get_multivalue()

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
