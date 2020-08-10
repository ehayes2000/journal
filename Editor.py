# A class to edit text through the command line
# functionality:
# 1. allow user to give and edit multiple lines of input
# 2. edit an existing document or string
# 3.
import os
class Editor:
    def __init__(self, extension='txt'):
        self.extension = extension

    # use vim to create a file and get input form the user in that file
    # read data out of that file
    # delete the file
    # return the data from the file as a string
    def get_long_input(self):
        os.system(f'touch _.{self.extension}')
        os.system(f'vim _.{self.extension}')
        file = open(f'_.{self.extension}', 'r')
        out_str = ''.join(file.readlines())
        file.close()
        os.remove(f'_.{self.extension}')
        return out_str

    # takes a string as an input
    # allows user to edit the string then returns the edited string
    def edit(self, in_str):
        file = open(f'_.{self.extension}', 'w+')
        file.write(in_str)
        file.close()
        os.system(f'vim _.{self.extension}')
        file = open(f'_.{self.extension}', 'r')
        out_str = ''.join(file.readlines())
        os.remove(f'_.{self.extension}')
        return out_str
