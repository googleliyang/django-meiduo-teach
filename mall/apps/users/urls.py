from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token
urlpatterns = [
    #/users/usernames/(?P<username>\w{5,20})/count/
    url(r'^usernames/(?P<username>\w{5,20})/count/$',views.RegisterUsernameAPIView.as_view(),name='usernamecount'),

    url(r'^$',views.RegisterUserAPIView.as_view()),

    # 我们登陆的url 采用
    # users/auths/

    url(r'^auths/',obtain_jwt_token),
    # url(r'^api-token-auth/',obtain_jwt_token),



    url(r'^infos/$',views.UserCenterInfoAPIView.as_view()),

    url(r'^emails/$',views.UserEmailAPIView.as_view()),

    url(r'^emails/verification/$',views.UserEmailVerificationAPIView.as_view()),

    # url(r'^addresses/$',views.UserAddressAPIView.as_view()),

    url(r'^browerhistories/$',views.UserHistoryAPIView.as_view()),
]

from .views import AddressViewSet
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'addresses',AddressViewSet,base_name='address')
urlpatterns += router.urls

"""

登陆:
    1.接收前端提交的数据(用户名和密码)
    2.校验用户名和密码
    3.获取user

obtain_jwt_token
一,也是调用的django自带的认证系统,先完成用户的身份认证  user

二,来生成一个token
"""

#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
#eyJ1c2VyX2lkIjoxMCwiZW1haWwiOiIiLCJ1c2VybmFtZSI6Iml0Y2FzdCIsImV4cCI6MTU1MDgyNDAxOX0.
#c4errq2huCv9VcSh4MWWpAEFcC-tH_eiCigZld6me5A

