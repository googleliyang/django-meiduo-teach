from django.shortcuts import render
from rest_framework.views import APIView

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

    def post(self,request):

        print(request.user)
        pass

