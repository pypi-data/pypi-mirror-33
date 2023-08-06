"""
日志记录相关的操作
"""
import requests
from munch import Munch

from client.FicusServerGetter import ficusServerGetter
from api.exceptions import ServiceNoInstanceException, ServiceInnerException

__all__ = ["log_debug", "log_info", "log_warn", "log_error"]


def log_debug(message):
    """
    打印debug日志
    :param message: 日志记录
    :return:
    """
    if message is None:
        return

    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    _inner_request(message, "debug", log_debug)


def log_info(message):
    """
    打印info日志
    :param message: 日志记录
    :return:
    """
    if message is None:
        return

    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    _inner_request(message, "info", log_info)


def log_warn(message):
    """
    打印warn日志
    :param message: 日志记录
    :return:
    """
    if message is None:
        return

    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    _inner_request(message, "warn", log_warn)


def log_error(message):
    """
    打印error日志
    :param message: 日志记录
    :return:
    """
    if message is None:
        return

    if ficusServerGetter.server_url is None:
        # 说明ficus服务没有启动
        raise ServiceNoInstanceException("ficus服务没有找到可用的实例")

    _inner_request(message, "error", log_error)


def _inner_request(message, level, func):
    """
    构造请求,并发送
    :param message: 消息
    :param level: 级别
    :param func: 递归函数
    :return:
    """
    request = None
    if not isinstance(message, Munch):
        # 说明不是 Munch类型的 判断是否是Dict的
        if isinstance(message, dict):
            # 如果是dict类型的,直接发
            request = message
    else:
        # 说明是munch的,那么就转成Dict的
        request = message.toDict()
    try:
        r = requests.post(f"{ficusServerGetter.server_url}remote/hl-service/{level}", json=request)
        r.raise_for_status()
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        # 这里说明是网络连接失败
        ficusServerGetter.change_new_server()
        func(message)
    except requests.exceptions.HTTPError as e:
        if r.status_code == 500:
            # 说明服务器端报错了
            raise ServiceInnerException(r.content.decode('utf-8'))
        raise e
