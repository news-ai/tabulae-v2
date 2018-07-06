# -*- coding: utf-8 -*-
# Core Django imports
from django.db.models import Manager

# Third-party app imports
from datetime import datetime, timedelta, time


class EmailManager(Manager):

    def emails_by_user_today(self, user):
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        today_start = datetime.combine(today, time())
        today_end = datetime.combine(tomorrow, time())

        print today_start
        print today_end

        return self.filter(created__lte=today_end,
                           created__gte=today_start, created_by=user)
