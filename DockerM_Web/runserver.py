#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from app import create_app, db, mail
from gevent.wsgi import WSGIServer
from app.lib.dbModel import User, Containers, Images ,ContainerStatus
from flask_script import Manager, Shell, Server, Command
from flask_migrate import Migrate, MigrateCommand


app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)


def shell_context():
    return dict(app=app, db=db, User=User, Containers=Containers, Images=Images, Container_Status=ContainerStatus)


# class CreateDb(Command):
#
#     def run(self):
#         db.create_all()


# @manager.command
# def create_db():
#     db.create_all()
#
#
# @manager.command
# def drop_db():
#     db.drop_all()


manager.add_command("runserver", Server(host="0.0.0.0", port=5000, use_debugger=True, threaded=True))
manager.add_command("shell", Shell(make_context=shell_context()))
# manager.add_command("create_db", CreateDb())
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()