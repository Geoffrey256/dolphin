from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("services/", views.services, name="services"),
    path("aquarium/", views.aquarium, name="aquarium"),
    path("gas/", views.gas, name="gas"),
    path("supplements/", views.supplements, name="supplements"),
]
