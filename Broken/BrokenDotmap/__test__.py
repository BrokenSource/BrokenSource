from Broken import *


# Can we initialize the module?
def test_initialization():
    dotmap = BrokenDotmap()

# -------------------------------------------------------------------------------------------------|
# Basic dictionary usage

# Loading from dictionary
def test_loading_from_dict():
    data = dict(
        loglevel="info",
        name="BrokenSource",
        nested=dict(
            hello="world",
        )
    )
    dotmap = BrokenDotmap(data)
    assert dotmap.as_dict      == data
    assert dotmap.loglevel     == "info"
    assert dotmap.name         == "BrokenSource"
    assert dotmap.nested.hello == "world"

# Does basic assignment work?
def test_assignment():
    dotmap = BrokenDotmap()

    # __getattr__ test
    dotmap.nested = "value"
    assert dotmap.nested == "value"

    # __getitem__ test
    dotmap["other"] = 5
    assert dotmap.other == 5

# Does nesting dictionaries work
def test_nesting():
    dotmap = BrokenDotmap()

    # Must nest as new key was found
    dotmap.other
    assert isinstance(dotmap.other, BrokenDotmap)

    # __getattr__ test
    dotmap.other.nested = "value"
    assert dotmap.other.nested == "value"

    # __getitem__ test
    dotmap["other"]["nested"] = 5
    assert dotmap.other.nested == 5

# Dictionaires .keys, .items, .values
def test_dictionary_methods():
    dotmap = BrokenDotmap()
    dotmap.loglevel = 5
    dotmap.name = "value"
    dotmap.boolean = True

    # Dictionary keys
    assert dotmap.keys() == [
        "loglevel", "name", "boolean"
    ]

    # Dictionary values
    assert dotmap.values() == [
        5, "value", True
    ]

    # Dictionary items
    assert dotmap.items() == [
        ("loglevel", 5),
        ("name", "value"),
        ("boolean", True),
    ]

# Default values testing
def test_setdefault():
    dotmap = BrokenDotmap()

    # __getattr__ test
    dotmap.default("name", "original")
    assert dotmap.name == "original"

    # Must not change as already set
    dotmap.default("name", "changed")
    assert dotmap.name == "original"

    # Must change
    dotmap.name = "forced"
    assert dotmap.name == "forced"

def test_to_dict():
    dotmap = BrokenDotmap()
    dotmap.nested = "value"
    dotmap.other.name = 3

    # Runs and have output
    data = dotmap.to_dict()

    assert isinstance(data, dict)
    assert data["nested"] == "value"
    print(data)
    assert data["other"]["name"] == 3

# -------------------------------------------------------------------------------------------------|
# Loaders

IMAGE_URL = "https://w.wallhaven.cc/full/x6/wallhaven-x6wjkv.png"

def test_plain_usage():
    image = LoaderImage(IMAGE_URL).load()
    assert isinstance(image, PIL.Image.Image)

def test_loader_image_assign_hinted():
    dotmap = BrokenDotmap()
    dotmap.image_png = IMAGE_URL
    assert isinstance(dotmap.image_png, PIL.Image.Image)

def test_loader_image_assign_unhinted():
    dotmap = BrokenDotmap()
    dotmap.image = IMAGE_URL
    assert isinstance(dotmap.image, PIL.Image.Image)

def test_loader_image_call_hinted():
    dotmap = BrokenDotmap()
    image = dotmap.image_png(IMAGE_URL)
    assert isinstance(image, PIL.Image.Image)

def test_loader_image_call_unhinted():
    dotmap = BrokenDotmap()
    image = dotmap.image(IMAGE_URL)
    assert isinstance(image, PIL.Image.Image)

def test_loader_image_manual():
    dotmap = BrokenDotmap()
    dotmap.image = LoaderImage(IMAGE_URL)
    assert isinstance(dotmap.image, PIL.Image.Image)

# -------------------------------------------------------------------------------------------------|
# Syncing

def test_sync():
    assert True
