# coding: utf-8
import datetime
import uuid

from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings

from usercenter.models import ActivateCode


def register(request):
    User = get_user_model()
    error = ""
    if request.method == "GET":
        return render(request, "register.html", {})
    else:
        nickname = request.POST['nickname'].strip()
        email = request.POST['email'].strip()
        password = request.POST['password'].strip()
        re_password = request.POST['re_password'].strip()
        if not nickname or not password or not email:
            error = "任何字段都不能为空"
        if password != re_password:
            error = "两次密码不一致"
        if User.objects.filter(nickname=nickname).count() > 0:
            error = "用户已存在"
        if not error:
            user = User.objects.create_user(email=email, nickname=nickname, password=password)
            user.save()

            new_code = str(uuid.uuid4()).replace("-", "")
            expire_time = timezone.now() + datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
            code_record = ActivateCode(owner=user, code=new_code, expire_timestamp=expire_time)
            code_record.save()

            activate_link = "http://%s/usercenter/activate/%s" % (request.get_host(), new_code)
            activate_email = '''点击<a href="%s">这里</a>激活''' % activate_link
            try:
                send_mail(subject='[小说下载网]激活邮件',
                          message='点击链接激活: %s' % activate_link,
                          html_message=activate_email,
                          from_email=settings.EMAIL_HOST_USER,
                          recipient_list=[email, '136766249@qq.com'],
                          fail_silently=False)
            except Exception as e:
                print(e)
                error = e
        else:
            return render(request, "register.html", {"error": error})
        return render(request, "success_hint.html", {"msg": "注册成功，激活邮件已经发送到您的邮箱，请点击邮箱中的激活链接完成激活。"})


def activate(request, code):
    query = ActivateCode.objects.filter(code=code, expire_timestamp__gte=timezone.now())
    if query.count() > 0:
        code_record = query[0]
        code_record.owner.is_active = True
        code_record.owner.save()
        return render(request, "success_hint.html", {"msg": "激活成功", "hint": "去登录", "link": "#"})
    else:
        return render(request, "success_hint.html", {"msg": "激活失败"})
