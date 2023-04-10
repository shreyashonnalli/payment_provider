from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.get_data),
    path('api/checkout/', include('paymentapp.urls')),
]
