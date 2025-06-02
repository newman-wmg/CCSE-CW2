from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('create-order/', views.create_order, name='create_order'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='confirmation'),
    path('list/', views.order_list, name='order_list'),
    path('detail/<int:order_id>/', views.order_detail, name='detail'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
]