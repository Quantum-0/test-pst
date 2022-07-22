""" Example main file """
from time import sleep
import os
from another_file import HELLO_WORLD_STRING, time

if __name__ == '__main__':
    assert os.environ['TEST_ENV'] == '1'
    while True:
        print(HELLO_WORLD_STRING)
        sleep(time())
