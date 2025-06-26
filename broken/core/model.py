from typing import Any, Iterable, Self, Union

from pydantic import BaseModel, ConfigDict, Field


class BrokenModel(BaseModel):
    model_config = ConfigDict(
        use_attribute_docstrings=True,
    )

    def model_post_init(self, __context):
        for cls in reversed(type(self).mro()):
            if method := cls.__dict__.get("__post__"):
                method(self)

    def __post__(self) -> None:
        ...

    def __hash__(self) -> int:
        """Deterministic model hash, as hash() is random seeded"""
        import xxhash
        return xxhash.xxh3_64_intdigest(self.json(full=True))

    # Serialization

    def json(self, full: bool=True) -> str:
        return self.model_dump_json(
            exclude_defaults=(not full),
            exclude_none=False
        )

    def dict(self, full: bool=True) -> dict:
        return self.model_dump(
            exclude_defaults=(not full),
            exclude_none=False
        )

    def schema(self) -> dict:
        return self.model_json_schema()

    # Deserialization

    @classmethod
    def load(cls, data: Union[dict, str]) -> Self:
        if isinstance(data, dict):
            return cls.model_validate(data)
        elif isinstance(data, str):
            return cls.model_validate_json(data)
        elif isinstance(data, cls):
            return data
        raise ValueError(f"Can't load from value of type {type(data)}")

    def update(self, **data: Union[dict, str]) -> Self:
        for (key, value) in data.items():
            setattr(self, key, value)
        return self

    # Dict-like utilities

    def keys(self) -> Iterable[str]:
        yield from self.dict().keys()

    def values(self) -> Iterable[Any]:
        yield from self.dict().values()

    def items(self) -> Iterable[tuple[str, Any]]:
        yield from self.dict().items()

    # Special

    def reset(self) -> None:
        for key, value in type(self).model_fields.items():
            setattr(self, key, value.default)


class FrozenHash(BaseModel):
    hash: int = Field(0, exclude=True)

    def __hash__(self):
        self.hash = (self.hash or super().__hash__())
        return self.hash

