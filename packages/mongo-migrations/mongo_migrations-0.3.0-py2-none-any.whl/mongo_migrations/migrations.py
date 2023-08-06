from __future__ import print_function

import hashlib
import logging
import os
import re
from datetime import datetime
import imp

logger = logging.getLogger(__name__)


class MigrationFile(object):
    PATTERN = '^(?P<id>[0-9]+)_[a-z0-9_]+\.py$'

    def __init__(self, id, filename):
        self.id = int(id)
        self.filename = filename

    def __str__(self):
        return '{0.id}: {0.filename}'.format(self)

    def __eq__(self, other):
        return self.id == other.id and self.filename == other.filename

    @staticmethod
    def normalize_name(name):
        return re.sub('[^a-z0-9_]', '_', name)

    @staticmethod
    def validate_id(migration_id):
        try:
            return int(migration_id)
        except ValueError:
            logger.error('Invalid migration_id %d', migration_id)

    def as_dict(self):
        return {
            'id': self.id,
            'filename': self.filename
        }


class Migrations(object):
    """Manage MongoDB migrations."""

    MIGRATIONS_COLLECTION = 'migrations'
    MIGRATIONS_DIRECTORY = 'migrations'
    NO_MIGRATIONS_MSG = 'All migrations registered, nothing to execute'

    def __init__(self, path, db):
        self.path = path
        self.db = db

        self.directory = os.path.join(path, self.MIGRATIONS_DIRECTORY)
        self.collection = self.db[self.MIGRATIONS_COLLECTION]

    def get_migration_files(self):
        """Find migrations files."""
        migrations = (re.match(MigrationFile.PATTERN, filename) for filename in os.listdir(self.directory))
        migrations = (MigrationFile(m.group('id'), m.group(0)) for m in migrations if m)
        return sorted(migrations, key=lambda m: m.id)

    def get_unregistered_migrations(self):
        """Find unregistered migrations."""

        def is_registered(migration):
            m_state = next(self.collection.find({'filename': migration.filename}).sort('_id', -1).limit(1), None)
            return m_state and m_state['type'] == 'up'

        unregistered = [m for m in self.get_migration_files() if not is_registered(m)]

        logger.debug('migration_files: %s', [m.filename for m in self.get_migration_files()])
        logger.debug('unregistered_migrations: %s', [m.filename for m in unregistered])

        return unregistered

    def check_directory(self):
        """Check if migrations directory exists."""
        exists = os.path.exists(self.directory)
        if not exists:
            logger.error("No migrations directory, %s", self.directory)
        return exists

    def show_status(self):
        """Show status of unregistered migrations"""
        if not self.check_directory():
            return

        last_migration_id = self.get_last_migrated_id()
        print('Last registered migration id: %s' % last_migration_id)

        migrations = self.get_unregistered_migrations()
        if migrations:
            logger.info('Unregistered migrations:')
            print('Unregistered migrations:')
            for migration in migrations:
                logger.info('migration file %s', migration.filename)
                print('migration file %s' % migration.filename)
        else:
            logger.info(self.NO_MIGRATIONS_MSG)
            print(self.NO_MIGRATIONS_MSG)

    def get_new_filename(self, name):
        """Generate filename for new migration."""
        name = MigrationFile.normalize_name(name)
        migrations = self.get_migration_files()
        migration_id = migrations[-1].id if migrations else 0
        migration_id += 1
        return '{:04}_{}.py'.format(migration_id, name)

    def create(self, name):
        """Create a new empty migration."""
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        filename = self.get_new_filename(name)
        with open(os.path.join(self.directory, filename), 'w') as fp:
            fp.write("def up(db): pass\n\n\n")
            fp.write("def down(db): pass\n")
            logger.info('migration file created: %s', filename)
            print('migration file created: %s' % filename)

    def load_migration_file(self, filename):
        """Load migration file as module."""
        path = os.path.join(self.directory, filename)
        module = imp.load_source("migration", path)
        return module

    def get_migrations_to_up(self, migration_id=None):
        """Find migrations to execute."""
        if migration_id is not None:
            migration_id = MigrationFile.validate_id(migration_id)
            if not migration_id:
                return []

        migrations = self.get_unregistered_migrations()
        if not migrations:
            logger.info(self.NO_MIGRATIONS_MSG)
            return []

        if migration_id:
            try:
                last_migration = [m for m in migrations if m.id == migration_id][0]
            except IndexError:
                logger.error('Migration is not in unregistered list, id: %d', migration_id)
                self.show_status()
                return []
        else:
            last_migration = list(migrations)[-1]

        return [m for m in migrations if m.id <= last_migration.id]

    @staticmethod
    def checksum(filename):
        with open(filename, 'rw+') as fm:
            content_orig = fm.read()
            p_find_checksum = re.compile("checksum[ \t]*\=[ \t]*['\"]{1}(.*)['\"]{1}")
            checksum_old = p_find_checksum.match(content_orig).group(1) if p_find_checksum.match(content_orig) else None
            content = re.sub('checksum[ \t]*\=[ \t]*.*', '', content_orig).lstrip()
            logger.debug('content: %s', content)
            checksum_new = hashlib.sha256(content).hexdigest()
            logger.debug('checksum_old: %s, checksum_new: %s', checksum_old, checksum_new)
            if not checksum_old:
                fm.seek(0, 0)
                fm.truncate()
                fm.write("checksum = '%s'\n\n%s" % (checksum_new, content))
            elif checksum_old and checksum_new != checksum_old:
                fm.seek(0, 0)
                fm.truncate()
                fm.write(re.sub(checksum_old, checksum_new, content_orig))

    def up(self, migration_id=None, fake=False):
        """Executes migrations."""
        if not self.check_directory():
            return

        for migration in self.get_migrations_to_up(migration_id):
            logger.info('Executing migration...')
            print('Executing migration %s...' % migration.filename, end='')

            if not fake:
                self.checksum(os.path.join(self.directory, migration.filename))

            migration_module = self.load_migration_file(migration.filename)

            if hasattr(migration_module, 'up'):
                record = migration.as_dict()
                if not fake:
                    migration_module.up(self.db)
                    record['checksum'] = migration_module.checksum
                record['date'] = datetime.utcnow()
                record['fake'] = fake
                record['type'] = 'up'
                self.collection.insert(record)
            else:
                logger.error('No up method')
                print('no up method found')

            print('OK')

        print('done')

    def get_last_migrated_id(self):
        """Find id of last applied migration."""
        migration = next(self.collection.aggregate([
            {'$group': {'_id': "$filename", 'last': {'$last': "$$ROOT"}}},
            {'$sort': {'_id': -1}},
            {"$match": {"last.type": "up"}},
            {'$limit': 1}
        ]), None)
        return migration['last']['id'] if migration else None

    def get_migrations_to_down(self, migration_id=None):
        """Find migrations to rollback."""
        migrations = self.get_migration_files()
        last_migration_id = self.get_last_migrated_id()

        if migration_id:
            migration_id = MigrationFile.validate_id(migration_id)
            if not migration_id:
                return []

            if migration_id in (m.id for m in self.get_unregistered_migrations()):
                logger.error('Migration is not applied, id: %d', migration_id)
                return []

            try:
                migration = [m for m in migrations if m.id == migration_id][0]
            except IndexError:
                logger.error('Migration does not exists, id: %d', migration_id)
                return []
        elif last_migration_id:
            try:
                migration = [m for m in migrations if m.id == last_migration_id][0]
            except IndexError:
                logger.error('Migration does not exists, id: %d', last_migration_id)
                return []
        else:
            return []

        return list(reversed([m for m in migrations
                              if migration.id <= m.id <= last_migration_id]))

    def down(self, migration_id=None):
        """Rollback to migration."""
        if not self.check_directory():
            return

        migrations_to_down = self.get_migrations_to_down(migration_id)
        if not migrations_to_down:
            print('None migrations to downgrade')

        for migration in migrations_to_down:
            logger.info('Rollback migration...')
            print('Rollback migration %s...' % migration.filename, end='')

            migration_db = self.collection.find({'filename': migration.filename, 'type': 'up'}).sort('_id', -1).limit(1)[0]

            if not migration_db.get('fake'):
                self.checksum(os.path.join(self.directory, migration.filename))

            migration_module = self.load_migration_file(migration.filename)
            if hasattr(migration_module, 'down'):
                record = migration.as_dict()
                if not migration_db.get('fake'):
                    migration_module.down(self.db)
                    record['fake'] = False
                    record['checksum'] = migration_module.checksum
                else:
                    record['fake'] = True
                record['date'] = datetime.utcnow()
                record['type'] = 'down'
                self.collection.insert(record)
            else:
                logger.info('No down method')
                print('no down method found')

            print('OK')

        print('done')
