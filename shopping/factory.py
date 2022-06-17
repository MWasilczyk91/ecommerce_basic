import factory
from factory import fuzzy

from shopping.models import Cart, OrderLimit, Shelf


class OrderLimitFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderLimit
        django_get_or_create = ("daily_limit", "region", "used_limit")

    daily_limit = fuzzy.FuzzyInteger(10)
    used_limit = 0
    region = fuzzy.FuzzyChoice(["XX", "YY", "ZZ"])


class ShelfFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Shelf
        django_get_or_create = ("products",)

    products = "prod1, prod2"


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    region = factory.SubFactory(OrderLimitFactory)

    @factory.post_generation
    def shelves(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for shelf in extracted:
                self.shelves.add(shelf)
