from django.db import transaction

from shopping.models import OrderLimit


@transaction.atomic
def reset_daily_order_limits():
    for order in OrderLimit.objects.select_for_update().all():
        order.used_limit = 0
        order.save()
