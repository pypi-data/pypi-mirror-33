from flask import Flask
from flask_cors import *

import config

app = Flask(__name__)
# 设置跨域
CORS(app, supports_credentials=True)

#读取本地配置文件
from config.BootstrapPropertyLoader import load_properties_after_started, init_from_yaml_property
init_from_yaml_property(__file__)

# 注册信息到eureka中
from eureka.client import EurekaClient

# 第一个参数即为注册到eureka中的服务名,要求sobey.开头, 只允许字母数字点号
ec = EurekaClient(config.application_name,
                  eureka_url=config.eureka_default_zone,
                  lease_renewal_interval_in_seconds=2,
                  lease_expiration_duration_in_seconds=6
                  )
# 发起服务注册以及心跳
ec.register("UP")
ec.start_heartbeat()

load_properties_after_started(__file__,ec)

# 这一行不能去掉,目的是引入flask的endpoints,并且位置需要在 app = Flask(__name__) 后面
# 引入views
from remote import remote

app.register_blueprint(remote, url_prefix='/')

# 程序启动后,判断是否需要注册执行器
from registry.LoadOnRegistryLoader import registry_after_started

registry_after_started(__file__, ec)
