
import threading,multiprocessing
from django.conf import settings
from .time_plus import DatetimePlus
from .func_plus import FuncHelper

class LocalAccessLog(object):
    write_log_process = None
    local_access_log_instance = None

    @staticmethod
    def write(content):
        if LocalAccessLog.local_access_log_instance is None:
            LocalAccessLog.local_access_log_instance = LocalAccessLog()
            LocalAccessLog.local_access_log_instance.queue.put('LocalAccessLog create')

        if not LocalAccessLog.local_access_log_instance.write_log_process.is_alive():
            LocalAccessLog.local_access_log_instance = LocalAccessLog()
            LocalAccessLog.local_access_log_instance.queue.put('LocalAccessLog re_create')

        LocalAccessLog.local_access_log_instance.queue.put(content)

    def write_to_file(self,log_recv):
        thread = threading.current_thread()
        while True:
            logstr = log_recv.get()
            logstr = DatetimePlus.get_now_only_time_to_str() + '\t' + logstr
            filename = self.get_log_file_name()
            with open(filename, 'a') as f:
                f.write(logstr + '\r\n')

    def __init__(self):
        queue = multiprocessing.Queue()
        self.queue = queue
        self.write_log_process = threading.Thread(target=self.write_to_file, args=(queue,))
        self.write_log_process.daemon = True
        self.write_log_process.start()

    def get_log_file_name(self):
        self.create_log_file_path()
        date_str = DatetimePlus.get_nowdate_to_str()
        filename = settings.SWEET_ACCESS_LOG_FILE_PATH + date_str + '_' + '.log'
        return filename

    def create_log_file_path(self):
        if not FuncHelper.check_directory_exists(settings.SWEET_ACCESS_LOG_FILE_PATH):
            FuncHelper.create_dirs(settings.SWEET_ACCESS_LOG_FILE_PATH)
