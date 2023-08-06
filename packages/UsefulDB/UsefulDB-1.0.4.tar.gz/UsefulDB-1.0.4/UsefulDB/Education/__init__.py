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

#import packages for framework
import os
import time
import json
import shutil
import datetime
import platform
import urllib
import requests
import bs4
import MySQLdb

__author__ = 'Elisey Sharov'

try:
    #system for checking the availability of user settings
    try:
        with open('config.json', mode='r') as f:
            data = json.load(f)
            use_lib = data['use_lib']
            version = data['version']
            PATH = data['path']
            lang = data['lang']
    except:
        answer = input('By using this framework, you accept the license agreement. Do you confirm?(Yes/No): ')
        if len(answer) > 2:
            dict = {}
            with open('config.json', mode='w') as f:
                dict['use_lib'] = True
                dict['version'] = 'Beta'
                dict['path'] = input('Enter the path to the folder where your users and databases will bestored(C:/...): ')
                dict['lang'] = input('Select the language to use (English/Russian): ')
                json.dump(dict, f)
            print('Applying settings...')
            time.sleep(2)
            with open('config.json', mode='r') as fh:
                data = json.load(fh)
                use_lib = data['use_lib']
                version = data['version']
                PATH = data['path']
                lang = data['lang']
        else:
            print("You don't can use this framework")
            time.sleep(5)
            quit()

    with open('config.json', mode='r') as f:
        DATA = json.load(f)
        if DATA['lang'] == 'Russian':
            create_info = 'Эта команда создаёт пользователей и базы данных'
            create_user_info = 'Эта команда создаёт пользователей'
            create_database_info = 'Эта команда создаёт базы данных'
            delete_info = 'Эта команда удаляет базы данных и пользователей'
            delete_info_user = 'Эта команда удаляет пользователя'
            delete_info_database = 'Эта команда удаляет базу данных'
            searching = 'Поиск ошибок...'
            tracking = 'UsefulDB Tracking: вы изменили конфигурационные настройки. Чтобы их сбросить, откройте файл "config.json" и удалите всё, кроме "version": "<версия>"'
            creating_column_title = 'Имя колонки'
            existing_error = 'Файл не существует'
            deleting_succes = 'Успешно удалено'
            existing_error_2 = 'Пользователь с таким именем уже существует'
            new_version_is_avialable = 'Доступна новая версия!'
            connection_error = 'Система не может проверить наличия новых версий. Проверьте подключение к интернету и повторите попытку'
            already_exists = 'База данных с таким именем уже существует'
            process_error = 'Файл занят другим процессом'
            old_version = 'Вы используете старую версию UsefulDB. Для получения новых функций, исправлений ошибок и новых фич, пожалуйста, обновите UsefulDB'
            unknown_version = 'Вы используете неизвестную версию. Изменяли ли вы этот атрибут в конфигурационном файле?'
            beta_tester_warnings = 'Вы используете Бета-версию UsefulDB. Эта версия может содержать баги и ошибки'
            key_error = 'Ключ не найден'
            succefully = 'Готово'
        else:
            create_info = 'This command creates a user and database'
            create_user_info = 'This command creates a user'
            create_database_info = 'This command creates a database'
            delete_info = 'This command deletes users and databases'
            delete_info_user = 'This command deletes users'
            delete_info_database = 'This command deletes databases'
            searching = 'Searching errors...'
            tracking = "UsefulDB Tracking: You change the system settings. To reset them, open the file 'config.json' and delete everything except 'version'"
            creating_column_title = 'Title of column: '
            existing_error = 'File not exists'
            deleting_succes = 'Succesfully finished'
            existing_error_2 = 'Command is not exists'
            new_version_is_avialable = 'New version is detected. For get new functions or fix bugs, please, update UsefulDB'
            connection_error = "System don't can check new versions. Please, check the Internet-connection and retry"
            already_exists = 'Database with that name already exists'
            process_error = 'File is in use by another process'
            old_version = 'You use an badly old version. Please, update UsefulDB!'
            unknown_version = 'You use unknown version of UsefulDB. Do you change file config.json?'
            beta_tester_warnings = 'You use a Beta-version of UsefulDB. This version may have errors and bags'
            key_error = 'Key is not exists'
            succefully = 'Done'

    if use_lib:
        try:
            s = requests.get('http://scgofficial.esy.es/version.html')
            b = bs4.BeautifulSoup(s.text, "html.parser")
            p1 = b.select('.version .fw')
            result_ver = p1[0].getText()
            if version == result_ver:
                #internet_connection = True
                pass
            else:
                if version == 'Beta':
                    print(beta_tester_warnings)
                    internet_connection = True
                elif version == '1.0.0' or '1.0.1' or '1.0.2' or '1.0.3':
                    print(old_version)
                    print(new_version_is_avialable)
                    internet_connection = True
                else:
                    print(unknown_version)
                    internet_connection = True
        except:
            print(connection_error)
            internet_connection = False

        with open('log.txt', mode='a') as f:
            info = platform.machine()
            now = datetime.datetime.now()
            pyversion = platform.python_version()
            os = platform.system()
            f.write('[{}]: UsefulDB {}, machine: {}, Python {}, OS: {}; Config: [lang={}, path={}, use={}]; Internet-connection: {}; Condition code: 100\n'.format(
                     now, version, info, pyversion, os, lang, PATH, use_lib, internet_connection))

        class create:
            def __init__(self, obj):
                self.Object = obj

            def info():
                print(create_info)

            class user:
                def __init__(self, u, p):
                    self.User = u
                    self.Pass = p

                def info():
                    print(create_user_info)

                def params(user, password, root=False):
                    if root:
                        with open('registered_users.json', mode='r') as f:
                            data = json.load(f)
                            num = int(data['count'])
                            num += 1
                            with open('registered_users.json', mode='w') as fh:
                                dict = {}
                                dict['count'] = num
                                json.dump(dict, fh)
                            with open('rooted_users.json', mode='w') as fhk:
                                dict = {}
                                dict['user'] = user
                                dict['password'] = password
                                dict['root'] = root
                                json.dump(dict, fhk)
                            if DATA['lang'] == 'Russian':
                                print('Супер-пользователь {} успешно создан'.format(user))
                            else:
                                print('Super-user {} is created succefully'.format(user))
                        with open('log.txt', mode='a') as f:
                            info = platform.machine()
                            now = datetime.datetime.now()
                            pyversion = platform.python_version()
                            os = platform.system()
                            f.write('[{}]: UsefulDB {}, machine: {}, Python {}, OS: {}; Config: [lang={}, path={}, use={}]; Internet-connection: {}; Condition code: 200\n'.format(
                                     now, version, info, pyversion, os, lang, PATH, use_lib, internet_connection))
                    else:
                        with open('registered_users.json', mode='r') as f:
                            data = json.load(f)
                            num = int(data['count'])
                            num += 1
                            dict = {}
                            with open('registered_users.json', mode='w') as fh:
                                dict['count'] = num
                                json.dump(dict, fh)
                            with open('user_{}.json'.format(num), mode='w') as fhk:
                                dict['user'] = user
                                dict['password'] = password
                                dict['root'] = root
                                json.dump(dict, fhk)
                            if DATA['lang'] == 'Russian':
                                print('Пользователь {} успешно создан'.format(user))
                            else:    
                                print('User {} is created succefully'.format(user))
                            with open('log.txt', mode='a') as f:
                                info = platform.machine()
                                now = datetime.datetime.now()
                                pyversion = platform.python_version()
                                os = platform.system()
                                f.write('[{}]: UsefulDB {}, machine: {}, Python {}, OS: {}; Config: [lang={}, path={}, use={}]; Internet-connection: {}; Condition code: 200\n'.format(
                                         now, version, info, pyversion, os, lang, PATH, use_lib, internet_connection))

            class database:
                def __init__(self, name, columns):
                    self.Name = name
                    self.Columns = int(columns)

                def info():
                    print(create_database_info)

                def params(name, columns):
                    try:
                        with open('database_{}.json'.format(name), mode='r') as f:
                            data = json.load(f)
                        print(already_exists)
                        with open('log.txt', mode='a') as f:
                            info = platform.machine()
                            now = datetime.datetime.now()
                            pyversion = platform.python_version()
                            os = platform.system()
                            f.write('[{}]: UsefulDB {}, machine: {}, Python {}, OS: {}; Config: [lang={}, path={}, use={}]; Internet-connection: {}; Condition code: 200\n'.format(
                                     now, version, info, pyversion, os, lang, PATH, use_lib, internet_connection))
                    except FileNotFoundError as er:
                        columns = int(columns)
                        dict = {}
                        column_count = 0
                        while columns > column_count:
                            column_count += 1
                            column_name = input(creating_column_title)
                            with open(r'{}database_{}.json'.format(PATH, name), mode='w') as f:
                                dict['{}'.format(column_name)] = None
                                json.dump(dict, f)
                        if DATA['lang'] == 'Russian':
                            print('База данных {} успешно создана'.format(name))
                        else:
                            print('Database {} is created succefully'.format(name))
                        with open('log.txt', mode='a') as f:
                            info = platform.machine()
                            now = datetime.datetime.now()
                            pyversion = platform.python_version()
                            os = platform.system()
                            f.write('[{}]: UsefulDB {}, machine: {}, Python {}, OS: {}; Config: [lang={}, path={}, use={}]; Internet-connection: {}; Condition code: 200\n'.format(
                                     now, version, info, pyversion, os, lang, PATH, use_lib, internet_connection))

        class delete:
            def __init__(self, n):
                self.Name = n

            def info():
                print(delete_info)

            class database:
                def __init__(self, name, columns):
                    self.Name = name
                    self.Confirm = columns

                def info():
                    print(delete_info_database)

                def params(name, confirm=False):
                    if confirm:
                        name = 'database_{}.json'.format(name)
                        try:
                            os.remove(r'{}{}'.format(path, name))
                            print(deleting_succes)
                        except:
                            print(existing_error)
                        finally:
                            with open('log.txt', mode='a') as f:
                                info = platform.machine()
                                now = datetime.datetime.now()
                                pyversion = platform.python_version()
                                os = platform.system()
                                f.write('[{}]: UsefulDB {}, machine: {}, Python {}, OS: {}; Config: [lang={}, path={}, use={}]; Internet-connection: {}; Condition code: 200\n'.format(
                                         now, version, info, pyversion, os, lang, PATH, use_lib, internet_connection))
                    else:
                        pass

            class user:
                def __init__(self, n, p):
                    self.Name = n
                    self.Pass = p

                def info():
                    print(delete_info_user)

                def params(user, password, confirm=False,
                           root=False, static=False,
                           save=False):
                    if confirm:
                        if static:
                            if root:
                                print(root_and_stacic)
                            else:
                                if DATA['lang'] == 'Russian':
                                    print('Удаление пользователя {}...'.format(user))
                                    n = 0
                                    while confirm:
                                        time.sleep(0.2)
                                        n += 1
                                        try:
                                            with open('user_{}.json'.format(n), mode='r') as f:
                                                data = json.load(f)
                                            if user == data['user']:
                                                if save:
                                                    shutil.copyfile(r'{}user_{}.json'.format(PATH, n), r'{}user_{}_SAVED.json'.format(PATH, n))
                                                else:
                                                    pass
                                                os.remove('user_{}.json'.format(n))
                                                print(deleting_succes)
                                                break
                                        except:
                                            print(existing_error_2)
                                            break
                                else:
                                    if DATA['lang'] == 'Russian':
                                        print('Удаление пользователя {}...'.format(user))
                                    else:
                                        print('Deleting user {}...'.format(user))
                                    n = 0
                                    while confirm:
                                        try:
                                            time.sleep(0.2)
                                            n += 1
                                            with open(r'{}user_{}.json'.format(PATH, n), mode='r') as f:
                                                data = json.load(f)
                                            if user == data['user']:
                                                os.remove(r'{}user_{}.json'.format(PATH, n))
                                                print(deleting_succes)
                                                break
                                        except Exception as er:
                                            print(existing_error_2, er)
                                            break
                        if root:
                            if static:
                                print(root_and_stacic)
                            else:
                                if DATA['lang'] == 'Russian':
                                    print('Удаление супер-пользователя {}...'.format(user))
                                else:
                                    print('Deleting super-user {}...'.format(user))
                                try:
                                    with open('rooted_users.json', mode='r') as f:
                                        data = json.load(f)
                                        name = data['user']
                                        passw = data['password']
                                        root = data['root']
                                    if user == name and root:
                                        os.remove('rooted_users.json')
                                        print(deleting_succes)
                                    else:
                                        print(user_not_exists_or_dont_rooted)
                                except PermissionError as er:
                                    print(process_error)
                                    raise er
                                except Exception as er:
                                    print(existing_error)
                                    raise er
                    else:
                        pass

                    with open('log.txt', mode='a') as f:
                        info = platform.machine()
                        now = datetime.datetime.now()
                        pyversion = platform.python_version()
                        os = platform.system()
                        f.write('[{}]: UsefulDB {}, machine: {}, Python {}, OS: {}; Config: [lang={}, path={}, use={}]; Internet-connection: {}; Condition code: 200\n'.format(
                                 now, version, info, pyversion, os, lang, PATH, use_lib, internet_connection))

        class edit:
            def __init__(self, n, t):
                self.Name = n
                self.Type = t

            def info():
                print(edit_info)

            class database:
                def __init__(self, n, c):
                    self.Name = n
                    self.Commit = c

                class add:
                    def __init__(self, i):
                        self.Item = i

                    def column(name, title):
                        name = 'database_{}.json'.format(name)
                        dict = {}
                        with open(r'{}{}'.format(PATH, name), mode='r') as f:
                            data = json.load(f)
                            dict = data
                            dict2 = {title: None}
                            dict.update(dict2)
                        with open(r'{}{}'.format(PATH, name), mode='w') as fh:
                            json.dump(dict, fh)
                            print(succefully)
                class remove:
                    def __init__(self, i):
                        self.Item = i

                    def column(name, title):
                        name = 'database_{}.json'.format(name)
                        with open(r'{}{}'.format(PATH, name), mode='r') as f:
                            data = json.load(f)
                            dict = data
                            try:
                                dict.pop(title)
                            except Exception as er:
                                print(key_error)
                                raise er
                        with open(r'{}{}'.format(PATH, name), mode='w') as fh:
                            json.dump(dict, fh)
                            print(succefully)

    else:
        time.sleep(2)
        print(searching)
        time.sleep(4)
        print(tracking)
        time.sleep(10)
        with open('log.txt', mode='a') as f:
            info = platform.machine()
            now = datetime.datetime.now()
            pyversion = platform.python_version()
            os = platform.system()
            f.write('[{}]: UsefulDB {}, machine: {}, Python {}, OS: {}; Config: [lang={}, path={}, use={}]; Internet-connection: {}; Condition code: 100\n'.format(
                     now, version, info, pyversion, os, lang, PATH, use_lib, internet_connection))
except NameError as error_name:
    with open('log.txt', mode='a') as f:
        info = platform.machine()
        now = datetime.datetime.now()
        pyversion = platform.python_version()
        os = platform.system()
        f.write('[{}]: UsefulDB {}, machine: {}, Python {}, OS: {}; Config: [lang={}, path={}, use={}]; Internet-connection: {}; Condition code: 101; Error: {}\n'.format(
                 now,  version, info, pyversion, os, lang, PATH, use_lib, internet_connection, error_name))
except KeyError as error_key:
    with open('log.txt', mode='a') as f:
        info = platform.machine()
        now = datetime.datetime.now()
        pyversion = platform.python_version()
        os = platform.system()
        f.write('[{}]: UsefulDB {}, machine: {}, Python {}, OS: {}; Config: [lang={}, path={}, use={}]; Internet-connection: {}; Condition code: 104; Error: {}\n'.format(
                 now, version, info, pyversion, os, lang, PATH, use_lib, internet_connection, error_key))
except ModuleNotFoundError as error_module:
    with open('log.txt', mode='a') as f:
        info = platform.machine()
        now = datetime.datetime.now()
        pyversion = platform.python_version()
        os = platform.system()
        f.write('[{}]: UsefulDB {}, machine: {}, Python {}, OS: {}; Config: [lang={}, path={}, use={}]; Internet-connection: {}; Condition code: 206; Error: {}\n'.format(
                 now, version, info, pyversion, os, lang, PATH, use_lib, internet_connection, error_module))