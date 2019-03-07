
"""
需求:
    登陆实现 cookie数据的合并redis
步骤:
    登陆
    1.获取cookie数据
        {sku_id:{count:xxx,selected:xxx},}

        {1: {count:10,selected:True}, 3:{count:30,selected:False}}

    2.获取redis (从redis服务器上将数据获取下来,不要通过redis代码来判断,
                因为判断会增加redids服务器的交互)
        hash:   {sku_id:count}
                {b'2':b'20',b'3':b'100'}
        set:    {sku_id}
                {2,3}

        我们把最终的数据再更新到 redis中
        最终的: {2:20,3:30,1:10}
        选中的: {1}
    3.合并



    cookie数据
        {1: {count:10,selected:True}, 3:{count:30,selected:False}}

    redis数据
        hash:  {2:20,3:100}
        set:   {2,3}

    合并前初始化记录 ( redis的数据 原则是不动的)
        cart = {2:20,3:100}
        cart_selected = {}

    合并
        1: {count:10,selected:True}
            cart = {2:20,3:100} + {1:10}
            cart_selected = {1}

        3:{count:30,selected:False}
            cart = {2:20,3:30} + {1:10}
            cart_selected = {1}


    最终的数据
        cart = {2:20,3:30,1:10}
        cart_selected = {1}

"""
import pickle

import base64
from django_redis import get_redis_connection


def merge_cookie_to_redis(request,user,response):

    """
    1.获取cookie数据
    2.获取redis 数据
    3.对redis的数据进行转换
    4. 合并前初始化记录 ( 保留redis的数据, 初始化一个选中的id列表)
    5. 合并
    6. 将合并的数据保存到redis中
    """

    # 1.获取cookie数据
    cookie_str = request.COOKIES.get('cart')
    if cookie_str is not None:
        #说明有数据
        cookie_cart =  pickle.loads(base64.b64decode(cookie_str))
        # {1: {count:10,selected:True}, 3:{count:30,selected:False}}

        # 2.获取redis 数据
        redis_conn = get_redis_connection('cart')

        # user = request.user
        #hash
        redis_id_counts = redis_conn.hgetall('cart_%s'%user.id)
        # {b'2':b'20',b'3':b'100'}

        # 3.对redis的数据进行转换
        redis_cart = {}
        for sku_id,count in redis_id_counts.items():
            redis_cart[int(sku_id)]=int(count)

        # redis_cart
        #{2:20,3:100}

        # 4. 合并前初始化记录 ( 保留redis的数据, 初始化一个选中的id列表)
        cookie_selected_ids = []

        # 5. 合并
        # {1: {count:10,selected:True}, 3:{count:30,selected:False}}

        for sku_id,count_selected_dict in cookie_cart.items():
            # if sku_id in redis_cart:
            #     redis_cart[sku_id]=count_selected_dict['count']
            # else:

            redis_cart[sku_id]=count_selected_dict['count']

            # 选中的状态
            if count_selected_dict['selected']:
                cookie_selected_ids.append(sku_id)

        # 6. 将合并的数据保存到redis中
        # 更新 hash
        # redis_cart = {sku_id:count,sku_id:count}
        redis_conn.hmset('cart_%s'%user.id,redis_cart)


        # 保存选中的id
        # cookie_selected_ids = [1,2,3,4]
        redis_conn.sadd('cart_selected_%s'%user.id,*cookie_selected_ids)

        # 7. cookie数据删除
        # response.delete_cookie('cart')

        # 相应对象我们只是使用一下,一定要返回
        return response

    return response
