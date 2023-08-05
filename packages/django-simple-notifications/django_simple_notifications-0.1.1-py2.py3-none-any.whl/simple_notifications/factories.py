from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User

import factory
from factory import fuzzy

from simple_notifications.models import Notification


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: "User {}".format(n))

    @factory.post_generation
    def check_password(obj, create, extracted, **kwargs):
        if obj.pk and len(obj.password) == 0:
            obj.set_password("password")
            obj.save()


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: "Group {}".format(n))


class NotificationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Notification

    from_date = fuzzy.FuzzyDateTime(start_dt=timezone.now(), force_hour=0, force_minute=0, force_second=0, force_microsecond=0)
    to_date = factory.LazyAttribute(lambda o: o.from_date + timedelta(days=7))
    message = fuzzy.FuzzyText()
    time_to_show = fuzzy.FuzzyInteger(1, 10)

    @factory.post_generation
    def users(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for user in extracted:
                self.users.add(user)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                self.groups.add(group)
