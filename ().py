# coding: utf-8
from users.models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
content_type = ContentType.objects.get_for_model(User)
permission = Permission.objects.create(codename="social_auth", name="Social Auth",  content_type=content_type)
