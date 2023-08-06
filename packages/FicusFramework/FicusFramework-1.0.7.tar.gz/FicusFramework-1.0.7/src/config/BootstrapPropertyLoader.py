import logging
import config

log = logging.getLogger('BootstrapPropertyLoader')


def load_properties_after_started(app, eureka_client):
    """
    加载配置文件  bootstrap.yml
    :param app:
    :param eureka_client:
    :return:
    """
    # 1. 获取yaml文件
    if not init_from_yaml_property(app):
        return

    # 这里开始尝试访问cloud-config获取配置文件
    server_url = _find_server_config_url(eureka_client)

    if server_url is None:
        return

    # region 发起请求 获取配置,并设置到 annotation.REMOTE_YML_CONFIG 中
    try:
        import requests
        r = requests.get(f"{server_url}{config.config_name}-{config.config_profile}.yml")
        r.raise_for_status()
        if len(r.content) > 0:
            from config import annotation
            import yaml
            annotation.REMOTE_YML_CONFIG = yaml.load(r.content)
        else:
            from api.exceptions import ServiceInnerException
            raise ServiceInnerException(f"cloud-config服务没有 {config.config_name}-{config.config_profile}.yml 配置")
    except requests.exceptions.ConnectionError or requests.exceptions.Timeout:
        if config.config_fail_fast:
            from api.exceptions import ServiceNoInstanceException
            raise ServiceNoInstanceException("cloud-config服务没有启动,系统启动失败")
        else:
            # 如果不快速失败,就直接返回
            return
    # endregion


def init_from_yaml_property(app):
    """
    读取本地的配置文件
    :param app:
    :return:
    """
    from registry import read_yaml_file
    yml = read_yaml_file(app, "bootstrap.yml")
    if yml is None:
        # 说明没有yml文件,不进行注册处理
        log.info("没有配置bootstrap.yml,采用默认的配置信息")
        return False

    # 说明有yml文件,开始进行处理

    # 第一个: server.port
    if "server" in yml and "port" in yml["server"]:
        config.server_port = yml["server"]["port"]
    try:
        config.config_name = yml["spring"]["cloud"]["config"]["name"]
    except:
        pass

    try:
        config.config_profile = yml["spring"]["cloud"]["config"]["profile"]
    except:
        pass

    try:
        config.config_server_id = yml["spring"]["cloud"]["config"]["discovery"]["service-id"]
    except:
        pass

    try:
        config.config_fail_fast = yml["spring"]["cloud"]["config"]["fail-fast"]
    except:
        pass

    try:
        config.application_name = yml["spring"]["application"]["name"]
    except:
        pass

    try:
        config.eureka_default_zone = yml["eureka"]["client"]["service-url"]["defaultZone"]
    except:
        pass

    return True


def _find_server_config_url(eureka_client):
    """
    获取server_config的服务地址
    :param eureka_client:
    :return:
    """
    app = eureka_client.get_app(config.config_server_id)
    from client.FicusServerGetter import FicusServerGetter
    # 找到cloud - config的服务地址
    server_getter = FicusServerGetter(server_id=config.config_server_id)

    if app is None or len(app["application"]["instance"]) == 0 or server_getter.server_url is None:
        # 说明配置服务没有启动,那么根据配置,决定是否抛错
        if config.config_fail_fast:
            from api.exceptions import ServiceNoInstanceException
            raise ServiceNoInstanceException("cloud-config服务没有启动,系统启动失败")
        else:
            # 如果不快速失败,就直接返回
            return None

    return server_getter.server_url
