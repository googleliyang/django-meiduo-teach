from django.conf.urls import url
from . import views

urlpatterns = [
    #/pay/orders/(?P<order_id>)\d+/
    url(r'^orders/(?P<order_id>\d+)/$',views.PayUrlAPIView.as_view(),name='pay'),

    #  /pay/status/
    url(r'^status/$',views.PayStatusAPIView.as_view()),
]