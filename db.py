
from peewee import *
from configparser import ConfigParser
import time
#import sqlite3
#import psycopg2


# Initialize config parser
# ConfigParser will use % as a reference to another variable in your config file.
# If your password contains %, then you need to tell config parser don't interpolate it.
cfg = ConfigParser(interpolation=None)
cfg.read('conf.ini')

# Read the settings from config file using dictionary like notation
db_conf = cfg['database']
db_name = db_conf['db_name']
db_port = db_conf['db_port']
db_host = db_conf['db_host']
user = db_conf['user']
passwd = db_conf['passwd']

# Initialize a MySQL database connection
# Check more examples from the documentation: http://docs.peewee-orm.com/en/latest/peewee/quickstart.html
myDB = MySQLDatabase(db_name, host=db_host, port=int(db_port), user=user, passwd=passwd, charset='utf8mb4')
myDB.connect()

# The best way to understand how the Model and field works in peewee is to read the documentation
# http://peewee.readthedocs.io/en/latest/peewee/models.html#models-and-fields

# Initialize a class for the Review table
class Review_summary(Model):
    skuId = TextField()
    design = TextField()
    feature = TextField()
    storage = TextField()
    display = TextField()
    batterylife = TextField()
    class Meta:
        database = myDB

class Review(Model):
    store = TextField()
    skuId = TextField()
    username = TextField()
    title = TextField()
    text = TextField()
    date_published = DateTimeField()
    rating = IntegerField()
    recommending = TextField()
    helpful = IntegerField()
    unhelpful = IntegerField()

    class Meta:
        database = myDB

class Product(Model):
    store = TextField()
    product_name = TextField()
    skuId = TextField()
    brand = TextField()
    price = FloatField()
    color = TextField()
    storage = TextField()
    spec_name = TextField()
    spec_value = TextField()
    
    class Meta:
        database = myDB

# http://peewee.readthedocs.io/en/latest/peewee/api.html#Model.create_table
# safe (bool) – If set to True, the create table query will include an IF NOT EXISTS clause.
with myDB:
    Review.create_table(safe=True)
    #time.sleep(2)
    Product.create_table(safe=True)
    Review_summary.create_table(safe = True)


