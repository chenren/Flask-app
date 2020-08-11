import os

from flask_migrate import Migrate, upgrade
from app import create_app, db
from app.models import Role, User

# app = create_app(os.getenv('FLASK_CONFIG') or 'default')
app = create_app('development')
migrate = Migrate(app, db)
app.app_context().push()


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@app.cli.command()
def deploy():
    """Run deployment task"""
    upgrade()
    Role.insert_roles()


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


if __name__ == '__main__':
    # db.drop_all()
    # db.create_all()
    # admin_role = Role(name='Admin')
    # user_me = User(email='chenren_w@163.com', username='chenren', role=admin_role)
    # db.session.add(admin_role)
    # db.session.add(user_me)
    # db.session.commit()

    app.run(port='8888', debug=True)
