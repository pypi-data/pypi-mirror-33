# Mongo Migrations Management Tool

## About

The applicaiton allows to create, execute and rollback migrations for MongoDB.
The migration files stored in `<init_directory>/migrations` directory.
Each file contains up and down python methods.
After execution the record about migration is added to `migrations` mongo collection.
The project is based on https://bitbucket.org/letsignitcloud/flask-mongoengine-migrations, but with many differeces:

* remove dependence from structlog
* remove dependence from flask
* added init command like alembic
* removed dependence from mongoengine and move on pymongo
* backported on python 2.7
* down to last migration_id if not specify it
* introduce env.py like alembic. 
* fake registration on db
* added up/down registration, for have complete history
* added checksum for migration file, calculated, added or updated for every run of up and down commands

The original author is Andrey Zhukov, while this is modified version by Massimo Cavalleri.

The collection migrations will be created automatically.
This is very important for understand the state of your database, following example can be useful:
    
    {
        "_id" : ObjectId("5b4b041ba17372661bb6017c"),
        "checksum" : "bb369cf68efbae886e1865a31a89d45ccfb49448a7d2625e901270631b5fc285",
        "filename" : "0001_prova.py",
        "fake" : false,
        "date" : ISODate("2018-07-15T08:21:47.940Z"),
        "type" : "up",
        "id" : 1
    }

## TODO:

* add parameters for db connection from command line
* add digits for choice number of digits id
* readd python3 support
* optimize code

## Usage
### Init migration directory on you project
    mongomigrations init
Now you must edit env.py inside directory and define get_db().
The get_db defined here can return uri or database object.

### Create migration
    mongomigrations create <name>
Creates migration file `<id>_<name>.py` with empty up and down methods.

### Show status
    mongomigrations status
Show migrations available for execution.

### Run migration
    mongomigrations up
    
#### To specific migration
    mongomigrations up <migration_id>

#### Register migration, but skip execution
    mongomigrations up --fake

### Rollback migration
    mongomigrations down <migration_id>

## Test
    python setup.py test

## Examples

### Remove field

```
def up(db):
    db['some_collection'].update_many(
        {'some_field': {'$exists': True}},
        {'$unset': {'some_field': 1}}
    )
```
