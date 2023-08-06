import os
import shutil
import __init__
import subprocess
'''
try:
    with open('config.json', mode='r') as f:
        data = json.load(f)
        mode = data['hard_mode']
        if mode:
            hard_mode()
        else:
            safe_mode()
except Exception as er:
    print(er)
print('Welcome to safely changing of frameword work. Do you want to use hard-mode? ')
'''
def second_command():
    code = input('$ ')
    if code == 'change':
        change()
    elif code == 'delete':
        delete()
    elif code == 'show':
        show()
    elif code == 'help':
        fw_help()
    else:
        print('Command is not searched. Please, try again')
        second_command()

def change():
    change_code = input('$change: ')
    if change_code == 'config':
        with open('config.json', mode='r') as f:
            data = json.load(f)
            MODE = data['whatisit']
        if MODE:
            answer = input('You do not needed in this command. You want to stop using framework? (Y/N): ')
            if answer == 'Y' or 'y':
                dict = {}
                with open('config.json', mode='a') as f:
                    dict['whatisit'] = False
                print('Succesfully changed')
            else:
                print('Okay')
        else:
            answer = input("By using this framework, you accept the rules of GNU 3.0 License. Are you confirm? (Y/N): ")
            if answer == 'Y' or 'y':
                with open('config.json', mode='w') as f:
                    dict = {}
                    dict['version'] = VERSION
                    dict['whatisit'] = True
                    dict['host'] = input('Insert your host: ')
                    dict['user'] = input('Insert host user: ')
                    dict['password'] = input('Insert host password: ')
                    dict['hard_mode'] = False
                    json.dump(dict, f)
            else:
                print("You don't can use this framework")
                time.sleep(8)
                quit()
    elif change_code == 'host_info':
        dict = {}
        with open('config.json', mode='a') as f:
            dict['host'] = input('Insert your host: ')
            dict['user'] = input('Insert host user: ')
            dict['password'] = input('Insert host password: ')
            dict['hard_mode'] = False
            json.dump(dict, f)
    else:
        print('Command is not searched. Please, try again')
        second_command()

def delete():
    delete_code = input('$delete: ')
    if delete_code == 'table' or 'database':
        print('Please, use main file for this command')
    elif delete_code == 'user':
        try:
            shutil.copyfile(r'root.json', r'root_SAVED.json')
            os.remove('root.json')
            print('User succesfully deleted')
        except:
            pass
        finally:
            second_command()
    elif delete_code == 'me':
        with open('config.json', mode='r') as f:
            data = json.load(f)
            VERSION = data['version']
        with open('config.json', mode='w') as f:
            dict = {}
            dict['version'] = VERSION
            json.dump(dict, f)
        os.remove(r'why.txt')
        os.remove('host.json')
        print('Your info was cleared')
    elif delete_code == 'logs':
        try:
            with open('log.txt') as f:
                data = json.load(f)
            with open('connection_log.txt') as f:
                data = json.load(f)
            os.remove(r'log.txt')
            os.remove(r'connection_log.txt')
            print('Logs succefully cleared')
        except:
            pass
    else:
        print('Command is not searched. Please, try again')
        second_command()

def show():
    show_code = input('$show: ')
    if show_code == 'docs':
        webbrowser.open('http://scgofficial.esy.es/UsefulDB/')
    elif show_code == 'all_files':
        path = os.getcwd()
        os.listdir(path)
    else:
        print('Command is not searched. Please, try again')

def fw_help():
    print('Creating:\n'
          + 'create.user.params(name, password, confirm)\n'
          + 'create.table.params(name, columns)\n'
          + 'create.database.params(name)\n'
          + 'Deleting:\n'
          + 'delete.user.params(name, password, confirm, save)\n'
          + 'delete.table.params(name, confirm)\n'
          + 'delete.database.params(name, confirm)\n'
          + 'For get more information, open documentation')