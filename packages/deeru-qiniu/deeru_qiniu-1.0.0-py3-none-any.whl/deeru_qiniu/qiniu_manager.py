# -*- coding:utf-8 -*-
import os
from ast import literal_eval
from hashlib import md5
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles.finders import get_finders
from qiniu import Auth, put_file, BucketManager, build_batch_stat, build_batch_delete
from app.app_models.config_model import Config
from deeru_qiniu.consts import deeru_qiniu_config


def get_qiniu_config():
    try:
        return getattr(settings, 'QINIU')
    except:
        config = Config.objects.get(name=deeru_qiniu_config['qiniu'])
        return literal_eval(config.cache)


def upload_img(img, type='media'):
    """
    上传img

    :return:
    """

    config = get_qiniu_config()

    # 七牛上传数据的凭证
    token = Auth(config['access_key'], config['secret_key']).upload_token(config['bucket_name'])
    if type == 'media':
        pre = config.get('media_pre', '')
    else:
        pre = config.get('static_pre', '')
    key = '%s/%s' % (pre, img.name)
    ret, info = put_file(token, key, img.path)
    if info.status_code == 200 and ret['key'] == key:
        return True
    else:
        return False


def upload_file(file_path, name, type='media'):
    """

    :param name:
    :param file_path: Path
    :param type:
    :return:
    """
    config = get_qiniu_config()

    # 七牛上传数据的凭证
    token = Auth(config['access_key'], config['secret_key']).upload_token(config['bucket_name'])
    if type == 'media':
        pre = config.get('media_pre', '')
    else:
        pre = config.get('static_pre', '')
    key = '%s/%s' % (pre, name)
    ret, info = put_file(token, key, file_path)
    if info.status_code == 200 and ret['key'] == key:
        return True
    else:
        return False


def delete_files(keys=None):
    """
    批量删除
    :param keys:
    :return:
    """
    if keys is None:
        keys = []
    config = get_qiniu_config()

    # 七牛上传数据的凭证
    q = Auth(config['access_key'], config['secret_key'])
    bucket = BucketManager(q)
    ops = build_batch_delete(config['bucket_name'], keys)
    ret, info = bucket.batch(ops)
    if info.status_code == 200:
        return True
    else:
        print(ret)
        return False


def get_static_files():
    for finder in get_finders():
        for path, storage in finder.list([]):
            yield path
