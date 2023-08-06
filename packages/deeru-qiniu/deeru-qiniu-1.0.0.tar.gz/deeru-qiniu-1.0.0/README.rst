DeerU QINIU
=====================

DeerU七牛插件

安装
-----

.. code-block:: bash

    pip install deeru-qiniu

使用
----

1. 运行初始化命令

    .. code-block:: bash

        python manage.py init_qiniu

    根据提示进行配置，
    你也可以跳过此步，在admin的 "配置" 中添加名为 "七牛配置" 的配置，配置内容为：

    .. code-block:: python

        {
            'access_key': 'access_key',
            'secret_key': 'secret_key',
            'bucket_name': '空间名',
            'media_pre':'媒体文件前缀（可为空）',
            'static_pre': '静态文件前缀（可为空）'
        }

    或是在 ``settings_local.py`` 中添加如下配置：

    .. code-block:: python

        QINIU = {
                'access_key': 'access_key',
                'secret_key': 'secret_key',
                'bucket_name': '空间名',
                'media_pre':'媒体文件前缀（可为空）',
                'static_pre': '静态文件前缀（可为空）'
                }

    .. note::

        运行时优先读取 ``settings_local.py`` 中的配置，没有再读取admin中的

2. 修改settings

    在 ``settings_local.py`` 的 `CUSTOM_APPS` 中添加app，
    修改或添加 ``STATIC_URL`` 、 ``MEDIA_URL`` 内容为七牛的域名，如果你设置了前缀，需要加上前缀

    .. code-block:: python

        CUSTOM_APPS = [
            'deeru_qiniu.apps.DeeruQiniuConfig'
        ]

        STATIC_URL='http://xx.bkt.clouddn.com/你的前缀/'
        MEDIA_URL='http://xx.bkt.clouddn.com/你的前缀/'

3. 上传文件

    运行命令上传文件

    .. code-block:: bash

        # 上传媒体文件
        python manage.py upload_qiniu --type media

        # 上传静态文件，上传静态文件前先运行collectstatic命令
        python manage.py collectstatic
        python manage.py upload_qiniu --type static

    若有相同名字的文件会上传失败，可用删除命令删除之前上传的文件

命令
----

删除命令
~~~~~~~~
会删除所有媒体文件或静态文件，不支持单个文件删除，删除单个文件在七牛后台中自行删除

.. code-block:: bash

        # 上传媒体文件
        python manage.py delete_qiniu [--type (media|static) ]


配置说明
---------

media_pre ,static_pre
~~~~~~~~~~~~~~~~~~~~~~

url的前缀，可为空，建议设置防止与空间中的旧文件冲突

其他
-------

如果文章中已经插入了图片，代理媒体文件会导致文章中的图片失效，需要重新编辑文章

license
---------

GUN V3.0