from django.urls import path
from . import views

urlpatterns = [
    path('create', views.create_checkout),
    path('<int:checkout_id>/transact', views.initiate_transaction),
    path('<int:checkout_id>', views.get_checkout),
    path('<int:checkout_id>/status', views.get_status),
    path('<int:checkout_id>/cancel', views.cancel_checkout),
    path('<int:checkout_id>/refund', views.refund_checkout),
    path('process', views.process_transaction),
]
