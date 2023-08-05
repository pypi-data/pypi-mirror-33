
from simple_notifications.settings import settings
from django.http import HttpRequest

from simple_notifications.business import NotificationLogic
from simple_notifications.compat import is_user_authenticated


def check_user_show_notification(request: HttpRequest):
    """
    Search and Return a dict with the first notitifcation found for the user, using the id
    :param request:
    :return: dict
    """
    #check if it's allow show the notifications to anonymous users
    check = settings["SIMPLE_NOTIFICATIONS"]["SHOW_NOTIFICATIONS_TO_ANONYMOUS_USER"]
    authenticated = is_user_authenticated(request.user)
    if not authenticated and not check:
        return {}
    user = request.user if authenticated else None
    notifications = NotificationLogic.get_notifications_for_user(user, path=request.path)
    if not notifications:
        return {}
    notifications.filter()
    notification = notifications.filter()[0]
    return {
        "notification": notification
    }
