# Mongo Migrations Management Tool

## About

The applicaiton allows to create, execute and rollback migrations for MongoDB.
The migration files stored in `<init_directory>/migrations` directory.
Each file contains up and down python methods.
After execution the record about migration is added to `migrations` mongo collection.
The project is based on https://bitbucket.org/letsignitcloud/flask-mongoengine-migrations, but with many differeces:
1) remove dependence from structlog
2) remove dependence from flask
3) added init command like alembic
4) removed dependence from mongoengine and move on pymongo
5) backported on python 2.7
6) down to last migration_id if not specify it
7) introduce env.py like alembic. 

The original author is Andrey Zhukov, while this is modified version by Massimo Cavalleri.
## TODO:
1) add downgrade registration, for have complete history
2) add digits for choice number of digits id
3) add possibility to use uuid instead id
4) readd python3 support
5) optimize

## Usage
### Init migration directory on you project
    mongo-migrations init
Now you must edit env.py inside directory and define get_db().
The get_db defined here can return uri or database object.

### Create migration
    mongo-migrations create <name>
Creates migration file `<id>_<name>.py` with empty up and down methods.

### Show status
    mongo-migrations status
Show migrations available for execution.

### Run migration
    mongo-migrations up
    
#### To specific migration
    mongo-migrations up <migration_id>

#### Register migration, but skip execution
    mongo-migrations up --fake

### Rollback migration
    mongo-migrations down <migration_id>

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
