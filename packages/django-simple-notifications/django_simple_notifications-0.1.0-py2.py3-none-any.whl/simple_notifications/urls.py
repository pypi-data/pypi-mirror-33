# -*- coding: utf-8 -*-
import django

from . import views

#app_name = 'dj_notifications'

if django.__version__[0] == "1":

    from django.conf.urls import url

    urlpatterns = [
        url("^user/notificated/(?P<pk>.+)/$",
            views.update_notification_user,
            name='User_Notificated',
        ),
    ]
else:

    from django.urls import path

    urlpatterns = [
        path('user/notificated/<pk>/',
             views.update_notification_user,
             name='User_Notificated'),
    ]
