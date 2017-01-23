import sync
import consolecapture
import qrcapture
import observer
import sysv_ipc
import threading
import logging
from multiprocessing import Process

server = 'https://somesite.com'
logging.basicConfig(filename='acquisitor.log',level=logging.INFO)
logging.info('Script starts')
memory_key = 880041
memory = sysv_ipc.SharedMemory(memory_key, flags = sysv_ipc.IPC_CREAT, mode = 0600, size = sysv_ipc.PAGE_SIZE)

webcam = Process(target=qrcapture.usb_cam, args=(memory_key,))
observer = Process(target=observer.observer, args=(memory_key,))
synchro = Process(target=sync.sync, args=(memory_key,server))

synchro.start()
webcam.start()
observer.start()