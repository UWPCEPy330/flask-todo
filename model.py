import os
import datetime

from peewee import Model, CharField, DateTimeField, ForeignKeyField
from playhouse.db_url import connect

db = connect(os.environ.get('DATABASE_URL', 'sqlite:///mydatabase.db'))


class User(Model):
    name = CharField(max_length=255, unique=True)
    password = CharField(max_length=255)

    class Meta:
        database = db

class Task(Model):
    name = CharField(max_length=255)
    performed_by = ForeignKeyField(model=User, null=True)
    performed = DateTimeField(null=True)

    class Meta:
        database = db