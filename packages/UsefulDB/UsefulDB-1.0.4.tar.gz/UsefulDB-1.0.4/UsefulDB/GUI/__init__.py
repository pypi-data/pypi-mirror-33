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

import os
import json
import shutil
import pymysql
import platform
import datetime
import webbrowser
from tkinter import *

__author__ = 'Elisey Sharov'

with open('config.json', mode='r') as f:
    data = json.load(f)
    VERSION = data['version']

root = Tk()
root.title('UsefulDB GUI')
root.geometry('300x400')

def create():
    def create_user():
        window = Toplevel()
        window.title('UsefulDB GUI: create user')
        window.geometry('300x400')
        name_text = Label(window, text='Username:')
        name_text.place(x=0, y=0)
        pass_text = Label(window, text='Password:')
        pass_text.place(x=0, y=20)
        name_entry = Entry(window)
        name_entry.place(x=100, y=0)
        pass_entry = Entry(window)
        pass_entry.place(x=100, y=20)
        def confirm_create():
            strd = var1.get()
            if strd == 1:
                try:
                    with open('root.json', mode='r') as f:
                        data = json.load(f)
                        rName = data['user']
                        rPass = data['pass']
                    answer = input('You already have super-user. Do you want to rewrite it? (Y/N): ')
                    if answer == 'Y' or 'y':
                        with open('root.json', mode='w') as f:
                            dict = {}
                            dict['user'] = name_entry.get()
                            dict['pass'] = pass_entry.get()
                            json.dump(dict, f)
                            window_2 = Toplevel()
                            window_2.title('Excellent!')
                            window_2.geometry('300x400')
                            dhfjd = Label(window_2, text='Super-user {} succesfully created!'.format(name_entry.get()))
                            dhfjd.pack()
                    else:
                        pass
                except:
                    with open('root.json', mode='w') as f:
                        dict = {}
                        dict['user'] = name_entry.get()
                        dict['pass'] = pass_entry.get()
                        json.dump(dict, f)
                        window_2 = Toplevel()
                        window_2.title('Excellent!')
                        window_2.geometry('300x400')
                        dhfjd = Label(window_2, text='Super-user {} succesfully created!'.format(name_entry.get()))
                        dhfjd.pack()
            else:
                print('Stopping...')
                pass
        def super_user_info():
            window = Toplevel()
            window.title('UsefulDB GUI: create user info')
            window.geometry('300x400')
            text = Label(window, text='Information:\nAttention! Creating a superuser gives you\nnot only access to the command panel,\nbut also the risk of breaking anything.\nBe careful when using this important feature')
            text.pack()
        var1 = IntVar()
        super_user_info_button = Button(window, text='Warning', command=super_user_info)
        super_user_info_button.place(x=0, y=50)
        check1 = Checkbutton(window, text='I understand', variable=var1)
        check1.place(x=0, y=80)
        confirm = Button(window, text='Confirm', command=confirm_create)
        confirm.place(x=0, y=110)
    def create_table():
        window = Toplevel()
        window.title('UsefulDB GUI: create table')
        window.geometry('300x400')
        table_name_text = Label(window, text='Table name:')
        table_name_text.place(x=0, y=0)
        table_columns_text = Label(window, text='Table columns:')
        table_columns_text.place(x=0, y=30)
        table_name_entry = Entry(window)
        table_name_entry.place(x=100, y=0)
        table_columns_entry = Entry(window)
        table_columns_entry.place(x=100, y=30)
        def create_table_confirm():
            columns = table_columns_entry.get()
            name = table_name_entry.get()
            columns = int(columns)
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
        confirm = Button(window, text='Create', command=create_table_confirm)
        confirm.place(x=0, y=60)
    def create_database():
        window = Toplevel()
        window.title('UsefulDB GUI: create database')
        window.geometry('300x400')
        db_text = Label(window, text='Database name:')
        db_text.place(x=0, y=0)
        db_entry = Entry(window)
        db_entry.place(x=100, y=0)
        def create_db():
            name = db_entry.get()
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
        db_create_button = Button(window, text='Create database', command=create_db)
        db_create_button.place(x=0, y=30)
    window = Toplevel()
    window.title('UsefulDB GUI: create')
    window.geometry('300x400')
    create_user_button = Button(window, text='Create user', command=create_user)
    create_user_button.pack()
    create_table_button = Button(window, text='Create table', command=create_table)
    create_table_button.pack()
    create_database_button = Button(window, text='Create database', command=create_database)
    create_database_button.pack()

def delete():
    window = Toplevel()
    window.title('UsefulDB GUI: delete')
    window.geometry('300x400')
    def delete_user():
        window = Toplevel()
        window.title('UsefulDB GUI: delete user')
        name_text = Label(window, text='Username:')
        name_text.place(x=0, y=0)
        pass_text = Label(window, text='Password:')
        pass_text.place(x=0, y=30)
        name_entry = Entry(window)
        name_entry.place(x=100, y=0)
        pass_entry = Entry(window)
        pass_entry.place(x=100, y=30)
        def confirm_func():
            try:
                name = name_entry.get()
                password = pass_entry.get()
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
            except:
                print("You don't have super-user")
        confirm_delete = Button(window, text='Delete', command=confirm_func)
        confirm_delete.place(x=0, y=60)
    def delete_table():
        window = Toplevel()
        window.title('UsefulDB GUI: delete table')
        window.geometry('300x400')
        name_text = Label(window, text='Table name:')
        name_text.place(x=0, y=0)
        name_entry = Entry(window)
        name_entry.place(x=100, y=0)
        name = name_entry.get()
        def confirm_func():
            name = name_entry.get()
            now = datetime.datetime.now()
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
            try:
                with connection.cursor() as cursor:
                    sql = 'DROP TABLE `%s`;' #sql-code
                    cursor.execute(sql, ('{}'.format(name)))
                    connection.commit() #saving changes
                    print('Table {} succesfully deleted'.format(name))
            except Exception as er:
                print('Something  is wrong: ', er)
                with open('connection_log.txt', mode='a') as f:
                    f.write('[{}]: SQL: DROP TABLE `%s`; Error: {}\n'.format(now, er))
            finally:
                connection.close()
        confirm_button = Button(window, text='Delete table {}'.format(name), command=confirm_func)
        confirm_button.place(x=0, y=30)
    def delete_database():
        window = Toplevel()
        window.title('UsefulDB GUI: delete database')
        window.geometry('300x400')
        name_text = Label(window, text='Database name:')
        name_text.place(x=0, y=0)
        name_entry = Entry(window)
        name_entry.place(x=100, y=0)
        name = name_entry.get()
        def confirm_func():
            name = name_entry.get()
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
        confirm_button = Button(window, text='Delete database {}'.format(name), command=confirm_func)
        confirm_button.place(x=0, y=30)
    delete_user_button = Button(window, text='Delete user', command=delete_user)
    delete_user_button.pack()
    delete_table_button = Button(window, text='Delete table', command=delete_table)
    delete_table_button.pack()
    delete_database_button = Button(window, text='Delete database', command=delete_database)
    delete_database_button.pack()
def change_edit():
    window = Toplevel()
    window.title('UsefulDB GUI: change(edit)')
    window.geometry('300x400')
    warning = Label(window, text='Warning!\nThis feature is not working.\nMaybe coming soon I will write it')
    warning.pack()

def info():
    window = Toplevel()
    window.title('UsefulDB GUI: info')
    window.geometry('300x400')
    pyversion = platform.python_version()
    opersyst = platform.system()
    information = Label(window, text='Info:\nUsefulDB {}\nPython {}\n OS {}'.format(VERSION, pyversion, opersyst))
    information.pack()

create_button = Button(root, text='Create', command=create)
create_button.pack()
delete_button = Button(root, text='Delete', command=delete)
delete_button.pack()
change_edit_button = Button(root, text='Change(edit)', command=change_edit)
change_edit_button.pack()
info_button = Button(root, text='Information', command=info)
info_button.pack()
'''
btn_calc.bind('<Button-1>', lambda event: sinus(entry_w.get(),
	                                            entry_phi.get(),
												entry_A.get(),
												entry_dy.get()))
'''

root.mainloop()