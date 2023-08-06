import imp
import logging
import os
import sys
import pymongo
import click
from mongo_migrations.migrations import Migrations
from pymongo import MongoClient

log_file = '/tmp/mongomigrations.log'

logger = logging.getLogger(__name__)


template_env = """
from pymongo import MongoClient

def get_db():
    '''
    return get_database from MongoClient
    '''
    raise Exception('Undefined db, edit your env.py')
    # example1:
    # return MongoClient('mongodb://admin:manager@localhost:27017/admin')['vnapi_8000']
    # example2:
    # return 'mongodb://admin:manager@localhost:27017/admin'

"""

env_file = 'env.py'


def get_env():
    path = os.getcwd()
    env = os.path.join(path, 'env.py')
    try:
        env_module = imp.load_source('env', env)
        db = env_module.get_db()
        if isinstance(db, basestring):
            db = MongoClient(db).get_database()
        return path, db
    except pymongo.errors.PyMongoError:
        print('ERROR: connection to mongodb fail')
        logger.error('connection to mongodb fail')
        sys.exit(-1)
    except Exception:
        print('ERROR: env.py broken')
        logger.exception('connection fail')
        sys.exit(-1)


@click.group()
def mongo_migrations():
    pass


@mongo_migrations.command()
def init():
    path = os.getcwd()
    with open(os.path.join(path, env_file), 'w') as f:
        f.writelines(template_env)


@mongo_migrations.command()
def status():
    migrations = Migrations(*get_env())
    migrations.show_status()


@mongo_migrations.command()
@click.argument('name')
def create(name):
    migrations = Migrations(*get_env())
    migrations.create(name)


@mongo_migrations.command()
@click.argument('migration_id', required=False)
@click.option('--fake', is_flag=True)
def up(migration_id=None, fake=False):
    migrations = Migrations(*get_env())
    migrations.up(migration_id, fake)


@mongo_migrations.command()
@click.argument('migration_id', required=False)
def down(migration_id=None):
    migrations = Migrations(*get_env())
    migrations.down(migration_id)


def main():
    lformat = '%(asctime)s - %(processName)-20s - %(name)-20s [%(lineno)4d] - ' \
              '%(levelname)-6s - %(process)-6d - %(message)s'
    logging.basicConfig(filename=log_file, level=logging.DEBUG, format=lformat)
    mongo_migrations()


if __name__ == '__main__':
    main()
