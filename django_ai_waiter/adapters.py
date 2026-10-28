from django_ai_waiter.app_settings import (
    CURRENCY_SYMBOL,
    TAX_RATE,
    ORDER_NUMBER_PREFIX,
)


class MenuAdapter:
    """Converts database menu data to AI friendly format."""

    @staticmethod
    def to_ai_format(menu_items):
        """Convert menu items list to readable text for AI."""
        if not menu_items:
            return "No menu items available."

        # Group by category
        categories = {}
        for item in menu_items:
            category = item.get("category", "Other")
            if category not in categories:
                categories[category] = []
            categories[category].append(item)

        # Build simple, plain-text menu (no IDs, minimal symbols)
        lines = ["Menu:"]
        for category, items in categories.items():
            lines.append(f"{category}:")
            for item in items:
                line = f"- {item['name']}: {CURRENCY_SYMBOL}{item['price']:.2f}"
                if item.get("is_vegetarian"):
                    line += " (Vegetarian)"
                if item.get("is_vegan"):
                    line += " (Vegan)"
                if item.get("is_gluten_free"):
                    line += " (Gluten Free)"
                lines.append(line)
            lines.append("")

        return "\n".join(lines)
    @staticmethod
    def to_dict(menu_item):
        """Convert single MenuItem model to dict."""
        return {
            "id": str(menu_item.id),
            "name": menu_item.name,
            "description": menu_item.description,
            "price": float(menu_item.price),
            "price_display": f"{CURRENCY_SYMBOL}{menu_item.price}",
            "category": menu_item.category.name if menu_item.category else "Other",
            "is_available": menu_item.is_available,
            "is_vegetarian": menu_item.is_vegetarian,
            "is_vegan": menu_item.is_vegan,
            "is_gluten_free": menu_item.is_gluten_free,
        }


class OrderAdapter:
    """Converts order data between database and AI format."""

    @staticmethod
    def cart_to_ai_format(cart_summary):
        """Convert cart summary to readable text for AI."""
        if not cart_summary or not cart_summary.get("items"):
            return "🛒 Cart is empty."

        lines = ["🛒 CURRENT ORDER:\n"]
        for item in cart_summary["items"]:
            lines.append(
                f"  • {item['quantity']}x {item['name']} "
                f"— {CURRENCY_SYMBOL}{item['subtotal']:.2f}"
            )

        lines.append(f"\nSubtotal: {CURRENCY_SYMBOL}{cart_summary['subtotal']:.2f}")
        lines.append(f"Tax ({TAX_RATE*100:.0f}%): {CURRENCY_SYMBOL}{cart_summary['tax']:.2f}")
        lines.append(f"Total: {CURRENCY_SYMBOL}{cart_summary['total']:.2f}")
        lines.append(f"Status: {cart_summary['state'].upper()}")

        return "\n".join(lines)

    @staticmethod
    def to_order_number():
        """Generate unique order number."""
        import random
        import string
        suffix = "".join(random.choices(string.digits, k=6))
        return f"{ORDER_NUMBER_PREFIX}-{suffix}"

    @staticmethod
    def cart_to_order_data(cart):
        """Convert cart to order creation data."""
        items = cart.cart_items.select_related("menu_item").all()
        subtotal = float(cart.total)
        tax = subtotal * TAX_RATE
        total = subtotal + tax

        return {
            "subtotal": round(subtotal, 2),
            "tax": round(tax, 2),
            "total": round(total, 2),
            "items": [
                {
                    "name": item.menu_item.name,
                    "quantity": item.quantity,
                    "unit_price": float(item.unit_price),
                    "subtotal": float(item.unit_price * item.quantity),
                }
                for item in items
            ],
        }


class PricingAdapter:
    """Handles all pricing calculations."""

    @staticmethod
    def calculate_total(subtotal):
        """Calculate tax and total from subtotal."""
        tax = subtotal * TAX_RATE
        total = subtotal + tax
        return {
            "subtotal": round(subtotal, 2),
            "tax": round(tax, 2),
            "total": round(total, 2),
            "tax_rate": TAX_RATE,
            "tax_percentage": f"{TAX_RATE * 100:.0f}%",
        }

    @staticmethod
    def format_price(amount):
        """Format price with currency symbol."""
        return f"{CURRENCY_SYMBOL}{amount:.2f}"

    @staticmethod
    def calculate_item_subtotal(unit_price, quantity):
        """Calculate subtotal for a single item."""
        subtotal = float(unit_price) * quantity
        return round(subtotal, 2)