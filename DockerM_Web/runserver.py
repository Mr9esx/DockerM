# -*- coding:utf-8 -*-
import os
from app import create_app, db
from app.lib.dbModel import User
from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command("runserver", Server(host="0.0.0.0", port=5000, use_debugger=True, threaded=True))

@manager.command
def creare():
    pass

if __name__ == '__main__':
    manager.run()