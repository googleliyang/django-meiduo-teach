from decimal import Decimal
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


from orders.models import OrderInfo
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
                Redis hash sku_id:count
                        set sku_id

                获取商品信息
                计算商品数量和价格
                更新订单的数量和价格

    """
    def create(self, validated_data):
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

        pass
