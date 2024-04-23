# Test Only, this also can be added in k series

end_of_object_found = False
start_check_end_of_obj = False
is_greater_or_lesser = 1

with open('LNL+T4+2230+CNVio3.dcfx', 'r') as f_in, open('modified_text_file.dcfx', 'w') as f_out:
    # 逐行读取原始文件

    new_names_g_5v = ['1234','5678', 'kezhao']
    new_names_l_5v = ['1111', '2222', 'jjj']
    for line in f_in:
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

            f_out.write(line)
            pass
        # 查找需要添加元素的位置
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
            # 在找到的位置插入新元素

        else:
            # 将原始行写入目标文件
            f_out.write(line)

        last_line = line

exit()

import xml.etree.ElementTree as ET

# 解析XML文件
tree = ET.parse('LNL+T4+2230+CNVio3.xml')
root = tree.getroot()


def iterate_elements(element, level, max_level):
    if level > max_level:
        return

    for child in element:
        if level == max_level:
            print(f"Element at level {level}: {child.tag}")
            altname = child.get('AltName')
            name = child.get('Name')
            print(altname)
            print(name)
            if altname is not None and name is not None:
                if "lnl_m_rvp1_erb_fab1" in altname and "VOLTAGE>5V" in altname and "VOLTAGE>5V" in name:
                    # 创建新的member元素
                    new_member = ET.Element('member')
                    new_member.set('Kind', 'Net')
                    new_member.set('Name', 'kezhao')

                    # 将新的member元素添加到<object>下
                    child.append(new_member)
                    break

        iterate_elements(child, level + 1, max_level)

def remove_namespace(tree):
    for elem in tree.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]  # 移除命名空间前缀
    return tree

iterate_elements(root, 1, 7)
tree = remove_namespace(tree)
#tree.write('modified_xml_file.xml', encoding="UTF-8")

'''
with open('modified_xml_file.xml', 'w') as f:
    f.write('<?xml version="1.0" encoding="UTF-8"? standalone="no" ?>\n')
    f.write(ET.tostring(root, encoding='unicode'))
'''

#exit()

for child in root:
    # 第二层节点的标签名称和属性
    print(child.tag,":", child.attrib)
    # 遍历xml文档的第三层
    for children in child:
        # 第三层节点的标签名称和属性
        print('     [children]:' + children.tag, ":", children.attrib)
        for sub_children in children:
            print('          [sub-children]:' + sub_children.tag, ":", sub_children.attrib)
            for ss_children in sub_children:
                print('             [s-sub-children]:' + ss_children.tag, ":", sub_children.attrib)
                for sss_children in ss_children:
                    print('                 [ss-sub-children]:' + sss_children.tag, ":", sss_children.attrib)
                    altname = sss_children.get('AltName')
                    name = sss_children.get('Name')
                    if altname == "@lnl_m_rvp1_erb_fab1.lnl_m_rvp1_erb_fab1(sch_1):\\VOLTAGE>5V\\" and name == "VOLTAGE>5V":
                        # 创建新的member元素
                        new_member = ET.Element('member')
                        new_member.set('Kind', 'Net')
                        new_member.set('Name', '+abcd')

                        # 将新的member元素添加到<object>下
                        child.append(new_member)
                        break
                    print(altname)
                    print(name)

tree.write('modified_xml_file.xml')


'''
# 检查root是否为None
if root is not None:
    # 遍历每个<object>元素
    objects = root.iter("object")
    if objects is not None:
        for obj in objects:
            print(obj)
            altname = obj.get('AltName')
            name = obj.get('Name')

            # 检查altname和name是否符合要求
            if altname == "@lnl_m_rvp1_erb_fab1.lnl_m_rvp1_erb_fab1(sch_1):\\VOLTAGE>5V\\" and name == "VOLTAGE>5V":
                # 创建新的member元素
                new_member = ET.Element('member')
                new_member.set('Kind', 'Net')
                new_member.set('Name', '+abcd')

                # 将新的member元素添加到<object>下
                obj.append(new_member)

    # 将修改后的XML数据写回到文件中
    tree.write('modified_xml_file.xml')
else:
    print("Root节点为None，无法解析XML文件。")
    
    '''

'''
import xml.etree.ElementTree as ET

tree = ET.parse("LNL+T4+2230+CNVio3.dcfx")
root = tree.getroot()
#print(root.tag, ":", root.attrib)  # 打印根元素的tag和属性

# 遍历每个<object>元素
for obj in root.find("cft:dir-objects"):
    altname = obj.get('AltName')
    name = obj.get('Name')

    print(altname)
    print(name)
    # 检查altname和name是否符合要求
    if "lnl_m_rvp1_erb_fab1" in altname and "VOLTAGE>5V" in altname and "VOLTAGE>5V" in name:
    # if altname == "@lnl_m_rvp1_erb_fab1.lnl_m_rvp1_erb_fab1(sch_1):\VOLTAGE>5V\\" and name == "VOLTAGE>5V":
        # 创建新的member元素
        new_member = ET.Element('member')
        new_member.set('Kind', 'Net')
        new_member.set('Name', 'kezhao')

        # 将新的member元素添加到<object>下
        obj.append(new_member)

# 将修改后的XML数据写回到文件中
tree.write('modified_xml_file.xml')
'''

'''
# 遍历xml文档的第二层
for child in root:
    # 第二层节点的标签名称和属性
    print(child.tag,":", child.attrib) 
    # 遍历xml文档的第三层
    for children in child:
        # 第三层节点的标签名称和属性
        print('     [children]:' + children.tag, ":", children.attrib)
        for sub_children in children:
            print('          [sub-children]:' + sub_children.tag, ":", sub_children.attrib)

'''