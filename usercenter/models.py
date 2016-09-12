from django.db import models
from django.conf import settings
# from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
# Create your models here.
class MyUserManager(BaseUserManager):
    def create_user(self, email, nickname, password=None):
        if not email:
            raise ValueError('必须输入邮箱')

        user = self.model(
            email=self.normalize_email(email),
            nickname=nickname
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, password):
        user = self.create_user(
            email,
            nickname,
            password=password
            )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)

        return user


class MyUser(AbstractBaseUser):

    email = models.EmailField(
        verbose_name='邮箱',
        max_length=255,
        unique=True,
    )
    nickname = models.CharField(verbose_name='昵称', max_length=50)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname']

    def get_full_name(self):
        return self.nickname

    def get_short_name(self):
        return self.nickname

    def __str__(self):
        return self.nickname

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


class ActivateCode(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="用户")
    code = models.CharField("激活码", max_length=100)

    expire_timestamp = models.DateTimeField()

    create_timestamp = models.DateTimeField(auto_now_add=True)
    last_update_timestamp = models.DateTimeField(auto_now=True)