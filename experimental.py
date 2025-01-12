import time
import pygame
from settings import *

print_real = print
internal_console = []
def print(*args, **kwargs):
    print_real(*args, **kwargs)
    sep = ' '
    if 'sep' in kwargs:
        sep = kwargs['sep']
    text = sep.join(map(str, args))
    if 'end' in kwargs:
        text += kwargs['end']
    if text.endswith('\n'):
        text = text[:-1]
    lines = text.split('\n')
    for l in lines:
        internal_console.append({'time': time.time(), 'text': l})

screen_exists = False
console_lines_erased = 0
last_console_len = 0
new_console_line = False
last_code = ''