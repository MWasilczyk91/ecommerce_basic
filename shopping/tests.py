import json

from rest_framework import status
from rest_framework.test import APITestCase

from shopping.factory import CartFactory, OrderLimitFactory, ShelfFactory
from shopping.models import Cart, Order, OrderLimit


class MakeOrderTestCase(APITestCase):
    def setUp(self):
        self.shelf = ShelfFactory()
        cart_region = OrderLimitFactory(region="XYZ")
        self.cart = CartFactory.create(
            status=Cart.StatusEnum.complete.value,
            shelves=(self.shelf,),
            region=cart_region,
        )

        self.global_limit = OrderLimit.objects.get(region="GLOBAL")
        self.global_limit.daily_limit = 3
        self.global_limit.save()

        self.url = "/api/orders/make_order/"

    def test_make_order_accepted(self):
        """Orders within global and regional limits for carts with status=complete
        should be created with status 'accepted'.
        """
        limit = OrderLimitFactory(daily_limit=1)
        data = {
            "region_id": limit.pk,
            "cart_id": self.cart.pk,
        }
        response = self.client.post(
            path=self.url,
            data=json.dumps(data),
            content_type="application/json",
        )
        expected_data = {
            "cart_id": self.cart.pk,
            "region_id": limit.pk,
            "status": Order.StatusEnum.accepted.name,
            "order_id": 1,
        }
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Order.StatusEnum.accepted.name)
        self.assertDictEqual(response.data, expected_data)

    def test_make_order_global_limit_exceeded(self):
        """Orders within regional limit but over the global limit for carts with status=complete
        should be created with status 'rejected'.
        """
        self.global_limit.used_limit = self.global_limit.daily_limit
        self.global_limit.save()
        limit = OrderLimitFactory(daily_limit=1)
        data = {
            "region_id": limit.pk,
            "cart_id": self.cart.pk,
        }
        response = self.client.post(
            path=self.url,
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Order.StatusEnum.rejected.name)

    def test_make_order_regional_limit_exceeded(self):
        """Orders exceeding the regional limit for carts with status=complete
        should be created with status 'rejected'.
        """
        limit = OrderLimitFactory(daily_limit=1, used_limit=1)
        data = {
            "region_id": limit.pk,
            "cart_id": self.cart.pk,
        }
        response = self.client.post(
            path=self.url,
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Order.StatusEnum.rejected.name)

    def test_make_order_cart_incomplete(self):
        """Orders within limits for carts with status other than 'complete'
        should be created with status 'rejected'.
        """
        self.cart.status = Cart.StatusEnum.new.value
        self.cart.save()
        limit = OrderLimitFactory(daily_limit=1)
        data = {
            "region_id": limit.pk,
            "cart_id": self.cart.pk,
        }
        response = self.client.post(
            path=self.url,
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Order.StatusEnum.rejected.name)

    def test_make_order_regional_limit_undefined(self):
        """Orders from region that doesn't have regional limit for carts with
        status=complete should be created with status 'accepted'.
        """
        limit = OrderLimitFactory(daily_limit=None)
        data = {
            "region_id": limit.pk,
            "cart_id": self.cart.pk,
        }
        response = self.client.post(
            path=self.url,
            data=json.dumps(data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], Order.StatusEnum.accepted.name)
