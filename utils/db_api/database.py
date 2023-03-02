from peewee import *

db = SqliteDatabase('database.db', pragmas={'foreign_keys': 1})


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id = AutoField(primary_key=True, unique=True)
    name = CharField(null=False, unique=True)
    telegram_id = IntegerField()


    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.name

class Movie(BaseModel):
    id = AutoField(primary_key=True, unique=True)
    title = CharField(null=False, unique=True)
    url = CharField(null=False, unique=True)
    user = IntegerField()
    vote = IntegerField(default=0)

class Voting(BaseModel):
    id = AutoField(primary_key=True, unique=True)
    open = BooleanField()

def create_database():
    db.create_tables([User, Movie, Voting])



if __name__ == '__main__':
    create_database()
