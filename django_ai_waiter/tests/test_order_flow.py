import pytest
from django_ai_waiter.models import Restaurant, MenuItem
from django_ai_waiter.cart_service import CartService
from django_ai_waiter.order_tools import OrderTools
from django_ai_waiter.tests.factories import  (
    RestaurantFactory,
    MenuItemFactory,
    CartFactory,
)


@pytest.mark.django_db
class TestOrderFlow:

    def test_create_restaurant(self):
        restaurant = RestaurantFactory()
        assert restaurant.name is not None
        assert restaurant.is_active is True

    def test_create_menu_item(self):
        item = MenuItemFactory(price=10.00)
        assert item.price == 10.00
        assert item.is_available is True

    def test_add_item_to_cart(self):
        restaurant = RestaurantFactory()
        item = MenuItemFactory(restaurant=restaurant, price=10.00)
        cs = CartService(
            session_key="test-flow-001",
            restaurant=restaurant,
        )
        cart_item = cs.add_item(item.id, quantity=2)
        assert cart_item.quantity == 2

    def test_cart_total(self):
        restaurant = RestaurantFactory()
        item = MenuItemFactory(restaurant=restaurant, price=10.00)
        cs = CartService(
            session_key="test-flow-002",
            restaurant=restaurant,
        )
        cs.add_item(item.id, quantity=3)
        summary = cs.get_cart_summary()
        assert summary["subtotal"] == 30.00

    def test_validate_cart(self):
        restaurant = RestaurantFactory()
        item = MenuItemFactory(restaurant=restaurant, price=10.00)
        cs = CartService(
            session_key="test-flow-003",
            restaurant=restaurant,
        )
        cs.add_item(item.id, quantity=1)
        tools = OrderTools(
            session_key="test-flow-003",
            restaurant=restaurant,
        )
        result = tools.validate_cart()
        assert result["valid"] is True

    def test_create_order(self):
        restaurant = RestaurantFactory()
        item = MenuItemFactory(restaurant=restaurant, price=10.00)
        cs = CartService(
            session_key="test-flow-004",
            restaurant=restaurant,
        )
        cs.add_item(item.id, quantity=1)
        tools = OrderTools(
            session_key="test-flow-004",
            restaurant=restaurant,
        )
        result = tools.create_order(table_number="5")
        assert result["success"] is True
        assert "ORD-" in result["order_number"]