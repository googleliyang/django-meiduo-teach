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
