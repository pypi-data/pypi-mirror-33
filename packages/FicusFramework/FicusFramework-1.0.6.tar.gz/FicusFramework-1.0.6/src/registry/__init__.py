"""
yml文件注册功能
"""
import os

import yaml


def read_yaml_file(file, yaml_name: str):
    """
    读取文件路径中的yaml文件
    :param yaml_name:
    :return:
    """
    # 获取当前文件路径
    filePath = os.path.dirname(file)

    # 获取配置文件的路径
    yamlPath = os.path.join(filePath, yaml_name)

    if not os.path.exists(yamlPath):
        # 如果文件不存在,忽略
        return None

    # 加上 ,encoding='utf-8'，处理配置文件中含中文出现乱码的情况。
    f = open(yamlPath, 'r', encoding='utf-8')

    cont = f.read()

    # 返回yaml文件对象
    return yaml.load(cont)
