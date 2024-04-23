from utility.klogger import KLogger
import re
import os

klogger = KLogger()
logger = klogger.getlogger()


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

    def is_same_file(file1, file2):
        norm_file1 = os.path.normpath(file1)
        norm_file2 = os.path.normpath(file2)

        return norm_file1 == norm_file2

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

    # dcfx file is almost the same as xml format, initially, intended to use ElementTree to do addition,
    # finally failed because while write back to file, the format changes a little bit for almost every line.
    # so drop it and just handle pure text instead
    def add_netnames_vs_5V(self, g_5v_pattern_names, l_5v_pattern_names):

        new_names_g_5v = []
        new_names_l_5v = []
        # to avoid duplication
        net_names_g_5v, net_names_l_5v = self.get_current_net_names_g_l_5v()
        g_5v_reg_names, l_5v_reg_names = self.convert_pattern_to_regular(g_5v_pattern_names, l_5v_pattern_names)

        with open(self.file_name, 'r') as f_in:
            for line in f_in:
                if 'AltName="' in line and ' Name="' in line:
                    #get real net name xxx from ' Name="xxx"'
                    real_net_name = line.split(' Name="')[1].split('"')[0]

                    for pattern in g_5v_reg_names:
                        if re.match(pattern, real_net_name) and real_net_name not in net_names_g_5v:
                            new_names_g_5v.append(real_net_name)

                    for pattern in l_5v_reg_names:
                        if re.match(pattern, real_net_name) and real_net_name not in net_names_l_5v:
                            new_names_l_5v.append(real_net_name)

        self.add_to_file(new_names_g_5v, new_names_l_5v)
    def add_to_file(self, new_names_g_5v, new_names_l_5v):
        end_of_object_found = False
        start_check_end_of_obj = False
        is_greater_or_lesser = 1

        with open(self.file_name, 'r') as f_in:
            all_lines = f_in.readlines()

        with open(self.file_name, 'w') as f_out:
            for line in all_lines:
                if start_check_end_of_obj is True:
                    if '</object>' in line:
                        end_of_object_found = True
                        start_check_end_of_obj = False

                if end_of_object_found is True:
                    end_of_object_found = False
                    if is_greater_or_lesser:
                        new_names = new_names_g_5v
                    else:
                        new_names = new_names_l_5v

                    for new_name in new_names:
                        start_index = last_line.find('Name="') + len('Name="')
                        end_index = last_line.find('"', start_index)
                        original_name = last_line[start_index:end_index]

                        # 替换 Name 属性值为新的值
                        new_line = last_line.replace(original_name, new_name)
                        f_out.write(new_line)
                        pass
                    pass

                if 'AltName="' in line and ' Name="' in line:
                    # 提取 AltName 属性值
                    altname_start_index = line.find('AltName="') + len('AltName="')
                    altname_end_index = line.find('"', altname_start_index)
                    altname = line[altname_start_index:altname_end_index]

                    # 提取 Name 属性值
                    name_start_index = line.find(' Name="') + len(' Name="')
                    name_end_index = line.find('"', name_start_index)
                    name = line[name_start_index:name_end_index]

                    # 检查 AltName 和 Name 属性值是否都包含 VOLTAGE>5V
                    if 'VOLTAGE>5V' in altname and 'VOLTAGE>5V' in name:
                        print("AltName and Name both contain 'VOLTAGE>5V'")
                        start_check_end_of_obj = True
                        is_greater_or_lesser = 1

                    if '+V' in altname and 'VOLTAGE&lt;5V' in name:
                        print("AltName and Name both contain 'VOLTAGE<5V'")
                        start_check_end_of_obj = True
                        is_greater_or_lesser = 0

                    f_out.write(line)

                else:
                    f_out.write(line)

                last_line = line


    def get_current_net_names_g_l_5v(self):

        net_names_g_5v = []
        net_names_l_5v = []

        start_check_end_of_obj = False
        is_greater_or_lesser = 1

        with open(self.file_name, 'r') as f_in:
            for line in f_in:
                if start_check_end_of_obj is True:
                    if '</object>' in line:
                        start_check_end_of_obj = False
                        continue

                    if 'Kind="' not in line and 'Name="' not in line:
                        continue

                    if is_greater_or_lesser:
                        name = line.split('Name="')[1].rstrip('"/>')
                        net_names_g_5v.append(name)
                        pass
                    else:
                        name = line.split('Name="')[1].rstrip('"/>')
                        net_names_l_5v.append(name)
                        pass

                if 'AltName="' in line and ' Name="' in line:
                    # 提取 AltName 属性值
                    altname_start_index = line.find('AltName="') + len('AltName="')
                    altname_end_index = line.find('"', altname_start_index)
                    altname = line[altname_start_index:altname_end_index]

                    # 提取 Name 属性值
                    name_start_index = line.find(' Name="') + len(' Name="')
                    name_end_index = line.find('"', name_start_index)
                    name = line[name_start_index:name_end_index]

                    # 检查 AltName 和 Name 属性值是否都包含 VOLTAGE>5V
                    if 'VOLTAGE>5V' in altname and 'VOLTAGE>5V' in name:
                        print("AltName and Name both contain 'VOLTAGE>5V'")
                        start_check_end_of_obj = True
                        is_greater_or_lesser = 1

                    if '+V' in altname and 'VOLTAGE&lt;5V' in name:
                        print("AltName and Name both contain 'VOLTAGE<5V'")
                        start_check_end_of_obj = True
                        is_greater_or_lesser = 0

        return net_names_g_5v, net_names_l_5v


    def convert_pattern_to_regular(self, g_5v_pattern_names, l_5v_pattern_names):

        g_5v_reg_names = []
        l_5v_reg_names = []
        for pattern in g_5v_pattern_names:
            # user may input like *abc, abc*, *abc*, abc, clear * to get abc
            g_5v = re.sub(r'^\*|\*$', '', pattern)
            escaped_g_5v = re.escape(g_5v)
            if pattern.startswith("*") and pattern.endswith("*"):
                pattern = r'.*' + escaped_g_5v + r'.*'
            elif pattern.startswith("*") and not pattern.endswith("*"):
                pattern = r'.*' + escaped_g_5v + r'$'
            elif not pattern.startswith("*") and pattern.endswith("*"):
                pattern = r'^' + escaped_g_5v + r'.*'
            else:
                pattern = r'^' + escaped_g_5v + r'$'

            #print('pattern: ' + pattern)
            logger.info('g 5v pattern: %s' + pattern)
            g_5v_reg_names.append(pattern)

        for pattern in l_5v_pattern_names:
            # user may input like *abc, abc*, *abc*, abc, clear * to get abc
            name = re.sub(r'^\*|\*$', '', pattern)
            escaped_l_5v = re.escape(name)
            if pattern.startswith("*") and pattern.endswith("*"):
                pattern = r'.*' + escaped_l_5v + r'.*'
            elif pattern.startswith("*") and not pattern.endswith("*"):
                pattern = r'.*' + escaped_l_5v + r'$'
            elif not pattern.startswith("*") and pattern.endswith("*"):
                pattern = r'^' + escaped_l_5v + r'.*'
            else:
                pattern = r'^' + escaped_l_5v + r'$'

            #print('pattern: ' + pattern)
            logger.info('l 5v pattern: %s' + pattern)
            l_5v_reg_names.append(pattern)

        return g_5v_reg_names, l_5v_reg_names