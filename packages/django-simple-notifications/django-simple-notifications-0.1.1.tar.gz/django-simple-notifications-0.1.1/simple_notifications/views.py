# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import JsonResponse, HttpRequest, Http404

from simple_notifications.business import NotificationLogic

from simple_notifications.models import (
    UserNotificated
)


@login_required
def update_notification_user(request: HttpRequest, pk: str) -> JsonResponse:
    """
    Update the number of time than a notification is show to the user
    :param request:
    :param pk: id from the user
    :return: json
    """
    notifications = NotificationLogic.get_notifications_for_user(request.user, pk)
    if not notifications.exists():
        raise Http404
    notification = notifications[0]
    user_notificated, created = UserNotificated.objects.get_or_create(
        notification=notification,
        user=request.user
    )
    user_notificated.times_show_to_user=F("times_show_to_user")+1
    user_notificated.save()
    return JsonResponse({"sucess": True})
