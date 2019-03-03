from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

# from mall.apps.users.models import User       错误的

# from apps.users.models import User            错误

from users.models import User
from users.serializers import RegisterUserSerializer, UserCenterInfoSerializer, UserEmailSerializer, AddressSerializer, \
    UserHistorySerializer

"""
一.分析需求
二.步骤(大概的思路)
三.确定请求方式和路由
四.选取哪个视图(结合需求,使用排除法)
五.编码
"""

"""
一.分析需求
当用户在用户名输入框中输入用户之后,当光标移开之后,前端应该 发送一个ajax请求
前端应该将 用户名传递给后端

    判断用户名有没有注册
    count   0       没有注册
    count   1       注册过来

    /users/usernames/itcast/count/

    /users/usernames/(?P<username>\w{5,20})/count/

二. 步骤(大概的思路)
   1. 后端接收数据
   2. 数据验证
   3. 查询数据库
   4. 返回相应

三.确定请求方式和路由
    GET     /users/usernames/(?P<username>\w{5,20})/count/

四.选取哪个视图(结合需求)
    APIView                         :基类
    GenericAPIView                  :对列表视图和详情视图做了通用支持,一般和mixin配合使用
    ListAPIView,RetrieveAPIView     : 连http请求方法都不用写

五.编码

"""
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
# class RegisterUsernameAPIView(APIView):
class RegisterUsernameAPIView(GenericAPIView):

    def get(self,request,username):
        # 1. 后端接收数据
        # 2. 数据验证
        # 3. 查询数据库
        count = User.objects.filter(username=username).count()

        data = {
            'count':count,
            'username':username
        }

        # 4. 返回相应
        return Response(data)

"""
一.分析需求
    当用户点击注册按钮的时候,需要让前端收集 用户名,手机号,密码,确认密码,短信验证码,是否同意协议

二.步骤(大概的思路)
    1.接收数据
    2.校验数据
    3.数据入库
    4.返回相应

三.确定请求方式和路由
    POST        users/


四.选取哪个视图(结合需求,使用排除法)
    APIView                         :基类
    GenericAPIView                  :对列表视图和详情视图做了通用支持,一般和mixin配合使用
    CreateAPIView                   : 连http请求方法都不用写

五.编码

"""
from users.serializers import RegisterUserSerializer
#############################一级视图##########################################
class RegisterUserAPIView(APIView):

    def post(self,request):
        # 1.接收数据
        data = request.data
        # 2.校验数据
        serializer = RegisterUserSerializer(data=data)
        serializer.is_valid()
        # 3.数据入库
        serializer.save()
        # 4.返回相应
        # serializer.data
        # 当我们把模型赋值给序列化器之后, 调用序列化器的 序列化方法(serializer.data 将对象转换为字典)
        # 原理是: 序列化器根据字段来获取模型中的数据

        return Response(serializer.data)


#############################二级视图##########################################
# from rest_framework.mixins import CreateModelMixin
# class RegisterUserAPIView(CreateModelMixin,GenericAPIView):
#
#     serializer_class = RegisterUserSerializer
#
#     def post(self,request):
#
#         return self.create(request)

#############################三级视图##########################################
# from rest_framework.generics import CreateAPIView
# class RegisterUserAPIView(CreateAPIView):
#
#     serializer_class = RegisterUserSerializer


"""
 当用户注册完成之后,自动登陆

 当用户注册完成之后,跳转到登陆页面,让用户输入用户名和密码自己登陆


"""

"""

"""

"""
一.分析需求
    当用户注册完成之后,自动登陆

    所谓的自动登陆是 当用户注册完成之后,我们生成一个token,将token返回给前端


二.步骤(大概的思路)
    # 1.用户注册完成之后
    # 2.生成一个token
    # 3.将token返回给前端

三.确定请求方式和路由
四.选取哪个视图(结合需求,使用排除法)
五.编码
"""


##########################个人中心##########################################

"""
一.分析需求
    当用户点击个人中心的时候,需要让前端将token传递过来

二.步骤(大概的思路)
    1. 个人中心必须是登陆用户才可以访问

    2. 获取用户信息  user
    3. 将对象转换为字典
    4. 返回相应

三.确定请求方式和路由
    GET     users/infos/

四.选取哪个视图(结合需求,使用排除法)
    APIView                         :基类
    GenericAPIView                  :对列表视图和详情视图做了通用支持,一般和mixin配合使用
    ListAPIView RetrieveAPIView     : 连http请求方法都不用写

五.编码

"""
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser,IsAuthenticatedOrReadOnly
# class UserCenterInfoAPIView(APIView):
#
#     # 1.个人中心必须是登陆用户才可以访问
#     permission_classes = [IsAuthenticated]
#
#     def get(self,request):
#
#
#         #from rest_framework_jwt.settings import api_settings
#         # jwt_encode(user)
#         # user = jwt_decode()
#
#         # token
#         # 2. 获取用户信息  user
#         user = request.user
#
#         # 3. 将对象转换为字典
#         serializer = UserCenterInfoSerializer(user)
#         # 4. 返回相应
#         return Response(serializer.data)
from rest_framework.generics import ListAPIView,RetrieveAPIView
class UserCenterInfoAPIView(RetrieveAPIView):
    #权限
    permission_classes = [IsAuthenticated]

    # queryset = User.objects.all()
    #序列化器
    serializer_class = UserCenterInfoSerializer


    def get_object(self):

        return self.request.user


"""
一.分析需求
    1.当用户输入邮箱之后,我们要保存邮箱信息

    2.还需要给 邮箱发送一个激活邮件
        激活邮件的内容
    3.激活邮件的状态
        点击激活邮件,更改邮件的状态

二.步骤(大概的思路)
    1.接收数据
    2.校验数据
    3.更新数据 put
    4.返回相应

三.确定请求方式和路由
    PUT     /users/email/

四.选取哪个视图(结合需求,使用排除法)
    APIView                         :基类
    GenericAPIView                  :对列表视图和详情视图做了通用支持,一般和mixin配合使用
    UpdateAPIView                    : 连http请求方法都不用写
五.编码
"""
# class UserEmailAPIView(APIView):
#
#     permission_classes = [IsAuthenticated]
#
#     def put(self,request):
#         # 1.接收数据
#         data = request.data
#         # 2.校验数据
#         serializer = UserEmailSerializer(instance=request.user,data=data)
#         serializer.is_valid(raise_exception=True)
#         # 3.更新数据 put

#         serializer.save()

#         # 4.返回相应
#         return Response(serializer.data)


# from rest_framework.mixins import UpdateModelMixin
# class UserEmailAPIView(UpdateModelMixin,GenericAPIView):
#      permission_classes = [IsAuthenticated]
#     # queryset = User.objects.all()
#
#     def get_object(self):
#
#         return self.request.user
#
#     serializer_class = UserEmailSerializer
#
#
#     def put(self,request):
#
#         return self.update(request)



from rest_framework.generics import UpdateAPIView
class UserEmailAPIView(UpdateAPIView):

    permission_classes = [IsAuthenticated]

    def get_object(self):

        return self.request.user

    serializer_class = UserEmailSerializer


"""
一.分析需求
    当用户点击激活邮件的时候,需要让前端将 token 传递给后端
二.步骤(大概的思路)
    1. 接收token
    2. 对token进行解密   {id:xxx,email:xxx}
    3. 查询用户信息
    4. 更改用户信息就可以了
    5. 返回相应
三.确定请求方式和路由
    GET     /users/emails/verifications/?token=xxxx
四.选取哪个视图(结合需求,使用排除法)
    APIView

五.编码
"""
from rest_framework import status
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature,SignatureExpired
from mall import settings
class UserEmailVerificationAPIView(APIView):


    def get(self,request):
        # 1. 接收token
        token = request.query_params.get('token')
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 2. 对token进行解密   {id:xxx,email:xxx}

        s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)

        #解密
        try:
            result = s.loads(token)
        except BadSignature:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 3. 查询用户信息
        id = result.get('id')
        email = result.get('email')

        try:
            user = User.objects.get(id=id,email=email)
        # user = User.objects.filter().filter()
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 4. 更改用户信息就可以了
        user.email_active=True
        user.save()
        # 5. 返回相应
        return Response({'msg':'ok'})



################################地址管理########################################

"""
新增地址

一.分析需求
   当用户点击保存地址按钮的时候,让前端收集 地址,省,市,区,联系人,邮箱,固定电话,详细地址,手机号
    提交给后端
    token 也就是用户信息,在请求头中提交

二.步骤(大概的思路)

   1.只有登陆用户才可以访问

   2.接收数据
   3.校验数据
   4.数据入库
   5.返回相应

三.确定请求方式和路由

   POST     users/addresses/

四.选取哪个视图(结合需求,使用排除法)
    APIView                         :基类
    GenericAPIView                  :对列表视图和详情视图做了通用支持,一般和mixin配合使用
    CreateAPIView                    : 连http请求方法都不用写
五.编码

"""
# from rest_framework.generics import CreateAPIView
# class UserAddressAPIView(CreateAPIView):
#
#     permission_classes = [IsAuthenticated]
#
#     serializer_class = AddressSerializer


    # AddressSerializer(instance=,)


class UserAddressAPIView(APIView):
    # 1.只有登陆用户才可以访问
    permission_classes = [IsAuthenticated]
    def post(self,request):
        #
        # 2.接收数据
        data = request.data
        # 3.校验数据
        serializer = AddressSerializer(data=data,context={'request':request,
                                                          'view':self})
        serializer.is_valid(raise_exception=True)
        # 4.数据入库
        serializer.save()
        # 5.返回相应
        return Response(serializer.data)


######################浏览记录##################################

"""  添加浏览记录
一.分析需求
    当登陆用户访问商品详情的时候,需要让前端发送一个 ajax请求
    将用户信息(token 在请求头中传递)和 商品id提交给后端

二.步骤(大概的思路)
    1.接收数据    goods_id
    2.校验数据
    3.数据入库
    4.返回相应

三.确定请求方式和路由
    POST         /users/browerhistories/          body

    GET         /users/browerhistory/?id=2
    GET         /users/browerhistory/id/


四.选取哪个视图(结合需求,使用排除法)
    APIView                         :基类
    GenericAPIView                  :对列表视图和详情视图做了通用支持,一般和mixin配合使用
    CreateAPIView                   : 连http请求方法都不用写

五.编码

Redis
    user_id,goods_id

String
    key:value

Hash

    hash_key:
        filed:value
        field:value


List  v
    list_key:  value1,value2,value2,value3,value1...

    user_id:    goods_id,goods_ids  有顺序

Set(无序)

    set_key:    value3,value1,value2,...


OrderSet

    zset_key:   value1,value2,value3,....

    user_id:   权重

"""

from rest_framework.generics import CreateAPIView
class UserHistoryAPIView(CreateAPIView):

    permission_classes = [IsAuthenticated]

    serializer_class = UserHistorySerializer

