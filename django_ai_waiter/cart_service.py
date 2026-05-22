from django.db import transaction
from django_ai_waiter.models import Cart, CartItem, MenuItem
from django_ai_waiter.state_machine import OrderStateMachine, OrderState, StateMachineError
from django_ai_waiter.app_settings import TAX_RATE, MIN_ORDER_AMOUNT


class CartServiceError(Exception):
    """Raised when cart operation fails."""
    pass


class CartService:
    """Handles all cart operations with state machine enforcement."""

    def __init__(self, session_key, restaurant=None):
        self.session_key = session_key
        self.restaurant = restaurant
        self.cart = self._get_or_create_cart()
        self.sm = OrderStateMachine(
            self._get_current_state()
        )

    def _get_or_create_cart(self):
        """Get existing cart or create new one."""
        cart = Cart.objects.filter(
            session_key=self.session_key,
            status=Cart.Status.ACTIVE,
        ).first()

        if not cart:
            cart = Cart.objects.create(
                session_key=self.session_key,
                restaurant=self.restaurant,
                status=Cart.Status.ACTIVE,
            )
        return cart

    def _get_current_state(self):
        """Get current state from cart."""
        items = self.cart.cart_items.count()
        if items == 0:
            return OrderState.NEW
        return OrderState.COLLECTING

    def add_item(self, menu_item_id, quantity=1, special_instructions=""):
        """Add item to cart."""
        # Check state allows collecting
        if not self.sm.can_transition(OrderState.COLLECTING):
            if self.sm.state != OrderState.COLLECTING:
                raise CartServiceError(
                    f"Cannot add items in state: {self.sm.state.value}"
                )

        # Get menu item
        try:
            menu_item = MenuItem.objects.get(
                id=menu_item_id,
                is_available=True,
            )
        except MenuItem.DoesNotExist:
            raise CartServiceError(f"Item not found or not available")

        # Add or update cart item
        with transaction.atomic():
            cart_item, created = CartItem.objects.get_or_create(
                cart=self.cart,
                menu_item=menu_item,
                defaults={
                    "quantity": quantity,
                    "unit_price": menu_item.price,
                    "special_instructions": special_instructions,
                }
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()

            # Move state to collecting
            if self.sm.state == OrderState.NEW:
                self.sm.transition(OrderState.COLLECTING)

        return cart_item

    def remove_item(self, menu_item_id):
        """Remove item from cart."""
        if self.sm.is_confirmed():
            raise CartServiceError(
                "Cannot remove items from a confirmed order!"
            )

        CartItem.objects.filter(
            cart=self.cart,
            menu_item_id=menu_item_id,
        ).delete()

        return True

    def get_cart_summary(self):
        """Get full cart summary with totals."""
        items = self.cart.cart_items.select_related("menu_item").all()

        item_list = []
        for item in items:
            item_list.append({
                "name": item.menu_item.name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "subtotal": float(item.unit_price * item.quantity),
            })

        subtotal = float(self.cart.total)
        tax = subtotal * TAX_RATE
        total = subtotal + tax

        return {
            "items": item_list,
            "subtotal": round(subtotal, 2),
            "tax": round(tax, 2),
            "total": round(total, 2),
            "state": self.sm.state.value,
            "item_count": len(item_list),
        }

    def confirm_order(self):
        """Confirm the order — no more changes after this!"""
        # Check minimum order amount
        subtotal = float(self.cart.total)
        if subtotal < MIN_ORDER_AMOUNT:
            raise CartServiceError(
                f"Minimum order amount is ${MIN_ORDER_AMOUNT}. "
                f"Current total is ${subtotal:.2f}"
            )

        # Check cart has items
        if not self.cart.cart_items.exists():
            raise CartServiceError("Cannot confirm empty cart!")

        # Transition state
        if not self.sm.can_transition(OrderState.CONFIRMED):
            raise CartServiceError(
                f"Cannot confirm order in state: {self.sm.state.value}"
            )

        self.sm.transition(OrderState.CONFIRMED)
        return self.get_cart_summary()

    def cancel_order(self):
        """Cancel the order."""
        if self.sm.is_placed():
            raise CartServiceError("Cannot cancel a placed order!")

        self.sm.transition(OrderState.CANCELLED)
        self.cart.status = Cart.Status.ABANDONED
        self.cart.save()
        return True