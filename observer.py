import re
import sysv_ipc
import verification
import logging


def observer(memory_key):
    logging.info('Observer starts')
    input = 0
    memory = sysv_ipc.SharedMemory(memory_key)
    memory.attach()
    while True:
        res = re.match(r'.+\s',memory.read())
        if res:
            temp = res.group()
            if (temp != input) & (temp != 'nil\n'):
                input = temp
                verification.verify(input.rstrip('\n'))