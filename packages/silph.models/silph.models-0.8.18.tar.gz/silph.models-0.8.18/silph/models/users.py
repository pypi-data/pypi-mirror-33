
from asyncqlio import (
    Column,
    Integer,
    SmallInt,
    BigInt,
    String,
    Text,
    Boolean,
    Timestamp,
    ForeignKey,
    Numeric,
    Serial,
)

from .base import Table


class Avatar(Table, table_name='avatars'):
    id = Column(Serial, primary_key=True, unique=True)

    title = Column(String, nullable=False)
    filename = Column(String, nullable=False)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class User(Table, table_name='users'):
    id = Column(Serial, primary_key=True, unique=True)

    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    silph_username = Column.with_name('username', String)
    reddit_username = Column(String)
    game_username = Column.with_name('in_game_username', String)

    ban_level = Column(Integer)

    role = Column(Integer)
    is_in_field_test = Column(Integer)

    created = Column(Timestamp)

    @property
    def name(self):
        return self.game_username or 'Traveler #%x' % self.id

    def payload(self):
        struct = {
            'id': self.id,
            'name': self.username,
            'role': self.role,
            'created': int(self.created.timestamp()),
            'version': 0,
        }

        return struct


class UserLogin(Table, table_name='user_logins'):
    id = Column(Serial, primary_key=True, unique=True)

    user = Column.with_name('user_id', Integer, nullable=False)
    vendor = Column.with_name('vendor_id', Integer, nullable=False)

    username = Column(Text)
    identifier = Column(String)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class UnlockedAvatar(Table, table_name='unlocked_user_avatars'):
    user = Column.with_name('user_id', Integer, primary_key=True)
    avatar = Column.with_name('avatar_id', Integer, primary_key=True)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class UserBadge(Table, table_name='user_badges'):
    user = Column.with_name('user_id', Integer, primary_key=True)
    badge = Column.with_name('badge_id', Integer, primary_key=True)

    count = Column(Integer, default=0)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)


class TravelersCard(Table, table_name='travelers_cards'):
    id = Column(Serial, primary_key=True, unique=True)

    user = Column.with_name('user_id', Integer, nullable=False)
    trainer_type = Column.with_name('trainer_type_id', Integer)

    avatar = Column.with_name('avatar_id', Integer)
    gender = Column(Integer)
    skintone = Column(Integer)

    @property
    def gender_code(self):
        return 'm' if self.gender == 0 else 'f'

    team = Column(SmallInt)
    xp = Column(Integer)
    top_pokemon = Column.with_name('top_6_pokemon', Text)

    home_region = Column(Text)
    pokedex = Column.with_name('pokedex_count', SmallInt)
    raid_average = Column(SmallInt)
    playstyle = Column(SmallInt)
    goal = Column.with_name('current_goal', SmallInt)

    public = Column.with_name('is_public', Boolean)
    badge_sort = Column(SmallInt)

    show_trainer_name = Column(Boolean)
    show_discords = Column(Boolean)
    show_reddit = Column(Boolean)

    created = Column(Timestamp)
    updated = Column.with_name('modified', Timestamp)

