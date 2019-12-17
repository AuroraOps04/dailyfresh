import time

from celery import Celery
from django.conf import settings
from django.core.mail import send_mail

app = Celery('celery_task.tasks', broker='redis://127.0.0.1:6379/8')


@app.task
def send_register_active_mail(to_email, username, token):
    subject = '天天生鲜欢迎信息'
    message = ''  # 这个参数是不会被渲染的.
    from_email = settings.EMAIL_FROM
    receivers = [to_email]
    html_message = f'<h1>{username}, 欢迎你成为天天生鲜会员.</h1>请点击一下注册码激活账户<a href="http://127.0.0.1:' \
                   f'8000/user/active/{token}/">http://127.0.0.1:8000/user/active/{token}/</a> '
    # 发送激活邮件
    send_mail(subject, message, from_email, receivers, html_message=html_message)
    # 模仿实际耗时任务
    time.sleep(5)
