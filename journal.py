import base64
import re
import json
from Editor import Editor
from getpass import getpass
from os import urandom
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet
from datetime import datetime


class Journal(Editor):
    def __init__(self, file, key=None):
        super().__init__()
        self.file = file
        self.key = key
        self.is_valid_key = self._is_valid_key()
        # self.journal = [(date_0, entry_0), ..., (date_n, entry_n)]
        # must be initialized by _load_to_search()
        self.journal_dict = {}

    def _file_exists(self):
        try:
            file = open(self.file, 'r')
            file.close()
            return True
        except FileNotFoundError:
            return False

    def _is_valid_key(self):
        # if the key has not been set return False
        if self.key == None:

            self.is_valid_key = False
            return False
        # if the file does not exist then the key will be valid
        elif not self._file_exists():
            print('File Created')
            self.is_valid_key = True
            return True
        # if the key is not None and the file exists
        try:
            # if the key successfully decrypts the file return True
            f = Fernet(self.key)
            file = open(self.file, 'rb')
            encrypted_data = file.read()
            decrypted_data = f.decrypt(encrypted_data)
            file.close()
            self.is_valid_key = True
            return True
        except:
            self.is_valid_key = False
            return False

    def _load_journal_dict(self):
        if not self.is_valid_key or not self._file_exists():
            return False

        f = Fernet(self.key)
        file = open(self.file, 'rb')
        enc_data = file.read()
        dec_data = f.decrypt(enc_data)
        self.journal_dict = json.loads(dec_data.decode())
        file.close()
        return True
    
    def _save_journal_dict(self):
        if not self.journal_dict:
            return False
        f = Fernet(self.key)
        raw_data = json.dumps(self.journal_dict)
        encrypted_data = f.encrypt(raw_data.encode())
        file = open(self.file, 'wb')
        file.write(encrypted_data)
        file.close()
        return True

    def _view_formatted_entry(self, date_key, begin=''):
        print(begin, end='')
        print(len(date_key) * '_')
        print(date_key, end='\n\n')
        print(self.journal_dict[date_key])

    def _get_time_stamp(self):
        now = datetime.now()
        time_stamp = f'{now.month}/{now.day}/{now.year} {now.hour}:{now.minute}'
        return time_stamp

    def _select_date(self):
        if not self.journal_dict:
            return False

        dates = list(self.journal_dict.keys())
        for i in range(len(dates)):
            print(f'{i + 1}. {dates[i]}')

        while True:
            try:
                usr_inpt = int(input('>>> '))
                if usr_inpt > 0 and usr_inpt <= len(dates):
                    break
            except:
                print('Invalid Input')

        return dates[usr_inpt - 1]
 
    def set_key(self, key):
        self.key = key
        if self._is_valid_key():
            self._load_journal_dict()
            return True
        else:
            return False

    def new_entry(self):
        time_stamp = self._get_time_stamp()
        new_entry = self.get_long_input()
        if new_entry:
            self.journal_dict[time_stamp] = new_entry
            self._save_journal_dict()

    def view_entry(self):
        if not self.journal_dict:
            return False
        date = self._select_date()
        self._view_formatted_entry(date)

    # FIXME: doesn't show first entry when there are more than 1 entries
    def view_all_entries(self):
        journal = iter(self.journal_dict)
        first_date = next(journal)
        self._view_formatted_entry(first_date)

        for date in journal:
            self._view_formatted_entry(date, '\n\n')

    def edit_entry(self):
        if not self.journal_dict:
            return False
        date = self._select_date()
        edited_entry = self.edit(self.journal_dict[date])
        edited_entry += '\nEdited ' + self._get_time_stamp()
        self.journal_dict[date] = edited_entry
        self._save_journal_dict()

def hash_pass(password):
    password = password.encode()
    salt = b'N\xab\xfe\x92yv\x14\xd5\x1d\xeds\xdd\xad\x0e\x81\xc1'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=1000000,
        backend=default_backend())
    return base64.urlsafe_b64encode(kdf.derive(password))

def main():
    j = Journal('/home/eric/Code/Personal/test_journal')
    psswd = getpass('password: ')
    key = hash_pass(psswd)
    j.set_key(key)

    while not j.is_valid_key:
        print('Incorrect password. Try again.')
        psswd = getpass('password: ')
        key = hash_pass(psswd)
        j.set_key(key)

    while True:
        print('1. New Entry')
        print('2. Edit Entry')
        print('3. Read Entry')
        print('4. Exit')

        usr_inpt1 = input('>>> ')

        if usr_inpt1 == '1':
            j.new_entry()
        elif usr_inpt1 == '2':
            j.edit_entry()
        elif usr_inpt1 == '3':
            while True:
                print('1. Read All Entries')
                print('2. Lookup Entry')
                print('3. Main Menu')
                usr_inpt2 = input('>>> ')
                if usr_inpt2 == '1':
                    j.view_all_entries()
                    break
                elif usr_inpt2 == '2':
                    j.view_entry()
                    break
                elif usr_inpt2 == '3':
                    break
                else:
                    print('Invalid Input')
        elif usr_inpt1 == '4':
            print('Goodbye')
            break
        else:
            print('Invalid Input')

main()

