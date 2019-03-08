from decimal import Decimal

from django_redis import get_redis_connection
from rest_framework import serializers

from goods.models import SKU


class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')

"""
{
  "freight": 10,
  "skus": [
    {
      "id": 1,
      "name": "Apple MacBook Pro 13.3英寸笔记本 银色",
    },
  ]
}
"""

class PlaceOrderSerialzier(serializers.Serializer):

    freight = serializers.DecimalField(label='运费',decimal_places=2,max_digits=10)
    skus = CartSKUSerializer(many=True)


from orders.models import OrderInfo, OrderGoods


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }


    """
    订单保存
        1. 先生成订单信息
            OrderInfo
            1.1 获取用户信息 V
            1.2 获取地址信息 V
            1.3 订单id     V
            1.4 总数量,总价格,运费 V
                先把数量和总价格定义为0
            1.5 支付方式    V
            1.6 订单状态    V

        2. 再保存商品信息
            OrderGoods

                1.Redis
                2.hash    sku_id:count
                3.set     sku_id
                4.在将redis的数据类型转换过程中,重新构造一个 选中的信息
                    redis_selecteds = {sku_id:count}
                5. 根据id获取商品信息 [sku,sku,sku,sku]
                6. 遍历商品列表
                    7. 判断购买量和库存的关系
                    8. 库存减少,销量增加
                    9. 累加商品数量和价格(将累加计算的值 更新到订单信息中)
                    10. 保存订单商品


                更新订单的数量和价格

    """
    def create(self, validated_data):


        # 前边省略了很多数据库的操作




        # 1. 先生成订单信息
        #     OrderInfo
        #     1.1 获取用户信息
        user = self.context['request'].user
        #     1.2 获取地址信息 V
        address = validated_data.get('address')
        #     1.3 订单id     V
        # 年月日时分秒 + 用户id(9位)
        from django.utils import timezone
        # Y Year
        # m month
        # d day
        # H Hour
        # M Minute
        # S Second
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + '%09d'%user.id
        #     1.4 总数量,总价格,运费 V
        #         先把数量和总价格定义为0
        total_count = 0
        total_amount = Decimal('0')
        freight = Decimal('10.00')
        #     1.5 支付方式    V
        # 1 表示 货到付款
        # 2 表示 支付宝
        pay_method = validated_data.get('pay_method')
        #     1.6 订单状态    V
        # 订单状态是根据支付方式来决定的
        # if pay_method == 1:
        #     status = 2
        # else:
        #     status = 1

        # cash 是现金的意思
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        # 部分代码使用事务
        from django.db import transaction

        with transaction.atomic():

            # 事务的开始的点
            save_point = transaction.savepoint()

            order = OrderInfo.objects.create(
                order_id=order_id,
                user = user,
                address=address,
                total_count=total_count,
                total_amount=total_amount,
                freight=freight,
                pay_method=pay_method,
                status=status
            )

            # 1.Redis
            redis_conn = get_redis_connection('cart')
            # 2.hash    sku_id:count
            # {sku_id:count}
            redis_id_counts = redis_conn.hgetall('cart_%s'%user.id)
            # 3.set     sku_id
            # [id,id,id]
            redis_selected_ids = redis_conn.smembers('cart_selected_%s'%user.id)

            # 4.在将redis的数据类型转换过程中,重新构造一个 选中的信息
            redis_selecteds = {}
            for sku_id in redis_selected_ids:
                redis_selecteds[int(sku_id)]=int(redis_id_counts[sku_id])

            #     redis_selecteds = {sku_id:count}
            # 5. 根据id获取商品信息 [sku,sku,sku,sku]

            ids = redis_selecteds.keys()
            skus = SKU.objects.filter(pk__in=ids)


            # 6. 遍历商品列表
            for sku in skus:
                #     7. 判断购买量和库存的关系
                count = redis_selecteds[sku.id]
                if sku.stock < count:

                    # 这里可能失败
                    # 回滚到我们记录的那个事务点
                    transaction.savepoint_rollback(save_point)

                    raise serializers.ValidationError('库存不足')

                #     8. 库存减少,销量增加
                import time
                time.sleep(7)

                # sku.stock -= count
                # sku.sales += count
                # sku.save()

                # 乐观锁

                # 1. 先查询(记录)一次 库存
                old_stock = sku.stock           # 10

                # 2. 我们把更新的数据 先计算出来

                new_stock = sku.stock-count
                new_sales= sku.sales + count

                #3. 更新的时候再查询一次,如果一致则更新
                # 更新操作会返回受影响的行数 1 表示更新成功
                # 0 表示更新失败
                result = SKU.objects.filter(pk=sku.id,stock=old_stock).update(stock=new_stock,
                                                                     sales=new_sales)

                if result == 0:
                    #说明更新失败了
                    # 说明下单失败了
                    transaction.savepoint_rollback(save_point)
                    raise serializers.ValidationError('下单失败')



                #     9. 累加商品数量和价格(将累加计算的值 更新到订单信息中)
                order.total_count += count
                order.total_amount += (count*sku.price)
                #     10. 保存订单商品
                OrderGoods.objects.create(
                    order = order,
                    sku=sku,
                    count=count,
                    price=sku.price
                )

            # 因为我们在遍历商品信息的时候 对数量和价格进行了累加计算
            order.save()

            transaction.savepoint_commit(save_point)

        return order

"""
               乐观锁
肉包子      10                 3

甲       先查询一次: 10
        更新数据的时候,再查询一次: 10   10==10  10-7=3


乙       先查询一次: 10
        更新数据的时候,再查询一次: 3        10 != 3  不操作数据了


乙       先查询一次: 3
        更新数据的时候,再查询一次: 3        3 == 3  操作数据了

"""