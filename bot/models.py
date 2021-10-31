from peewee import *

db = SqliteDatabase('bot/db.db')



class Request(Model):
    id = PrimaryKeyField(unique=True)
    user_id = IntegerField()
    date = DateField()
    type = CharField()
    hotels = CharField()

    class Meta:
        database = db
        order_by = 'id'
        db_table = 'requests'
