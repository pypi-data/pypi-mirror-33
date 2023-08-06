'''
This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

__author__ = 'Elisey Sharov' #name of UsefulDB author

#importing standart packages for framework
import os
import json
import time
import shutil
import datetime
import platform
#importing PIP-packages
import requests
import bs4
import pymysql.cursors

#get info about installed version
with open('config.json', mode='r') as f:
    data = json.load(f)
    VERSION = data['version']

#function for fast saving config, optimize lines of code
def confirm_rules():
    with open('config.json', mode='w') as f:
        dict = {}
        dict['version'] = VERSION
        dict['whatisit'] = True
        dict['host'] = input('Insert your host: ')
        dict['user'] = input('Insert host user: ')
        dict['password'] = input('Insert host password: ')
        dict['hard_mode'] = False
        json.dump(dict, f)

try: #try to check new version and condition of internet-connection
    s = requests.get('http://scgofficial.esy.es/version.html')
    b = bs4.BeautifulSoup(s.text, "html.parser")
    p1 = b.select('.version .fw')
    result_ver = p1[0].getText()
    if VERSION == result_ver:
        NET = True #you have internet-connection
    else:
        if VERSION == 'Beta': #you wanna to crash your PC?
            NET = True #you have internet-connection
            print('You have a Beta-version of UsefulDB. This version may contain more bugs and errors, than simple version')
        elif VERSION == '1.0.0' or '1.0.1' or '1.0.2' or '1.0.3': #if you use this versions - you're a bad man
            NET = True #you have internet-connection
            print('You have old version of UsefulDB. Please, update the framework for get new features and bug fixes!')
        else: #another versions is not can be
            NET = True #you have internet-connection
            print("Are you change the 'config.json' file?")
except: #if you haven't internet-connection or sever have problems
    NET = False #you haven't internet-connection
    print("System can't check avialable of new versions. Check the internet-connection and try again")

#checking code for errors to write it to file log.txt
try:
    try: #checking info in config.json(first launch or second+)
        with open('config.json', mode='r') as f:
            data = json.load(f)
            VERSION = data['version']
            USE = data['whatisit']
            host = data['host']
            db_user = data['user']
            db_pass = data['password']
            hmode = data['hard_mode']
        shutil.copy(r'config.json', r'gui\config.json')
    #if it first framework launch
    except Exception as error:
        answer = input('By using this framework, you accept the rules of GNU 3.0 License. Are you confirm? (Y/N): ')
        if answer == 'Y': #if input = Y, calling function
            confirm_rules()
            USE = True #confirmation
        elif answer == 'y': #also if input = y
            confirm_rules()
            USE = True #confirmation
        else: #you must to accept the license rules
            print("You don't can use this framework")
            time.sleep(8)
            quit()
        raise error

    if USE:
        #don't touch that! It just for log.txt! Your IP and other like that info don't will be written
        with open('log.txt', mode='a') as f:
            info = platform.machine() #32bit or 64?
            now = datetime.datetime.now() #time right now
            pyversion = platform.python_version() #version of Python. If you have < 3, frameword don't will be work
            opersyst = platform.system() #operation system
            f.write('[{}]: '.format(now)
                    + 'UsefilDB {}; '.format(VERSION)
                    + 'Python {}; '.format(pyversion)
                    + 'Machine {}; '.format(info)
                    + 'OS {}; '.format(opersyst)
                    + 'Config [use = {}]; '.format(USE)
                    + 'Internet-connection: {};\n'.format(NET)
                   )

        if NET: #framework required internet. Without it framework don't will be work, becauze he connect with server
            class create: #create something
                def __init__(self, i):
                    self.Item = i

                def info():
                    print('Wanna to create something? Call this class!')

                class user: #create super-user
                    def __init__(self, n, p):
                        self.Name = n
                        self.Pass = p

                    def info():
                        print('Wanna get the acces to command panel? Create a super-user!')

                    def params(name, password, confirm=False): #name - username, password - pass, confirm - creation of super-user
                                                               #give you acces to the command panel. Its panel can break something
                                                               #please, be accurate
                        if confirm: #are you confirm creating os super-user? It can break something
                            try:
                                with open('root.json', mode='r') as f: #are you have super-user yet?
                                    data = json.load(f)
                                    user = data['user']
                                    password = data['pass']
                                    print('You already have super-user')
                            except Exception as error: #if not
                                with open('root.json', mode='w') as f:
                                    dict = {}
                                    dict['user'] = name
                                    dict['pass'] = password
                                    json.dump(dict, f)
                                    print('Super-user {} is created. Now you can use command panel'.format(name))
                        else: #if not
                            pass

                class database: #create database
                    def __init__(self, n):
                        self.Name = n
                        
                    def info():
                        print('Fastly database creation')

                    def params(name): #name - database name
                        now = datetime.datetime.now() #time right now
                        with open('config.json', mode='r') as f:
                            data = json.load(f)
                            host = data['host']
                            db_user = data['user']
                            db_pass = data['password']
                        try: #are you have correct info of database name?
                            with open('host.json', mode='r') as f:
                                data = json.load(f)
                                db = data['database']
                        except Exception as error: #if not
                            answer = input('Insert the database name: ')
                            with open('host.json', mode='w') as f:
                                dict = {}
                                dict['database'] = answer
                                json.dump(dict, f)
                            raise error
                        connection = pymysql.connect(host=host,
                                                     user=db_user,
                                                     password=db_pass,
                                                     charset='utf8mb4',
                                                     cursorclass=pymysql.cursors.DictCursor
                                                     ) #connection with your host 
                        try: #trying to add new database
                            with connection.cursor() as cursor:
                                sql = 'CREATE DATABASE `%s`;' #sql-code
                                cursor.execute(sql, ('{}'.format(name))) #sql-code running
                                connection.commit() #saving changes
                            with open('connection_log.txt', mode='a') as f: #info fot connection_log.txt If you have a
                                                                            #problem, you should send me that file too
                                f.write('[{}]: SQL: {}\n'.format(now, sql))
                        except Exception as er:
                            print('Something is wrong: ', er)
                            with open('connection_log.txt', mode='a') as f:
                                f.write('[{}]: SQL: {}\n'.format(now, sql))
                        finally:
                            connection.close() #if we don't close connection, it can doing something bad

                class table: #create table in database
                    def __init__(self, n):
                        self.Name = n

                    def info():
                        print('Wanna create table? Call create.table.params(name, columns)!')

                    def params(name, columns): #name - table name, columns - count of columns
                        columns = int(columns) #if you write like '3'(must be 3), system converting str to int
                        with open('config.json', mode='r') as f:
                            data = json.load(f)
                            host = data['host']
                            db_user = data['user']
                            db_pass = data['password']
                        try: #are you have correct info of database name?
                            with open('host.json', mode='r') as f:
                                data = json.load(f)
                                db = data['database']
                        except Exception as error: #if not
                            answer = input('Insert the database name: ')
                            with open('host.json', mode='w') as f:
                                dict = {}
                                dict['database'] = answer
                                json.dump(dict, f)
                            raise error
                        #connecting to database
                        connection = pymysql.connect(host=host,
                                                     user=db_user,
                                                     password=db_pass,
                                                     db=db,
                                                     charset='utf8mb4',
                                                     cursorclass=pymysql.cursors.DictCursor
                                                     ) #connection with your host
                        number = 0 #for checking number of column
                        start_num = 0 #for cheking primary
                        while number < columns: #calculator for checking creating columns: it's first? second? comething else?
                            columnName = input('Name of column: ') #column name
                            columnLength = int(input('Length: ')) #column length
                            columnType = input('Type (int, varchar or another): ') #column type
                            columnCondition = bool(input('Is this column primary? (True/False): ')) #is this primary?
                            if start_num <= 0: #create CONST, its requiered for table with containg more than 1 columns
                                MAINCOLUMN = columnName
                            else: #if column number isn't 0(no-primary)
                                columnCondition = False #if something is wrong, we don't have contain 2 primary columns
                            try:
                                now = datetime.datetime.now() #time right now
                                if columnCondition:
                                    start_num += 1
                                    with connection.cursor() as cursor:
                                        if columnName == 'id': #it's cool feature: id always needed in A_I
                                            sql = 'CREATE TABLE `%s`(`{}` {}({}) NOT NULL AUTO_INCREMENT, PRIMARY KEY (`id`));'.format(columnName,
                                                                                                                   columnType,
                                                                                                                   columnLength
                                                                                                                   )
                                        else: #or not?
                                            sql = 'CREATE TABLE `%s`(`{}` {}({}) NOT NULL);'.format(columnName,
                                                                                                    columnType,
                                                                                                    columnLength
                                                                                                    )
                                        with open('connection_log.txt', mode='a') as f:
                                            f.write('[{}]: columnID: {}; columnName: {}; columnType: {}; '.format(now, number,
                                                                                                                  columnName,
                                                                                                                  columnType
                                                                                                                  )
                                                    + 'columnLength: {}, columnCondition: {}; SQL: {}\n'.format(columnLength,
                                                                                                                columnCondition,
                                                                                                                sql))
                                        cursor.execute(sql, ('{}'.format(name)))
                                        connection.commit() #saving changes
                                else:
                                    with connection.cursor() as cursor:
                                        sql = "ALTER TABLE `%s` ADD `{}` {}({}) NOT NULL AFTER `{}`;".format(columnName,
                                                                                                             columnType,
                                                                                                             columnLength,
                                                                                                             MAINCOLUMN
                                                                                                             )
                                        with open('connection_log.txt', mode='a') as f:
                                            f.write('[{}]: columnID: {}; columnName: {}; columnType: {}; '.format(now, number,
                                                                                                                  columnName,
                                                                                                                  columnType
                                                                                                                  )
                                                    + 'columnLength: {}, columnCondition: {}; SQL: {}\n'.format(columnLength,
                                                                                                                columnCondition,
                                                                                                                sql))
                                        cursor.execute(sql, ('{}'.format(name)))
                                        connection.commit() #saving changes
                            except Exception as er:
                                print('Something wrong: ', er)
                                now = datetime.datetime.now() #time right now
                                with open('connection_log.txt', mode='a') as f:
                                    f.write('[{}]: columnID: {}; columnName: {}; columnType: {}; '.format(now, number,
                                                                                                    columnName,
                                                                                                    columnType)
                                            + 'columnLength: {}, columnCondition: {}; SQL: {} Error: {};\n'.format(columnLength,
                                                                                                                   columnCondition,
                                                                                                                   sql, er))
                            finally:
                                number += 1 #if something is broken, we must add that. you aren't needed in infinity cycle
                            if number > columns:
                                connection.close() #if we don't close connection, it can do something bad
                                break

            class delete: #delete something
                def __init__(self, i):
                    self.Item = i

                def info():
                    print('Wanna delete something? Call this class!')

                class user: #delete user
                    def __init__(self, n, p):
                        self.Name = n
                        self.Pass = p

                    def info():
                        print('Its funcion will delete super-user')

                    def params(name, password, confirm=False, save=True, why='No one can know that'):
                        if confirm: #are you confirm deleting user?
                            if save: #do you want to save data?
                                try:
                                    with open('root.json', mode='r') as f:
                                        data = json.load(f)
                                        rName = data['user']
                                        rPass = data['pass']
                                    if name != rName: #it's a super-user. another rules. only hardcore. unauthorized access?
                                        print('Username "{}" is not matched'.format(name))
                                    elif password != rPass: #it's a super-user. another rules. only hardcore. unauthorized access?
                                        print("Password isn't correct")
                                    else: #if your info is correctly, run function
                                        shutil.copy(r'root.json', r'root_SAVED.json') #saving file
                                        os.remove(r'root.json') #deleting file
                                        print('User {} succesfully deleted'.format(name))
                                        with open('why.txt', mode='a') as f:
                                            f.write('{}'.format(why))
                                except Exception as er:
                                    print("You don't have super-user", er)
                            else: #if you don't want to save
                                try:
                                    with open('root.json', mode='r') as f:
                                        data = json.load(f)
                                        rName = data['user']
                                        rPass = data['pass']
                                    if name != rName: #it's a super-user. another rules. only hardcore. unauthorized access?
                                        print('Username "{}" is not matched'.format(name))
                                    elif password != rPass: #it's a super-user. another rules. only hardcore. unauthorized access?
                                        print("Password isn't correct")
                                    else: #if your info is correctly, run function
                                        os.remove(r'root.json') #deleting file
                                        #where is saving???
                                        print('User {} succesfully deleted'.format(name))
                                        with open('why.txt', mode='a') as f:
                                            f.write('{}'.format(why))
                                except Exception as er:
                                    print("You don't have super-user", er)
                        else: #if you don't confirm - command isn't running
                            pass

                class database: #delete database
                    def __init__(self, n):
                        self.Name = n

                    def info():
                        print('Wanna delete database? Just call this function')

                    def params(name, confirm=False):
                        with open('config.json', mode='r') as f:
                            data = json.load(f)
                            host = data['host']
                            db_user = data['user']
                            db_pass = data['password']
                        connection = pymysql.connect(host=host,
                                                     user=db_user,
                                                     password=db_pass,
                                                     charset='utf8mb4',
                                                     cursorclass=pymysql.cursors.DictCursor
                                                     ) #connection with your host
                        now = datetime.datetime.now() #time right now
                        if confirm: #are you confirm your choise? do you really want to delete database?
                            try:
                                with connection.cursor() as cursor:
                                    sql = 'DROP DATABASE `%s`;' #sql-code
                                    cursor.execute(sql, ('{}'.format(name)))
                                    with open('connection_log.txt', mode='a') as f:
                                        f.write('[{}]: SQL: {}\n'.format(now, sql))
                                    connection.commit() #saving changes
                                    print('Database {} succesfully deleted'.format(name))
                            except Exception as er:
                                print('Something is wrong: ', er)
                                with open('connection_log.txt', mode='a') as f:
                                    f.write('[{}]: SQL: {} Error: {}\n'.format(now, sql, er))
                                raise er
                            finally:
                                connection.close() #closing connection for safely exit
                        else:
                            pass

                class table: #delete table
                    def __init__(self, n):
                        self.Name = n

                    def info():
                        print('Wanna delete table? Just call this function')

                    def params(name, confirm=False):
                        now = datetime.datetime.now() #time right now
                        with open('config.json', mode='r') as f:
                            data = json.load(f)
                            host = data['host']
                            db_user = data['user']
                            db_pass = data['password']
                        try: #are you have correct info of database name?
                            with open('host.json', mode='r') as f:
                                data = json.load(f)
                                db = data['database']
                        except Exception as error: #if not
                            answer = input('Insert the database name: ')
                            with open('host.json', mode='w') as f:
                                dict = {}
                                dict['database'] = answer
                                json.dump(dict, f)
                            raise error
                        connection = pymysql.connect(host=host,
                                                     user=db_user,
                                                     password=db_pass,
                                                     db=db,
                                                     charset='utf8mb4',
                                                     cursorclass=pymysql.cursors.DictCursor
                                                     ) #connection with your host
                        if confirm: #are you confirm your choise?
                            try:
                                with connection.cursor() as cursor:
                                    sql = 'DROP TABLE `%s`;' #sql-code
                                    cursor.execute(sql, ('{}'.format(name)))
                                    with open('connection_log.txt', mode='a') as f:
                                        f.write('[{}]: SQL {}'.format(now, sql))
                                    connection.commit() #saving changes
                                    print('Table {} succesfully deleted'.format(name))
                            except Exception as er:
                                print('Something  is wrong: ', er)
                                with open('connection_log.txt', mode='a') as f:
                                    f.write('[{}]: SQL: DROP TABLE `%s`; Error: {}\n'.format(now, er))
                            finally:
                                connection.close()
                        else:
                            pass

        else: #framework needed in stability of internet-connection and server work
            time.sleep(8)
            pass
    else: #if you trying to launch framework, but you don't accept the licence rules, framework just close himself
        pass

#and this!
except Exception as error:
    with open('log.txt', mode='a') as f:
        info = platform.machine()
        now = datetime.datetime.now()
        pyversion = platform.python_version()
        opersyst = platform.system()
        f.write('[{}]: '.format(now)
                + 'UsefulDB {}; '.format(VERSION)
                + 'Python {}; '.format(pyversion)
                + 'Machine {}; '.format(info)
                + 'OS {}; '.format(opersyst)
                + 'Config [use = {}]; '.format(USE)
                + 'Internet-connection: {}; '.format(NET)
                + 'Error: {};\n'.format(error)
               )