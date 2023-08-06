from django.core.management import BaseCommand

from app.app_models.config_model import Config
from app.app_models.other_model import Album
from deeru_qiniu.consts import deeru_qiniu_config
from deeru_qiniu.qiniu_manager import get_qiniu_config, delete_files, get_static_files


class Command(BaseCommand):
    """
    删除文件
    python manage.py delete_qiniu
    """

    def add_arguments(self, parser):
        parser.description = '''删除七牛上的全部媒体文件或静态文件'''

        parser.add_argument('--type',
                            default='media',
                            choices=['media', 'static'],
                            dest='type',
                            help='类型')

    def handle(self, *args, **options):
        self.type = options['type']
        config = get_qiniu_config()
        if self.type == 'media':
            pre = config.get('media_pre', '')
            keys = []
            for a in Album.objects.all():
                keys.append('%s/%s' % (pre, a.img.name))
            print(keys)
            delete_files(keys)

        elif self.type == 'static':
            keys = []
            pre = config.get('static_pre', '')
            for name in get_static_files():
                keys.append('%s/%s' % (pre, name))
            delete_files(keys)

