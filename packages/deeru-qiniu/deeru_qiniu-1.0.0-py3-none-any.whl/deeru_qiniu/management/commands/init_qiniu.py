from django.core.management import BaseCommand

from app.app_models.config_model import Config
from deeru_qiniu.consts import deeru_qiniu_config


class Command(BaseCommand):
    """
    初始化
    python manage.py init_qiniu
    """

    def handle(self, *args, **options):
        base_config = {'access_key': input('输入七牛Access_Key：'),
                       'secret_key': input('输入七牛Secret_Key：'),
                       'bucket_name': input('输入七牛空间名：'),
                       'media_pre': input('媒体文件url前缀：'),
                       'static_pre': input('静态文件url前缀：')
                       }

        try:
            config = Config.objects.create(name=deeru_qiniu_config['qiniu'], config=str(base_config))
        except:
            config = Config.objects.get(name=deeru_qiniu_config['qiniu'])
            config.config = str(base_config)

        config.save()
