
from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    chinese_name = models.CharField(max_length=50, blank=True, null=True)
    mobile = models.CharField(max_length=50, blank=True, null=True)
    emp_no = models.CharField(max_length=50, blank=True, null=True)
    domain_account = models.CharField(max_length=50, blank=True, null=True)
    ticket = models.CharField(max_length=50, blank=True, null=True)
    level = models.CharField(max_length=50, blank=True, null=True)
    weixin_token = models.CharField(max_length=100, blank=True, null=True)
    remark = models.CharField(max_length=500, blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True)
    create_user = models.ForeignKey(User,related_name='create_user', blank=True, null=True)
    login_time = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    expiration_time = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    last_change_datetime = models.DateTimeField(auto_now=True)
    last_change_user = models.ForeignKey(User,related_name='last_change_user', blank=True, null=True)


    def __unicode__(self):
        return self.user.username
