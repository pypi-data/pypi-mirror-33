# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group

from model_utils.models import TimeStampedModel


class Notification(TimeStampedModel):
    """
    A model used for create notifications to show to the user
    """

    from_date = models.DateTimeField()
    to_date = models.DateTimeField()
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    groups = models.ManyToManyField(Group, blank=True)
    activate = models.BooleanField(default=True)
    message = models.TextField()
    time_to_show = models.PositiveIntegerField(default=1)
    url = models.CharField(max_length=255, null=True, blank=True)


class UserNotificated(TimeStampedModel):
    """
    The model used for keep track of how many times a notification has been shown to a user
    """
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE)
    times_show_to_user = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
