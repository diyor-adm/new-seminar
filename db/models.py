import sys

try:
    from django.db import models
except Exception:
    print('Exception: Django Not Found, please install it with "pip install django".')
    sys.exit()


class Appeal(models.Model):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    address = models.CharField(max_length=256)
    price = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=64)
    user_age = models.CharField(max_length=16)
    date_time = models.TextField(max_length=64)
    user_id = models.PositiveIntegerField()


class Seminars(models.Model):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    address = models.CharField(max_length=256)
    seminar = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=64)
    user_age = models.CharField(max_length=16)
    date_time = models.TextField(max_length=64)
    user_id = models.PositiveIntegerField()


class Consultation(models.Model):
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    address = models.CharField(max_length=256)
    phone_number = models.CharField(max_length=64)
    user_age = models.CharField(max_length=16)
    date_time = models.TextField(max_length=64)
    user_id = models.PositiveIntegerField()


class users(models.Model):
    full_name = models.CharField(max_length=256)
    user_lang = models.CharField(max_length=256)
    user_id = models.PositiveIntegerField()
    date_time = models.TextField(max_length=64)



