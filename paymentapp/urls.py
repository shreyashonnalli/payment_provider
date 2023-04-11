from django.urls import path
from . import views

urlpatterns = [
    path('create', views.create_checkout),
    path('<int:checkout_id>/transact', views.initiate_transaction),
]
