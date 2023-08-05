
from asyncqlio import (
    Column,
    Integer,
    SmallInt,
    String,
    Text,
    Timestamp,
    Serial,
    Boolean,
    Numeric,
)

from .base import Table


class Pokemon(Table, table_name='pokemons'):
    id = Column(Serial, primary_key=True, unique=True)

    name = Column.with_name('identifier', String, nullable=False)
    species = Column.with_name('species_id', Integer, nullable=False)

    height = Column(SmallInt, nullable=False)
    weight = Column(SmallInt, nullable=False)

    base_xp = Column.with_name('base_experience', SmallInt, nullable=False)

    order = Column(SmallInt, nullable=False)

    primary_type = Column.with_name('type_1_id', SmallInt, nullable=False)
    secondary_type = Column.with_name('type_2_id', SmallInt, nullable=False)

    primary_type_text = Column.with_name('type_1', SmallInt, nullable=False)
    secondary_type_text = Column.with_name('type_2', SmallInt, nullable=False)

    description = Column(Text)


class PokemonType(Table, table_name='types'):
    id = Column(Serial, primary_key=True, unique=True)

    title = Column(String, nullable=False)

    bg_primary_color = Column.with_name('background_hex', String)
    bg_secondary_color = Column.with_name('background_hex_2', String)
    font_color = Column.with_name('font_hex', String)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)
