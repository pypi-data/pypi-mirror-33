# -*- coding:utf-8 -*-

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from app.app_models.other_model import Album
from deeru_qiniu.qiniu_manager import upload_img


@receiver(post_save, sender=Album, dispatch_uid="deeru_qiniu_album_post_save")
def article_pre_save(sender, **kwargs):
    img = kwargs['instance'].img
    try:
        upload_img(img)
    except:
        pass



