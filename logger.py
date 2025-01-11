import os
import datetime
from settings import log_dir_absolute

def print_error(message):
    os.makedirs(log_dir_absolute, exist_ok=True)
    file_name = str(datetime.datetime.now()).replace(':', '-')

    with open(file=os.path.join(log_dir_absolute, file_name+'.log'), mode='a', encoding='utf-8') as f:
        f.write(f'{str(datetime.datetime.now())}\t{message}\n')