#!/usr/bin/env python
import os
import app as linkitup
from app import app, db
from app.models import User
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

manager = Manager(app)


@manager.shell
def make_shell_context():
    return dict(app=app, db=db, User=User)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    # migrate database to latest revision
    upgrade()

# Setup migrate command
migrations_dir = os.path.join(os.path.dirname(linkitup.__file__), 'migrations')
migrate = Migrate(app, db, directory=migrations_dir)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
