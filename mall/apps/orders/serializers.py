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


        pass
