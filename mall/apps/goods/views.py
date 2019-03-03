from django.shortcuts import render

# Create your views here.
from goods.models import SKU
from goods.serializers import SKUSerialzier


class Person(object):

    name = ''
    sex = ''


p = Person()
p.name='aaa'


"""
设置表的思想是:
不要上来就定义模型,要先分析
1. 尽量多的分析字段,而且将比较明显的表分析出来(不要分析表和表之间的关系)
2. 找一个安静的没有人打扰的时候,分析表和表之间的关系 (分析的时候,就分析2个表之间的分析)

"""


"""

热销商品
需求:
    当用户点击某一个分类的时候,需要获取 这个分类的热销数据

步骤:
    1. 接收分类id
    2. 校验数据
    3. 根据分类id查询数据(排序,获取指定条数的数据)  [SKU,SKU,SKU]
    4. 创建序列化器,将对象列表转换为字典
    5. 返回相应
请求方式和路由
    GET      /goods/categories/(?P<category_id>\d+)/hotskus/

    GET     /goods/hotskus/?cat_id=xxx

    POST    /goods/hotskus/         body

视图:
    APIView
    GeneriAPIVIew
    ListAPIView,RetrieveAPIView

编码:

"""
from rest_framework.generics import ListAPIView
class HotsSKUListAPIView(ListAPIView):

    pagination_class = None

    #GET      /goods/categories/(?P<category_id>\d+)/hotskus/

    serializer_class = SKUSerialzier

    # queryset = SKU.objects.filter(category_id=self.categroy_id)

    def get_queryset(self):
        category_id = self.kwargs['category_id']

        return SKU.objects.filter(category_id=category_id,is_launched=True).order_by('-sales')[:2]
        # SKU.obects.filter(category_id=category_id).order_by('-sales')[0:2]
        # pass


    # def get(self,request,category_id):


    # pass

"""
解决问题的思路:  把复杂的问题 简单化
                简单的问题 先实现 ,再一点一点的实现复杂的

"""

from rest_framework.pagination import PageNumberPagination




from rest_framework.generics import GenericAPIView

class SKUListAPIView(ListAPIView):

    serializer_class = SKUSerialzier

    #添加排序
    from rest_framework.filters import OrderingFilter
    filter_backends = [OrderingFilter]
    #添加排序字段
    ordering_fields=['sales','price','create_time']

    #添加分页
    # pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        category_id = self.kwargs['category_id']

        return SKU.objects.filter(category_id=category_id, is_launched=True)



from .serializers import SKUIndexSerializer
from drf_haystack.viewsets import HaystackViewSet

class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer

