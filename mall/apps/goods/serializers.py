from rest_framework import serializers

# SKU
from goods.models import SKU


class SKUSerialzier(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')