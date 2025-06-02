# This file provides custom template filters for order-related calculations,
# allowing mathematical operations to be performed within Django templates.

from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    # Converts value to float to ensure decimal precision in order calculations
    return float(value) * arg 