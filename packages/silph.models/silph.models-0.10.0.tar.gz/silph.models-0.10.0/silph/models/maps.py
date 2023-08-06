
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


class Pip(Table, table_name='pips'):
    id = Column(Serial, primary_key=True, unique=True)

    user = Column.with_name('user_id', Integer, nullable=False)
    type = Column(SmallInt, nullable=False, default=0)

    active = Column(Boolean, nullable=False, default=False)

    latitude = Column(Numeric(8, 12), nullable=False)
    longitude = Column(Numeric(8, 12), nullable=False)

    icon = Column(String(150))
    image = Column(String(150))

    message = Column(Text)

    created = Column(Timestamp)
    updated = Column(Timestamp)
