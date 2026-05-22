from django.db import transaction
from django_ai_waiter.models import Cart, CartItem, Order, OrderItem, MenuItem
from django_ai_waiter.adapters import OrderAdapter, PricingAdapter
from django_ai_waiter.app_settings import MIN_ORDER_AMOUNT


class OrderToolsError(Exception):
    """Raised when order tool operation fails."""
    pass


class OrderTools:
    """
    MCP Order Tools:
    - validate_cart
    - create_order
    - confirm_order
    """

    def __init__(self, session_key, restaurant=None):
        self.session_key = session_key
        self.restaurant = restaurant

    def _get_active_cart(self):
        """Get active cart for session."""
        cart = Cart.objects.filter(
            session_key=self.session_key,
            status=Cart.Status.ACTIVE,
        ).first()

        if not cart:
            raise OrderToolsError("No active cart found!")

        return cart

    def validate_cart(self):
        """
        Validate cart before order creation.
        Checks:
        - Cart exists
        - Cart has items
        - All items are available
        - Minimum order amount met
        """
        try:
            cart = self._get_active_cart()
        except OrderToolsError as e:
            return {
                "valid": False,
                "message": str(e),
                "errors": ["No active cart found"],
            }

        errors = []
        items = cart.cart_items.select_related("menu_item").all()

        # Check cart has items
        if not items.exists():
            errors.append("Cart is empty")

        # Check all items are available
        unavailable = []
        for cart_item in items:
            if not cart_item.menu_item.is_available:
                unavailable.append(cart_item.menu_item.name)

        if unavailable:
            errors.append(
                f"These items are no longer available: {', '.join(unavailable)}"
            )

        # Check minimum order amount
        subtotal = float(cart.total)
        if subtotal < MIN_ORDER_AMOUNT:
            errors.append(
                f"Minimum order is ${MIN_ORDER_AMOUNT}. "
                f"Current total is ${subtotal:.2f}"
            )

        if errors:
            return {
                "valid": False,
                "message": "Cart validation failed",
                "errors": errors,
            }

        # Calculate totals
        pricing = PricingAdapter.calculate_total(subtotal)

        return {
            "valid": True,
            "message": "Cart is valid and ready to order!",
            "subtotal": pricing["subtotal"],
            "tax": pricing["tax"],
            "total": pricing["total"],
            "item_count": items.count(),
        }

    def create_order(self, table_number="1"):
        """Create order from active cart."""

        # Validate first
        validation = self.validate_cart()
        if not validation["valid"]:
            return {
                "success": False,
                "message": validation["message"],
                "errors": validation["errors"],
            }

        cart = self._get_active_cart()
        items = cart.cart_items.select_related("menu_item").all()

        # Calculate totals
        subtotal = float(cart.total)
        pricing = PricingAdapter.calculate_total(subtotal)

        with transaction.atomic():
            # Generate order number
            order_number = OrderAdapter.to_order_number()

            # Create order
            order = Order.objects.create(
                restaurant=self.restaurant or cart.restaurant,
                cart=cart,
                order_number=order_number,
                status=Order.Status.PENDING,
                table_number=table_number,
                subtotal=pricing["subtotal"],
                tax=pricing["tax"],
                total=pricing["total"],
            )

            # Create order items from cart items
            for cart_item in items:
                OrderItem.objects.create(
                    order=order,
                    menu_item=cart_item.menu_item,
                    name=cart_item.menu_item.name,
                    unit_price=cart_item.unit_price,
                    quantity=cart_item.quantity,
                )

            # Mark cart as checked out
            cart.status = Cart.Status.CHECKED_OUT
            cart.save()

        return {
            "success": True,
            "order_number": order_number,
            "message": f"Order #{order_number} created successfully!",
            "subtotal": pricing["subtotal"],
            "tax": pricing["tax"],
            "total": pricing["total"],
            "table_number": table_number,
        }

    def confirm_order(self, order_number):
        """Confirm a pending order."""
        try:
            order = Order.objects.get(
                order_number=order_number,
                status=Order.Status.PENDING,
            )
        except Order.DoesNotExist:
            return {
                "success": False,
                "message": f"Order #{order_number} not found or already confirmed",
            }

        order.status = Order.Status.CONFIRMED
        order.save()

        return {
            "success": True,
            "order_number": order_number,
            "message": f"Order #{order_number} confirmed! Kitchen is preparing your food.",
            "status": order.status,
        }