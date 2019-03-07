from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView

from goods.models import SKU
from orders.serializers import CartSKUSerializer, PlaceOrderSerialzier, OrderSerializer

"""
提交订单界面的展示

需求:
    1.必须是登陆用户才可以访问此界面(用户地址信息确定的)
    当登陆用户访问此界面的时候,需要让前端将用户信息传递给后端

思路:
    # 1.接收用户信息,并验证用户信息
    # 2.根据用户信息获取redis中选中商品的id  [id,id,id]
    # 3.根据id获取商品的详细信息 [sku,sku,sku]
    # 4.将对象列表转换为字典
    # 5.返回相应

请求方式和路由
    GET     orders/placeorders/



"""
from rest_framework.permissions import IsAuthenticated
class PlaceOrderAPIView(APIView):

    # 接收用户信息
    # 添加权限
    permission_classes = [IsAuthenticated]

    def get(self,request):
        # 1.接收用户信息, 并验证用户信息
        user = request.user
        # 2.根据用户信息获取redis中选中商品的id  [id,id,id]
        redis_conn = get_redis_connection('cart')

        # hash   {sku_id:count }
        redis_id_counts = redis_conn.hgetall('cart_%s'%user.id)
        # set
        redis_selected_ids = redis_conn.smembers('cart_selected_%s'%user.id)

        # 类型的转换, 在类型转换过程中,我们重新组织(获取)选中的商品的信息

        redis_selected_cart = {}
        # {sku_id:count}
        for sku_id in redis_selected_ids:
            redis_selected_cart[int(sku_id)] = int(redis_id_counts[sku_id])

        ids = redis_selected_cart.keys()
        # 3.根据id获取商品的详细信息 [sku,sku,sku]
        skus = SKU.objects.filter(pk__in=ids)

        for sku in skus:
            sku.count = redis_selected_cart[sku.id]
        # 4.将对象列表转换为字典
        # serializer = CartSKUSerializer(skus,many=True)
        # 5.返回相应

        # 钱
        # 最好使用 货比类型
        from decimal import Decimal

        # 100/3 = 33.33    33.33   33.33  33.34
        freight = Decimal('10.00')

        # data = {
        #     'skus':serializer.data,
        #     'freight':freight
        # }
        # return Response(data)

        serializer = PlaceOrderSerialzier({'freight':freight,
                                           'skus':skus})

        return Response(serializer.data)
"""
[
  {
    "id": 1,
    "name": "Apple MacBook Pro 13.3英寸笔记本 银色",
    "default_image_url": "http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrPB4GAWkTlAAGuN6wB9fU4220429",
    "price": "11388.00",
    "count": 11
  },
  {
    "id": 10,
    "name": "华为 HUAWEI P10 Plus 6GB+128GB 钻雕金 移动联通电信4G手机 双卡双待",
    "default_image_url": "http://image.meiduo.site:8888/group1/M00/00/02/CtM3BVrRchWAMc8rAARfIK95am88158618",
    "price": "3788.00",
    "count": 1
  }
]

{
    skus: serializer.data,
    运费:10
}


"""

"""
提交订单

需求:
    当用户点击提交按钮的时候,我们需要让前端 将 用户信息, 地址,支付方式 提交给后端

步骤:
    1. 接收数据
    2. 验证数据
    3. 数据入库
    4. 返回相应

请求方式和路由
    POST  orders/


"""
class OrderAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self,request):

        # 1. 接收数据
        data = request.data
        # 2. 验证数据
        serializer = OrderSerializer(data=data)
        serializer.is_valid()
        # 3. 数据入库
        serializer.save()
        # 4. 返回相应
        return Response(serializer.data)


