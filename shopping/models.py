from enum import Enum, IntEnum, unique

from django.core.exceptions import ValidationError
from django.db import models


class Shelf(models.Model):
    products = models.CharField(max_length=255)


class OrderLimit(models.Model):
    region = models.CharField(
        unique=True,
        max_length=8,
        help_text="Country code",
    )
    daily_limit = models.PositiveIntegerField(
        null=True, blank=True, help_text="Daily order limit"
    )
    used_limit = models.PositiveIntegerField(
        default=0, help_text="Current usage, reset daily"
    )

    def save(self, *args, **kwargs):
        if self.region == "global" and not self.daily_limit:
            raise ValidationError("Global ordering daily limit must be greater than 0")
        if self.daily_limit is not None and self.used_limit > self.daily_limit:
            self.used_limit = self.daily_limit
        super().save(*args, **kwargs)


class Cart(models.Model):
    @unique
    class StatusEnum(IntEnum):
        new = 1
        complete = 2

    shelves = models.ManyToManyField(
        Shelf,
        related_name="carts",
    )
    status = models.IntegerField(
        null=False,
        choices=[(choice.value, choice.name) for choice in StatusEnum],
        default=StatusEnum.new.value,
    )
    region = models.ForeignKey(
        OrderLimit, on_delete=models.PROTECT, related_name="carts"
    )


class Order(models.Model):
    @unique
    class StatusEnum(IntEnum):
        accepted = 1
        rejected = 2

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="orders")
    status = models.IntegerField(
        null=False,
        choices=[(choice.value, choice.name) for choice in StatusEnum],
    )
    region = models.ForeignKey(
        OrderLimit, on_delete=models.PROTECT, related_name="orders"
    )
    creation_date = models.DateTimeField(db_index=True, auto_now_add=True)
