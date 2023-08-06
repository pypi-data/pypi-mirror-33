from django.apps import AppConfig


class DeerUApiConfig(AppConfig):
    name = 'deeru_api'

    # 获取插件、主题的专业配置路径
    # deeru_config_context='deeru_api.consts.deeru_api_config_context'

    # 下面几项暂时没用

    # 类型
    deeru_type = 'plugin'

    # 别名，插件、主题列表中显示的名字
    nice_name = 'deeru-api'

    url = ''

    author = ''

    description = ''
