
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
"""

def merge_cookie_to_redis():

    """
    1.获取cookie数据
    2.获取redis 数据
    3.对redis的数据进行转换
    4. 合并前初始化记录 ( 保留redis的数据, 初始化一个选中的id列表)
    5. 合并
    6. 将合并的数据保存到redis中
    """