import re

from django.shortcuts import render, redirect, HttpResponse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.core.urlresolvers import reverse
from django.views import View
from django.conf import settings
from django.contrib.auth import login, authenticate

from celery_task.tasks import send_register_active_mail
from .models import User


class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        if not all([username, password, email]):
            return render(request, 'register.html', context={'err_msg': '数据不完整'})
        if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
            return render(request, 'register.html', context={'err_msg': '邮箱格式不正确'})
        if allow != 'on':
            return render(request, 'register.html', context={'err_msg': '请同意协议'})
        try:
            User.objects.get(username=username)

            return render(request, 'register.html', context={'err_msg': '用户名已存在'})
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.is_active = 0
            user.save()

            serializer = Serializer(settings.SECRET_KEY, 60 * 60)
            token = serializer.dumps({'confirm': user.id})
            token = token.decode()

            # 把邮件发送加入到用户队列
            send_register_active_mail.delay(email, username, token)
            return redirect(reverse('goods:index'))


class ActiveView(View):
    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 60 * 60)
        try:
            user_id = serializer.loads(token)['confirm']
            User.objects.filter(id=user_id).update(is_active=1)
            return redirect(reverse('user:login'))
        except SignatureExpired:
            return HttpResponse("激活码已过期")


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        if not all([username, password]):
            return render(request, 'login.html', context={'errmsg': '数据不完整'})
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('goods:index'))
            else:
                return render(request, 'login.html', context={'errmsg': '用户未激活'})
        else:
            return render(request, 'login.html', context={'errmsg': '账号密码错误'})