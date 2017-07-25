import os
import sys

null = open(os.devnull, 'w')
stdout = sys.stdout

def enable():
    sys.stdout = stdout

def disable():
    sys.stdout = null