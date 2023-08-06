import os
import time
import platform
import webbrowser
import subprocess
from __init__ import *

access = False

try:
    with open('root.json', mode='r') as f:
        data = json.load(f)
        rName = data['user']
        rPass = data['pass']
        name = input('Input username: ')
        if name == rName:
            passw = input('Input password: ')
            if passw == rPass:
                access = True
                print('Logging into subproces...')
                time.sleep(3)
            else:
                print('Password is not correct')
        else:
            print('User is not matched')
except:
    print('You do not have super-user')

if access:
    def fw_delete(item):
        if item == 'table':
            tableName = input('Table name: ')
            delete.table.params('{}'.format(tableName), confirm=True)
        elif item == 'database':
            dbName = input('Database name: ')
            delete.database.params('{}'.format(dbName), confirm=True)
        elif item == 'user':
            os.remove('root.json')
            print('User removed')
    def fw_create(item):
        if item == 'table':
            tableName = input('Table name: ')
            columnCount = input('Columns: ')
            create.table.params('{}'.format(tableName), '{}'.format(columnCount))
        elif item == 'database':
            dbName = input('Database name: ')
            create.database.params('{}'.format(dbName))
        elif item == 'user':
            with open('root.json', mode='w') as f:
                dict = {}
                dict['user'] = input('Username: ')
                dict['pass'] = input('Password: ')
                json.dump(dict, f)
            print('User created')
    def show(item):
        if item == 'docs':
            webbrowser.open('http://scgofficial.esy.es/UsefulDB/')
        elif item == 'folder':
            path = os.getcwd()
            print(os.listdir(path))
        elif item == 'mangas': #top secret
            webbrowser.open('http://scgofficial.esy.es/mangas/')
        elif item == 'author':
            print('Elisey Sharov. Rostov-on-Don, Russian Federation')
        elif item == 'info':
            info = platform.machine()
            now = datetime.datetime.now()
            pyversion = platform.python_version()
            opersyst = platform.system()
            print('UsefulDB {};\n'.format(VERSION)
                  + 'Python {};\n'.format(pyversion)
                  + 'Machine {};\n'.format(info)
                  + 'OS {};\n'.format(opersyst)
                  + 'Config [use = {}];\n'.format(USE)
                  + 'Internet-connection: {};\n'.format(NET)
                 )
        else:
            print('Function do not have attr {}. Here is contain args: docs, folder, author')
    print('Now, you can do anything, if you have knowledge about Python. Full free')
    while access:
        code = input('$ ')
        time.sleep(2)
        eval(code)
else:
    print('You do not have access to this panel')
    pass
