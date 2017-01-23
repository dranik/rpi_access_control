import sysv_ipc
import logging


def console(memory_key):
    logging.info('Console input starts')
    while True:
        result = raw_input('>')
        if result != '':
            memory = sysv_ipc.SharedMemory(memory_key)
            memory.attach()
            result = result + '\n'
            memory.write(result)