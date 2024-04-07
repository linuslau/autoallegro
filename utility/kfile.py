from utility.klogger import KLogger
import re

klogger = KLogger()
logger = klogger.getlog()


class KFile(object):

    def __init__(self, file_name):
        self.file_name = file_name
        pass

    def __del__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def replace(self, old_values, new_values, case_sensitive=False):
        f = open(self.file_name, 'r')
        all_lines = f.readlines()
        f.close()
        f = open(self.file_name, 'w+')

        if case_sensitive:
            for idx, line in enumerate(all_lines):
                for old_value, new_value in zip(old_values, new_values):
                    line_new = re.sub(old_value, new_value, line)
                f.writelines(line_new)
        else:
            for idx, line in enumerate(all_lines):
                for old_value, new_value in zip(old_values, new_values):
                    check_upper = old_value.upper()
                    line_upper = line.strip().upper()
                    insensitive_check = re.compile(re.escape(old_value), re.IGNORECASE)
                    if check_upper in line_upper:
                        line = insensitive_check.sub(new_value, line)
                        pass
                    else:
                        pass
                f.write(line)

        f.close()
        return
