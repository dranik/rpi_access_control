import os, select, subprocess
import sysv_ipc


def usb_cam(memory_key):
    memory = sysv_ipc.SharedMemory(memory_key)
    memory.attach()
    try:
        import RPi.GPIO
        args = ["zbarcam --nodisplay --raw -q --prescale=320x240"]
        p1 = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True, close_fds=True)
    except:
        args = ["LD_PRELOAD=/usr/lib/libv4l/v4l1compat.so zbarcam --nodisplay --raw -q --prescale=320x240"]
        p1 = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True, close_fds=True)
    while True:
        rlist, wlist, xlist = select.select([p1.stdout], [], [])
        for stdout in rlist:
            result = os.read(stdout.fileno(), 1024)
            if result != '':
                result = result + '\n'
                memory.write(result)