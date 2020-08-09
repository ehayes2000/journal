import base64
import re
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
        self.is_valid_key = False
        self.key = key
        # self.journal = [(date_0, entry_0), ..., (date_n, entry_n)]
        # must be initialized by _load_to_search()
        self.journal = None

    # Decrypt the old data
    # Get a new entry from the user and add it to the old data
    # Write all data back to file encrypted
    def new_entry(self):
        f = Fernet(self.key)

        file = open(self.file, 'rb')
        old_entries = file.read()
        file.close()

        try:
            old_entries = f.decrypt(old_entries).decode()
        except:
            old_entries = ''

        now = datetime.now()
        time_stamp = f'{now.month}/{now.day}/{now.year} {now.hour}:{now.minute}\n'
        old_entries += '\n\n\n' + time_stamp

        print('    ' + '_' * 80)
        usr_inpt = self.get_long_input()
        if usr_inpt:
            old_entries += '\n' + usr_inpt
            old_bytes = old_entries.encode()
            self._write(old_bytes)

    # Given an encoded message, encrypt it and write it to file
    def _write(self, message):
        f = Fernet(self.key)
        file = open(self.file, 'wb')
        file.write(f.encrypt(message))
        file.close()

    # Decrypt entire file and print it
    def read_all(self):
        f = Fernet(self.key)
        file = open(self.file, 'rb')
        data = file.read()
        file.close()
        print(f.decrypt(data).decode())

    # set a key and check if it is a valid key for the set file
    def set_key(self, key):
        print('setting key... ')
        self.key = key
        if self._is_valid_key():
            self.is_valid_key = True
        else:
            self.is_valid_key = False

    # check if a set key is valid for a set file
    def _is_valid_key(self):
        print('validating key... ')
        f = Fernet(self.key)
        try:
            file = open(self.file, 'rb')
            file.close()
        except FileNotFoundError:
            print('file created')
            file = open(self.file, 'w')
            file.close()
            return True
        try:

            with open(self.file, 'rb') as file:
                encrypted_data = file.read()
                decrypted_data = f.decrypt(encrypted_data)
                return True
        except:
            return False

    # print list of dates and give user option to view entry corresponding
    # to date
    def search(self):
        self._load_to_search()
        for i in range(len(self.journal)):
            print(f'{i+1}. {self.journal[i][0]}')
        try:
            usr_inpt = int(input('>>> '))
            return self.journal[i - 1][1]
        except:
            print('Invalid Input')

    # decrypt all entries in the file and sort them by date into a list of tuples
    # (date, entry)
    def _load_to_search(self):
        f = Fernet(self.key)
        date = re.compile('[0-9]{1,2}/[0-9]{1,2}/[0-9]{4} [0-9]{1,2}:[0-9]{1,2}')
        file = open(self.file, 'rb')
        data = file.read()
        file.close()
        decrypted = f.decrypt(data).decode()
        dates = re.findall(date, decrypted)
        entries = re.split(date, decrypted)
        self.journal = list(zip(dates, entries[1:]))


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
        print('1. Write')
        print('2. Read')
        print('3. Exit')
        usr_inpt = input('>>> ')
        if usr_inpt == '1':
            print('Writing: ')
            j.new_entry()
        elif usr_inpt == '2':
            print('1. View All')
            print('2. Search Entry')
            usr_inpt = input('>>> ')
            if usr_inpt == '1':
                print('_' * 80)
                j.read_all()
                print('_' * 80)
            elif usr_inpt == '2':
                print('_' * 80)
                print(j.search())
                print('_' * 80)
        elif usr_inpt == '3':
            break
        else:
            print('Invalid Input')


main()
