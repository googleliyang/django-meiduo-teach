import pickle

import base64
from django.shortcuts import render
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from carts.serialziers import CartSerializer, CartSKUSerializer
from goods.models import SKU

"""
    后端:  关系型数据库 mysql
        非关系数据库   redis
1. 登陆用户保存在后端

    未登陆用户保存在前端, cookie

2. 前端和后端 都是保存 商品id,个数和选中的状态

3.
    登陆用户保存在redis中,确定 redis是数据结构
        user_id_1:
                 sku_id_1,count_5,selected_True
                 sku_id_2,count_10,selected_False
                 sku_id_3,count_15,selected_True

        sku_id,count,selected
    Redis 数据是保存在内存中,我们应该尽量少的来占用内存空间(不要浪费空间)
        Hash
            hash_key:
                filed:value
                field:value

            user_id_1:
                sku_id_1: count_5
                2: 10
                3: 15

        Set(无序)

            set_key:    value3,value1,value2,...
            保存选中的id
            未选中的id 是通过程序来判断的
            sku_id_1:   [1,3]



    未登录用户保存在cookie中,确定 cookie的数据结构
        {
            'sku_id':{count:xxx,selected:True},
            'sku_id':{count:xxx,selected:True},
            'sku_id':{count:xxx,selected:True},
        }

4.
    处理数据

    base64模块

1G = 1024M
1M = 1024K
1K = 1024B
1B = 8b 比特位
比特位 0/1

A               A       A
0100 0001   0100 0001   0100 0001

base64 是 6个 比特位为一个字节

010000  010100  000101   000001
x       y       z           n


5. 先让用户 能够添加到购物车,需要验证的时候再验证


"""
# Create your views here.
from django.http.response import JsonResponse

# carts

class CartAPIView(APIView):

    # APIView 会对我们的身份进行验证
    # 会调用 perform_authentication
    # 其实就是调用 request.user 来判断用户是身份

    # 即便用户的token过期 或者 伪造 我们就认为它是没有登陆
    # 没有登陆的话 我们把购物车数据保存在cookie中
    # 保存在cookie中的话 是可以访问 http方法的

    # 所以 应该在 我们需要验证的时候 再来验证身份就行了

    def perform_authentication(self, request):
        pass
    """
    一.需求:

    如果用户没有登陆,当用户点击加入购物车的时候,前端需要将商品id,个数,选中状态提交给后端
    如果用户登陆了,当用户点击加入购物车的时候,前端需要将商品id,个数,选中状态和用户信息提交给后端

    二.步骤:

    1.后端接收这些数据(sku_id,count,selected)
    2.校验数据
    3.校验之后再获取这些数据
    4.获取用户信息
    5.根据用户信息进行判断
    6.登陆用户redis
        6.1 连接redis
        6.2 保存数据    hash  set
        6.3 返回相应
    7.未登录用户cookie

        接收数据了    1: count:1 selected:True

        7.1 先获取cookie信息
        7.2 判断cookie信息中 是否有 购物车的信息
            如果有 cookie信息是经过base64加密的,现在要解密
            如果没有

            {1:'count':2,'selected':True}
        7.3 判断商品是否存在cookie的购物车中
            如果有则累加个数
            如果没有 则将接收的数据 添加到cookie购物车中

            {1:'count':2,'selected':True}
        7.4 对字典数据进行转换   'abcde'
        7.5  设置cookie
        7.6   返回相应

    """
    def post(self,request):
        # 1.后端接收这些数据(sku_id,count,selected)
        data = request.data
        # 2.校验数据
        serializer = CartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        # 3.校验之后再获取这些数据
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')
        # 4.获取用户信息
        user = request.user
        # 5.根据用户信息进行判断
        # is_authenticated 认证过的,也就是说 是登陆的用户
        if user is not None and user.is_authenticated:

            # 6.登陆用户redis
            #     6.1 连接redis
            redis_conn = get_redis_connection('cart')
            #     6.2 保存数据
            # hash
            redis_conn.hset('cart_%s'%user.id,sku_id,count)
            # set  集合
            if selected:
                redis_conn.sadd('cart_selected_%s'%user.id,sku_id)
            #     6.3 返回相应
            return Response(serializer.data)

        else:
            # 7.未登录用户cookie
            #
            #     接收数据了    1: count:1 selected:True
            #
            #     7.1 先获取cookie信息
            cookie_str = request.COOKIES.get('cart')
            #     7.2 判断cookie信息中 是否有 购物车的信息
            if cookie_str is not None:
                #         如果有 cookie信息是经过base64加密的,现在要解密
                # 7.2.1 先将字符串经过base64 解密
                bytes_data = base64.b64decode(cookie_str)
                #7.2.2 将解密的二进制 进行字典转换
                cookie_cart = pickle.loads(bytes_data)

            else:
                #         如果没有
                cookie_cart = {}
            #
            #         cookie_cart = {1:{'count':2,'selected':True}}
            #     7.3 判断商品是否存在cookie的购物车中
            if sku_id in cookie_cart:
                #         如果有则累加个数
                original_count = cookie_cart[sku_id]['count']
                # count = count + original_count
                count += original_count

            #更新数据
            #         如果没有 则将接收的数据 添加到cookie购物车中
            cookie_cart[sku_id]={
                'count':count,
                'selected':selected
            }

            #
            #         {1:{'count':2,'selected':True}}
            #     7.4 对字典数据进行转换   'abcde'
            # 7.4.1 将字典转换为二进制
            bytes_dumps = pickle.dumps(cookie_cart)
            #7.4.2 对二进制进行base64编码
            bytes_str =  base64.b64encode(bytes_dumps)
            # 7.4.3 获取字符串
            cookie_save_str = bytes_str.decode()
            #     7.5  设置cookie
            response = Response(serializer.data)

            response.set_cookie('cart',cookie_save_str,3600)

            #     7.6   返回相应
            return response


    """
    一.需求
        当用户点击购物车页面的时候,我们需要让前端将用户信息传递给后端
    二.步骤
        1. 获取用户信息
        2. 判断用户信息
        3. 登陆用户从redis中获取数据
            3.1 连接redis
            3.2 获取redis的数据 hash set  sku_id:count,sku_id:count ,
            3.3 获取商品的所有的id      [id,id,id,id]
            3.4 再根据id获取商品的详细信息  [sku,sku,sku,sku]
            3.5 将对象列表转换为字典
            3.6 返回相应
        4. 未登录用户从cookie中获取数据
            4.1 从cookie中获取数据
            4.2 判断数据是否存在
                如果存在则要进行 解码     {sku_id:{count:xxx,selected:xxx}}
                如果不存在
            4.3 获取商品的所有的id  [id,id,id]
            4.4 再根据id获取商品的详细信息 [sku,sku,sku,sku]
            4.5 将对象列表转换为字典
            4.6 返回相应




        # 1. 获取用户信息
        # 2. 判断用户信息
        # 3. 登陆用户从redis中获取数据
        #     3.1 连接redis
        #     3.2 获取redis的数据 hash set  sku_id:count,sku_id:count ,
        #
        # 4. 未登录用户从cookie中获取数据
        #     4.1 从cookie中获取数据
        #     4.2 判断数据是否存在
        #         如果存在则要进行 解码     {sku_id:{count:xxx,selected:xxx}}
        #         如果不存在
        # 5   获取商品的所有的id  [id,id,id]
        # 6   再根据id获取商品的详细信息 [sku,sku,sku,sku]
        # 7   将对象列表转换为字典
        # 8   返回相应
    """

    def get(self,request):

        # 1. 获取用户信息
        user = request.user
        # 2. 判断用户信息
        if user is not None and user.is_authenticated:

            # 3. 登陆用户从redis中获取数据
            #     3.1 连接redis
            redis_conn = get_redis_connection('cart')
            #     3.2 获取redis的数据 hash set  sku_id:count,sku_id:count ,
            # hash
            # {sku_id:count,sku_id:count}
            redis_ids_count = redis_conn.hgetall('cart_%s'%user.id)

            #set
            # {sku_id,sku_id}
            redis_selected_ids = redis_conn.smembers('cart_selected_%s'%user.id)

            # 额外做一部,统一数据格式
            # 将redis数据转换为 cookie数据格式

            cookie_cart = {}
            #{sku_id:{count:xxx,selected:xxx}}
            # 对redis数据进行遍历
            for id,count in redis_ids_count.items():

                # 判断 遍历的id 是否在 选中的列表中
                if id in redis_selected_ids:
                    selected=True
                else:
                    selected=False

                cookie_cart[id] = {
                    'count':count,
                    # 'selected': id in redis_selected_ids
                    'selected': selected
                }


        else:

            # 4. 未登录用户从cookie中获取数据
            #     4.1 从cookie中获取数据
            cookie_str = request.COOKIES.get('cart')
            #     4.2 判断数据是否存在
            if cookie_str is not None:
            #         如果存在则要进行 解码
            # {sku_id:{count:xxx,selected:xxx}}
                cookie_cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                #         如果不存在
                cookie_cart = {}


        # 5   获取商品的所有的id  [id,id,id]
        # 获取字典中的所有key
        ids = cookie_cart.keys()
        # 6   再根据id获取商品的详细信息 [sku,sku,sku,sku]
        skus = SKU.objects.filter(pk__in=ids)

        # 额外添加一部 ,对列表数据进行遍历 ,动态添加 count和selected

        # {sku_id:{count:xxx,selected:xxx}}
        # 从 cookie_cart 中获取 count和 selected
        for sku in skus:
            sku.count = cookie_cart[sku.id]['count']
            sku.selected = cookie_cart[sku.id]['selected']

        # 7   将对象列表转换为字典
        serializer = CartSKUSerializer(skus,many=True)
        # 8   返回相应
        return Response(serializer.data)


