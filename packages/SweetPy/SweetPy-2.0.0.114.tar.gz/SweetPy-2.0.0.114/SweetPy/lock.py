import os
import multiprocessing

if os.name == 'nt':
    import win32con, win32file, pywintypes
    LOCK_EX = win32con.LOCKFILE_EXCLUSIVE_LOCK
    LOCK_SH = 0  # The default value
    LOCK_NB = win32con.LOCKFILE_FAIL_IMMEDIATELY
    __overlapped = pywintypes.OVERLAPPED()
elif os.name == 'posix':
    from fcntl import LOCK_EX, LOCK_SH, LOCK_NB
else:
    print("File Locker only support NT and Posix platforms!")

class LockPlus(object):
    file = open('self.lock', "a+")
    def lock(self):
        if os.name == 'nt':
            hfile = win32file._get_osfhandle(LockPlus.file.fileno())
            win32file.LockFileEx(hfile, LOCK_EX, 0, 0xffff0000, __overlapped)
        elif os.name == 'posix':
            fcntl.flock(LockPlus.file.fileno(), LOCK_EX)

    def unlock(self):
        if os.name == 'nt':
            hfile = win32file._get_osfhandle(LockPlus.file.fileno())
            win32file.UnlockFileEx(hfile, 0, 0xffff0000, __overlapped)
        elif os.name == 'posix':
            fcntl.flock(LockPlus.file.fileno(), fcntl.LOCK_UN)


