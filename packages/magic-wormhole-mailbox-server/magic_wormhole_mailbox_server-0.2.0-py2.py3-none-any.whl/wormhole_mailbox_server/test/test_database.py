from __future__ import print_function, unicode_literals
import os
from twisted.python import filepath
from twisted.trial import unittest
from .. import database
from ..database import _get_db, TARGET_VERSION, dump_db, DBError

class Get(unittest.TestCase):
    def test_create_default(self):
        db_url = ":memory:"
        db = _get_db(db_url, "channel")
        rows = db.execute("SELECT * FROM version").fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["version"], TARGET_VERSION)

    def test_open_existing_file(self):
        basedir = self.mktemp()
        os.mkdir(basedir)
        fn = os.path.join(basedir, "normal.db")
        db = _get_db(fn, "channel")
        rows = db.execute("SELECT * FROM version").fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["version"], TARGET_VERSION)
        db2 = _get_db(fn, "channel")
        rows = db2.execute("SELECT * FROM version").fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["version"], TARGET_VERSION)

    def test_open_bad_version(self):
        basedir = self.mktemp()
        os.mkdir(basedir)
        fn = os.path.join(basedir, "old.db")
        db = _get_db(fn, "channel")
        db.execute("UPDATE version SET version=999")
        db.commit()

        with self.assertRaises(DBError) as e:
            _get_db(fn, "channel")
        self.assertIn("Unable to handle db version 999", str(e.exception))

    def test_open_corrupt(self):
        basedir = self.mktemp()
        os.mkdir(basedir)
        fn = os.path.join(basedir, "corrupt.db")
        with open(fn, "wb") as f:
            f.write(b"I am not a database")
        with self.assertRaises(DBError) as e:
            _get_db(fn, "channel")
        self.assertIn("not a database", str(e.exception))

    def test_failed_create_allows_subsequent_create(self):
        patch = self.patch(database, "get_schema", lambda version: b"this is a broken schema")
        dbfile = filepath.FilePath(self.mktemp())
        self.assertRaises(Exception, lambda: _get_db(dbfile.path))
        patch.restore()
        _get_db(dbfile.path, "channel")

    def OFF_test_upgrade(self): # disabled until we add a v2 schema
        basedir = self.mktemp()
        os.mkdir(basedir)
        fn = os.path.join(basedir, "upgrade.db")
        self.assertNotEqual(TARGET_VERSION, 2)

        # create an old-version DB in a file
        db = _get_db(fn, "channel", 2)
        rows = db.execute("SELECT * FROM version").fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["version"], 2)
        del db

        # then upgrade the file to the latest version
        dbA = _get_db(fn, "channel", TARGET_VERSION)
        rows = dbA.execute("SELECT * FROM version").fetchall()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["version"], TARGET_VERSION)
        dbA_text = dump_db(dbA)
        del dbA

        # make sure the upgrades got committed to disk
        dbB = _get_db(fn, "channel", TARGET_VERSION)
        dbB_text = dump_db(dbB)
        del dbB
        self.assertEqual(dbA_text, dbB_text)

        # The upgraded schema should be equivalent to that of a new DB.
        # However a text dump will differ because ALTER TABLE always appends
        # the new column to the end of a table, whereas our schema puts it
        # somewhere in the middle (wherever it fits naturally). Also ALTER
        # TABLE doesn't include comments.
        if False:
            latest_db = _get_db(":memory:", "channel", TARGET_VERSION)
            latest_text = dump_db(latest_db)
            with open("up.sql","w") as f: f.write(dbA_text)
            with open("new.sql","w") as f: f.write(latest_text)
            # check with "diff -u _trial_temp/up.sql _trial_temp/new.sql"
            self.assertEqual(dbA_text, latest_text)

class CreateChannel(unittest.TestCase):
    def test_memory(self):
        db = database.create_channel_db(":memory:")
        latest_text = dump_db(db)
        self.assertIn("CREATE TABLE", latest_text)

    def test_preexisting(self):
        basedir = self.mktemp()
        os.mkdir(basedir)
        fn = os.path.join(basedir, "preexisting.db")
        with open(fn, "w"):
            pass
        with self.assertRaises(database.DBAlreadyExists):
            database.create_channel_db(fn)

    def test_create(self):
        basedir = self.mktemp()
        os.mkdir(basedir)
        fn = os.path.join(basedir, "created.db")
        db = database.create_channel_db(fn)
        latest_text = dump_db(db)
        self.assertIn("CREATE TABLE", latest_text)

    def test_create_or_upgrade(self):
        basedir = self.mktemp()
        os.mkdir(basedir)
        fn = os.path.join(basedir, "created.db")
        db = database.create_or_upgrade_channel_db(fn)
        latest_text = dump_db(db)
        self.assertIn("CREATE TABLE", latest_text)

class CreateUsage(unittest.TestCase):
    def test_memory(self):
        db = database.create_usage_db(":memory:")
        latest_text = dump_db(db)
        self.assertIn("CREATE TABLE", latest_text)

    def test_preexisting(self):
        basedir = self.mktemp()
        os.mkdir(basedir)
        fn = os.path.join(basedir, "preexisting.db")
        with open(fn, "w"):
            pass
        with self.assertRaises(database.DBAlreadyExists):
            database.create_usage_db(fn)

    def test_create(self):
        basedir = self.mktemp()
        os.mkdir(basedir)
        fn = os.path.join(basedir, "created.db")
        db = database.create_usage_db(fn)
        latest_text = dump_db(db)
        self.assertIn("CREATE TABLE", latest_text)

    def test_create_or_upgrade(self):
        basedir = self.mktemp()
        os.mkdir(basedir)
        fn = os.path.join(basedir, "created.db")
        db = database.create_or_upgrade_usage_db(fn)
        latest_text = dump_db(db)
        self.assertIn("CREATE TABLE", latest_text)

    def test_create_or_upgrade_disabled(self):
        db = database.create_or_upgrade_usage_db(None)
        self.assertIs(db, None)

class OpenChannel(unittest.TestCase):
    def test_open(self):
        basedir = self.mktemp()
        os.mkdir(basedir)
        fn = os.path.join(basedir, "created.db")
        db1 = database.create_channel_db(fn)
        latest_text = dump_db(db1)
        self.assertIn("CREATE TABLE", latest_text)
        db2 = database.open_existing_db(fn)
        self.assertIn("CREATE TABLE", dump_db(db2))

    def test_doesnt_exist(self):
        basedir = self.mktemp()
        os.mkdir(basedir)
        fn = os.path.join(basedir, "created.db")
        with self.assertRaises(database.DBDoesntExist):
            database.open_existing_db(fn)

class OpenUsage(unittest.TestCase):
    def test_open(self):
        basedir = self.mktemp()
        os.mkdir(basedir)
        fn = os.path.join(basedir, "created.db")
        db1 = database.create_usage_db(fn)
        latest_text = dump_db(db1)
        self.assertIn("CREATE TABLE", latest_text)
        db2 = database.open_existing_db(fn)
        self.assertIn("CREATE TABLE", dump_db(db2))

    def test_doesnt_exist(self):
        basedir = self.mktemp()
        os.mkdir(basedir)
        fn = os.path.join(basedir, "created.db")
        with self.assertRaises(database.DBDoesntExist):
            database.open_existing_db(fn)


