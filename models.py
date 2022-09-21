from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    TextField,
    DoubleField,
    DateTimeField,
)
from datetime import datetime

sqlite_db = SqliteDatabase('my_app.db', pragmas={'journal_mode': 'wal'})


class BaseModel(Model):
    """A base model that will use our Sqlite database."""

    class Meta:
        database = sqlite_db


class Payment(BaseModel):
    currency = CharField(index=True)
    amount = DoubleField()
    sending_date = DateTimeField(default=datetime.now())
    comment = TextField(null=True)


def create_database():
    sqlite_db.connect()
    sqlite_db.create_tables([Payment])
    sqlite_db.close()
