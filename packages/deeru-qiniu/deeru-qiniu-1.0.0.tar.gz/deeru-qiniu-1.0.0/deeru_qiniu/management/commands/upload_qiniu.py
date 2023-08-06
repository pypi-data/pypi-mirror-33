import os

from django.conf import settings
from django.core.management import BaseCommand

from app.app_models.other_model import Album
from deeru_qiniu.qiniu_manager import get_static_files, upload_file


class Command(BaseCommand):
    """
    上传文件到七牛
    python manage.py upload_qiniu
    """

    def add_arguments(self, parser):
        parser.description = '''上传媒体文件、静态文件到七牛'''

        parser.add_argument('--type',
                            default='media',
                            choices=['media', 'static'],
                            dest='type',
                            help='类型')

    def handle(self, *args, **options):
        self.type = options['type']

        if self.type == 'media':
            for a in Album.objects.all():
                a.save()
        elif self.type == 'static':
            for name in get_static_files():
                print(name)
                upload_file(os.path.join(settings.STATIC_ROOT, name),name, type='static')
