#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import os.path
import re
import shutil
import datetime

RequestType = 'RequestType'
ResponseType = 'ResponseType'
ModelType = 'ModelType'
RESULTS_DIR = 'parse_bjsc_results/'

BOOL = 'bool'
INT = 'int'
LONG = 'long'
DOUBLE = 'double'
STRING = 'string'
BINARY = 'binary'
BYTE = 'byte'
DECIMAL = 'decimal'
SHORT = 'short'
FLOAT = 'float'
DATETIME = 'datetime'
LIST = 'list'
MAP = 'map'

TYPE_MAP = {
    'bool': {
        'decorate': 'assign',
        'type': 'BOOL'
    },
    'int': {
        'decorate': 'assign',
        'type': 'NSInteger'
    },
    'long': {
        'decorate': 'assign',
        'type': 'long long'
    },
    'double': {
        'decorate': 'assign',
        'type': 'CGFloat'
    },
    'string': {
        'decorate': 'copy',
        'type': 'NSString'
    },
    'binary': {
        'decorate': 'assign',
        'type': 'NSInteger'
    },
    'byte': {
        'decorate': 'assign',
        'type': 'NSInteger'
    },
    'decimal': {
        'decorate': 'assign',
        'type': 'CGFloat'
    },
    'short': {
        'decorate': 'assign',
        'type': 'NSInteger'
    },
    'float': {
        'decorate': 'assign',
        'type': 'CGFloat'
    },
    'datetime': {
        'decorate': 'assign',
        'type': 'long long'
    },
    'list': {
        'decorate': 'copy',
        'type': 'NSArray'
    },
    'map': {
        'decorate': 'copy',
        'type': 'NSDictionary'
    }
}

def parse():
    if len(sys.argv) <= 1:
        print("没有指定目录或者文件")
        return
    #开始处理
    input = os.path.abspath(sys.argv[1])
    if os.path.isdir(input):
        #输入是一个目录
        _parse_dir(input)
    elif os.path.isfile(input):
        #输入是一个文件
        _parse_file(input)
    else:
        print("输入既不是合法路径")
        return

def _parse_dir(dir):
    #合并目录下所有文件
    file_names = os.listdir(dir)
    tmp_file = os.path.join(os.getcwd(), 'parse_bjsc_tmp.bjsc')
    file = open(tmp_file, 'w')
    for file_name in file_names:
        file_path = os.path.join(dir, file_name)
        suffix = os.path.splitext(file_path)[1]
        #忽略非bjsc文件
        if suffix != '.bjsc':
            continue
        #将每个文件内容合并
        for line in open(file_path):
            file.write(line)
        file.write('\n')
    file.close()
    #处理合并后的文件
    _parse_file(tmp_file)
    #删除临时文件
    os.remove(tmp_file)
    
def _parse_file(file):
    text = open(file).read()
    pattern = r"""
            class          ##以class开头
            \s+           ##中间间隔一个或者多个空字符
            (\w+)             ##类名
            \s*           ##间隔0个或者多个空字符
            \{              ##左括号
            ([^\}]*)         ##中间任意非}字符
            \}             ##右括号
    """
    regex = re.compile(pattern, re.VERBOSE|re.MULTILINE|re.DOTALL|re.IGNORECASE)
    #创建目录存放结果
    result_dir = os.path.join(os.getcwd(), RESULTS_DIR)
    #先清空文件夹，再重新创建
    if os.path.exists(result_dir):
        shutil.rmtree(result_dir)
    os.makedirs(result_dir)
    print('\n目录重新创建成功:\n' + result_dir)
    for m in regex.finditer(text):
        if m.group(1) and m.group(2):
            if RequestType in m.group(1):
                classType = RequestType   #request
                className = m.group(1).replace(RequestType, '')
            elif ResponseType in m.group(1):
                classType = ResponseType   #response
                className = m.group(1).replace(ResponseType, '')
            else:
                classType = ModelType   #model
                className = m.group(1)
            _parse_class(className, classType, m.group(2))
                 

def _parse_class(className, classType, content):
    print('\n======================\n')
    print('开始解析\nclass:' + className + '\n' + '类型:' + classType + '\n' + '内容:' + content)
    result_dir = os.path.join(os.getcwd(), RESULTS_DIR)
    lines = content.splitlines()
    property_list = []
    current_comments = []
    for line in lines:
        #去掉前后空字符
        strip_line = line.strip()
        prop_dict = _find_prop_dict(strip_line)
        if prop_dict:
            prop_type = prop_dict.get('type')
            if '.' in prop_type:
                continue
            #分号后面的注释
            tmp_idx = strip_line.find(';')
            tmp = ''
            if tmp_idx > 0:
                tmp = strip_line[tmp_idx+1:]
            if tmp:
                current_comments.append(tmp)
            comment_dict = {
                'comments': current_comments
            }
            prop_dict = dict(prop_dict.items() + comment_dict.items())
            property_list.append(prop_dict)
            #一个属性处理完毕
            current_comments = []
        else:
            current_comments.append(strip_line)
    
    _create_class(className, classType, property_list)
    

def _find_prop_dict(line):
    pattern = r'^\s*([\w+\.]*)\s*(<\w+>)?\s*(\w+)\s*;'
    regex = re.compile(pattern, re.VERBOSE|re.MULTILINE|re.DOTALL)
    for m in regex.finditer(line):
        if m.group(1) and m.group(3):
            return {
                'type': m.group(1),
                'name': m.group(3),
                'protocol': m.group(2).replace('<', '').replace('>', '') if m.group(2) else ''
            }
    return {}

def _create_class(className, classType, prop_list):
    file_name = _class_file_name(className, classType)
    h_path = _h_class_result_path(className, classType)
    m_path = _m_class_result_path(className, classType)
    if _check_and_clear_file_if_need(h_path, m_path):
        print('file:' + h_path + ' and ' + m_path + ' exists')
        return
    _create_h_class(className, classType, prop_list)
    _create_m_class(className, classType, prop_list)


def _create_m_class(className, classType, prop_list):
    file_name = _class_file_name(className, classType)
    m_path = _m_class_result_path(className, classType)
    #m文件
    m_file = open(m_path, 'w')
    #注释
    m_file.write('//\n//  '+file_name + '.m' + '\n//\n//  '+'created on '+datetime.datetime.now().strftime("%Y/%m/%d") + '\n//\n\n')
    m_file.write('#import "' + file_name + '.h"' + '\n\n')
    m_file.write('@implementation ' + file_name + '\n\n')

    if classType == RequestType:
        m_file.write('-(NSString*)getFuncKey {\n\t' + 'return @"xxx";' + '\n' + '}' + '\n\n')
        m_file.write('-(NSString *)getModelName {\n\t' + 'return @"'+_class_file_name(className, ResponseType) + '";' + '\n' + '}' + '\n\n')
        m_file.write('- (NSString *)requestServiceCode {\n\t' + 'return @"xxx";' + '\n' + '}' + '\n\n')
        m_file.write('+ (NSDictionary *)CTKeyMapperDictionary {\n\t'+'return @{\n\t\t')
        m_file.write(_prop_map_string(prop_list))
        m_file.write('\t};\n')
        m_file.write('}\n\n')
    elif classType == ResponseType:
        m_file.write('+ (JSONKeyMapper*)keyMapper {\n\t' + 'return [CTRespBase CTKeyMapperWithDictionary:@{\n\t\t')
        m_file.write(_prop_map_string(prop_list))
        m_file.write('\t}];\n')
        m_file.write('}\n\n')
    else:
        m_file.write('+ (JSONKeyMapper*)keyMapper {\n\t' + 'return [[JSONKeyMapper alloc] initWithDictionary:@{\n\t\t')
        m_file.write(_prop_map_string(prop_list))
        m_file.write('\t}];\n')
        m_file.write('}\n\n')

    m_file.write('@end')
    m_file.close()

def _create_h_class(className, classType, prop_list):
    file_name = _class_file_name(className, classType)
    h_path = _h_class_result_path(className, classType)
    h_file = open(h_path, 'w')
    super_class = ''
    if classType == RequestType:
        super_class = 'CTReqBase'
    elif classType == ResponseType:
        super_class = 'CTRespBase'
    else:
        super_class = 'JSONModel'
    #注释
    h_file.write('//\n//  '+file_name + '.h' + '\n//\n//  '+'created on '+datetime.datetime.now().strftime("%Y/%m/%d") + '\n//\n\n')
    h_file.write('#import "' + super_class + '.h"' + '\n')
    #引用其他类
    import_list = []
    for prop in prop_list:
        if prop['protocol'] and _is_model_type(prop['protocol']):
            if prop['protocol'] not in import_list:
                import_list.append(prop['protocol'])
        if _is_model_type(prop.get('type')):
            if prop.get('type') not in import_list:
                import_list.append(prop.get('type'))

    for import_type in import_list:
        h_file.write('#import "' + _class_file_name(import_type, ModelType) + '.h' + '"' + '\n')

    if classType == ModelType:
        h_file.write('\n@protocol ' + file_name + ';\n')
    #interface开始
    h_file.write('\n@interface ' + file_name + ' : ' + super_class + '\n\n')
    for prop in prop_list:
        comment = _merge_comments(prop['comments'])
        prop_type = prop['type']
        prop_name = prop['name']
        prop_protocol = prop['protocol']
        decorate = _decorate_symbol(prop_type)
        protocol = ('<'+_class_file_name(prop_protocol, ModelType)+'>') if _is_model_type(prop_protocol) else ''
        indicator = '' if decorate=='assign' else '*'
        line = '@property (nonatomic, ' + decorate + ')' + _class_type_name(prop_type) + protocol + ' ' + indicator + prop_name + ';' + '\n'
        if comment and len(comment)>0:
            h_file.write(comment) 
        h_file.write(line)
    #interface结束
    h_file.write('\n@end')
    h_file.close()

def _prop_map_string(prop_list):
    result = ''
    for index, prop in enumerate(prop_list):
            prop_name = prop['name']
            result += '\t\t@"'+prop_name+'"' + ': ' + '@"' + prop_name+'"'
            if index != len(prop_list) - 1:
                result += ','
            result += '\n\t\t'
    return result
    
def _is_model_type(prop_type):
    if not prop_type:
        return False
    config_map = TYPE_MAP.get(prop_type)
    if config_map:
        return False
    return True
    

def _decorate_symbol(prop_type):
    config_map = TYPE_MAP.get(prop_type)
    if config_map and config_map.get('decorate'):
        return config_map.get('decorate')
    return 'strong'

def _class_type_name(prop_type):
    config_map = TYPE_MAP.get(prop_type)
    if config_map and config_map.get('type'):
        return config_map.get('type')
    return _class_file_name(prop_type, ModelType)

def _merge_comments(comments):
    if not comments:
        return ''
    comments = [item for item in comments if len(item)>0]
    result = '/* '
    for index, comment in enumerate(comments):
        comment = comment.replace('/*', '').replace('*/', '').replace('//', '')
        if index > 0:
            comment = '   ' + comment.replace('/*', '') + '\n'
        result = result + comment
    result = result + '*/' + '\n'
    return result

def _check_and_clear_file_if_need(h_path, m_path):
    if os.path.exists(h_path) and os.path.exists(m_path):
        return True
    
    if os.path.exists(h_path):
        os.remove(h_path)
    if os.path.exists(m_path):
        os.remove(m_path)
    return False

def _h_class_result_path(className, classType):
    result_dir = os.path.join(os.getcwd(), RESULTS_DIR)
    file_name = _class_file_name(className, classType)
    return os.path.join(result_dir, file_name + '.h')

def _m_class_result_path(className, classType):
    result_dir = os.path.join(os.getcwd(), RESULTS_DIR)
    file_name = _class_file_name(className, classType)
    return os.path.join(result_dir, file_name + '.m')

def _class_file_name(className, classType):
    if classType == RequestType:
        return 'IBUReq' + className
    elif classType == ResponseType:
        return 'IBUResp' + className
    else:
        return 'IBUM' + className

parse()