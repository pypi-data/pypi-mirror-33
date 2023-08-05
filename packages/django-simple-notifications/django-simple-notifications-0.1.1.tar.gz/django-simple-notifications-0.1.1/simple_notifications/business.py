from django.db.models import Q, F
from django.utils import timezone

from simple_notifications.models import Notification


class NotificationLogic:

    @classmethod
    def get_notifications_for_user(cls, user=None, pk=None, path=None):
        time = timezone.now()
        notifications = Notification.objects.filter(
            from_date__lte=time,
            to_date__gte=time
        ).order_by("id")
        if user:
            groups = user.groups.values_list('id', flat=True)
            notifications = notifications.filter(
                Q(users__in=[user]) |
                Q(groups__in=groups) |
                Q(users__isnull=True, groups__isnull=True)
            )

            if not notifications.exists():
                return False
            notifications = notifications.filter(Q(usernotificated__times_show_to_user__lt=F("time_to_show"),
                                                   usernotificated__user=user) |
                                                 Q(usernotificated__isnull=True))
        else:
            notifications = notifications.filter(users__isnull=True, groups__isnull=True)
        if not notifications.exists():
            return False
        if pk:
            notifications = notifications.filter(pk=pk)
        if path:
            notifications = notifications.filter(Q(url=path)|Q(url__isnull=True)|Q(url=""))
        return notifications
