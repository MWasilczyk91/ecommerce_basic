from datetime import datetime

from django.core.management.base import BaseCommand
from django_q.models import Schedule


class Command(BaseCommand):
    help = """
    Command to create a task in django_q schedule that runs the function
    resetting daily order limits every day.
    """

    def handle(self, *args, **kwargs):
        Schedule.objects.create(
            name="Reset daily order limits",
            func="shopping.tasks.reset_daily_order_limits",
            schedule_type=Schedule.DAILY,
            repeats=-1,
            next_run=datetime(2022, 6, 13, 0),
        )
        self.stdout.write(
            "Schedule task for func reset_daily_order_limits created successfully"
        )
