import sys

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()


class Users(models.Model):
    full_name = models.CharField(max_length=256)
    user_phone_num = models.TextField(max_length=64)
    username = models.TextField(max_length=64)
    date_time = models.TextField(max_length=64)
    user_id = models.PositiveIntegerField()


class Channels(models.Model):
    channel_name = models.TextField(max_length=64)
    channel_link = models.TextField(max_length=64)



