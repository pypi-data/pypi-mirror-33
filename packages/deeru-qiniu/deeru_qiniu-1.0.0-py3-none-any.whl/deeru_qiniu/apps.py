from django.apps import AppConfig


class DeeruQiniuConfig(AppConfig):
    name = 'deeru_qiniu'

    # 下面几项暂时没用

    # 类型
    deeru_type = 'plugin'

    # 别名，插件、主题列表中显示的名字
    nice_name = '七牛自动上传插件'

    url = ''

    author = 'gojuukaze'

    description = '七牛自动上传插件'

    def ready(self):
        # signals are imported, so that they are defined and can be used
        import deeru_qiniu.signals
