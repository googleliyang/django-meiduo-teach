"""
Celery
    1. 因为celery是一个即插即用的任务队列 ,所以插入到我们工程的话
        Celery需要使用我们工程的配置文件 (必须放在 创建celery实例对象前边)
    2. 创建celery实例对象
    3. 设置broker
    4. celery自动检测任务

任务         创建任务
            1.任务的包名(随意) , 包中的文件 必须是 tasks.py
            2.所谓的任务 其实就是函数
            3.这个任务必须被Celery的实例对象的 task装饰器装饰
            4.这个任务,必须要让Celery自动检测
broker

worker
    celery -A celery实例对象的脚本文件路径 worker -l info
    celery -A celery_tasks.main worker -l info
"""

from celery import Celery

#1. Celery需要使用我们工程的配置文件
# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mall.settings")

import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'mall.settings'

#2. 创建Celery实例对象
# main 其实就是能够确保celery唯一就可以  (可以理解为 名字,名字唯一就好了)
# 一般都是使用 包的路径(包不会重复)
app = Celery(main='celery_tasks')

# 3. 设置broker
app.config_from_object('celery_tasks.config')

# 4. celery自动检测任务
# 任务 的包路径
app.autodiscover_tasks(['celery_tasks.sms','celery_tasks.email','celery_tasks.html'])


