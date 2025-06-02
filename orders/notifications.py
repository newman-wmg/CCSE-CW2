# This file handles sending order status update emails to users.

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

def send_order_status_email(order, status):
    # Map order statuses to corresponding email subjects
    subject_map = {
        'pending': 'Order Confirmation - Your SecureCart Order',
        'shipped': 'Your order has been shipped!',
        'delivered': 'Your order has been delivered!',
        'canceled': 'Your order has been canceled',
    }
    
    # Exit if the status is not recognized
    if status not in subject_map:
        return
    
    # Prepare context for the email template
    context = {
        'order': order,
        'user': order.user,
    }
    
    # Render the HTML message using the appropriate template
    html_message = render_to_string(f'orders/emails/{status}_order.html', context)
    
    # Send the email to the user with the specified subject and HTML content
    send_mail(
        subject=subject_map[status],
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
        html_message=html_message,
    ) 