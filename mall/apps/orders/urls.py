from django.conf.urls import url
from . import views

urlpatterns = [
    #/orders/places/
    url(r'^places/$',views.PlaceOrderAPIView.as_view(),name='placeorder'),
]