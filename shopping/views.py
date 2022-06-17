from django.db import IntegrityError, transaction
from django.http import Http404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response

from shopping.models import Cart, Order, OrderLimit, Shelf
from shopping.serializers import CartSerializer, OrderSerializer, ShelfSerializer


class ShelfViewSet(viewsets.ModelViewSet):
    queryset = Shelf.objects.all()
    serializer_class = ShelfSerializer


class CartViewSet(
    RetrieveModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Cart.objects.all()

    serializer_class = CartSerializer

    @action(detail=False, methods=["post"])
    def add_to_cart(self, request, *args, **kwargs):
        serialized = self.get_serializer_class()(data=request.data)
        serialized.is_valid()
        data = serialized.data
        try:
            cart = Cart.objects.create(
                region_id=data["region_id"],
            )
        except IntegrityError:
            raise Http404(f"region_id:{data['region_id']} does not exist.")
        cart.shelves.set(data["shelves"])
        data["status"] = Cart.StatusEnum(cart.status).name
        data["cart_id"] = cart.pk

        return Response(data, status=status.HTTP_201_CREATED)


class OrderViewSet(
    RetrieveModelMixin,
    UpdateModelMixin,
    ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Order.objects.all()

    serializer_class = OrderSerializer

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def make_order(self, request, *args, **kwargs):
        serialized = self.get_serializer_class()(data=request.data)
        serialized.is_valid()
        data = serialized.data
        if check_cart_complete(data["cart_id"]):
            order_status = (
                Order.StatusEnum.accepted.value
                if complies_with_order_limits(data["region_id"])
                else Order.StatusEnum.rejected.value
            )
        else:
            order_status = Order.StatusEnum.rejected.value
        order = Order.objects.create(
            status=order_status,
            region_id=data["region_id"],
            cart_id=data["cart_id"],
        )
        data["status"] = Order.StatusEnum(order.status).name
        data["order_id"] = order.pk

        return Response(data, status=status.HTTP_201_CREATED)


def complies_with_order_limits(region_id: int) -> bool:
    limit_global = OrderLimit.objects.select_for_update().get(region="GLOBAL")
    if limit_global.used_limit == limit_global.daily_limit:
        return False
    try:
        limit = OrderLimit.objects.select_for_update().get(pk=region_id)
    except OrderLimit.DoesNotExist:
        raise Http404(f"region_id:{region_id} does not exist.")
    if limit.daily_limit is None or limit.used_limit < limit.daily_limit:
        limit.used_limit += 1
        limit_global.used_limit += 1
        limit.save()
        limit_global.save()
        return True
    return False


def check_cart_complete(cart_id: int) -> bool:
    try:
        cart_status = Cart.objects.get(pk=cart_id).status
    except Cart.DoesNotExist:
        raise Http404(f"cart_id:{cart_id} does not exist.")
    return cart_status == Cart.StatusEnum.complete.value
