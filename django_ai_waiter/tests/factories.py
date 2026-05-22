import factory
from django_ai_waiter.models import (
    Restaurant,
    MenuCategory,
    MenuItem,
    Cart,
    CartItem,
    Order,
    Conversation,
)


class RestaurantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Restaurant

    name = factory.Sequence(lambda n: f"Restaurant {n}")
    slug = factory.Sequence(lambda n: f"restaurant-{n}")
    is_active = True


class MenuCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MenuCategory

    restaurant = factory.SubFactory(RestaurantFactory)
    name = factory.Sequence(lambda n: f"Category {n}")
    display_order = factory.Sequence(lambda n: n)


class MenuItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MenuItem

    restaurant = factory.SubFactory(RestaurantFactory)
    category = factory.SubFactory(MenuCategoryFactory)
    name = factory.Sequence(lambda n: f"Item {n}")
    price = factory.Sequence(lambda n: 10.00 + n)
    is_available = True
    is_vegetarian = False


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    restaurant = factory.SubFactory(RestaurantFactory)
    session_key = factory.Sequence(lambda n: f"session-{n}")
    status = Cart.Status.ACTIVE


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart = factory.SubFactory(CartFactory)
    menu_item = factory.SubFactory(MenuItemFactory)
    quantity = 1
    unit_price = factory.LazyAttribute(lambda o: o.menu_item.price)