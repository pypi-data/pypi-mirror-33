import enum as _enum
import pathlib
from typing import Type

import click


class Enum(click.Choice):
    """
    Enum support for click.

    Use it as a collection: @click.option(..., type=cli.Enum(MyEnum)).
    Then, this expects you to pass the *name* of a member of the enum.

    From `this github issue <https://github.com/pallets/click/issues/
    605#issuecomment-277539425>`_.
    """

    def __init__(self, enum: Type[_enum.Enum]):
        self.__enum = enum
        super().__init__(enum.__members__)

    def convert(self, value, param, ctx):
        return self.__enum[super().convert(value, param, ctx)]


class Path(click.Path):
    """Like click.Path but returning ``pathlib.Path`` objects."""

    def convert(self, value, param, ctx):
        return pathlib.Path(super().convert(value, param, ctx))
