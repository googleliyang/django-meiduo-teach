from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView

"""
第一步：创建应用
    在沙箱环境中已经有 appid了
第二步：配置密钥
    在沙箱环境中 需要配置 2对秘钥
    1对在我们的服务器上
        一个公钥 (保存在支付宝的服务器上)
        一个私钥 (保存在我们的服务器上)
    另外1对在支付宝服务器上
        一个公钥(我们需要在沙箱中复制到我们自己的服务器上)
        一个私钥(保存在支付宝的服务器上)

第三步：搭建和配置开发环境

第四步：接口调用
"""

"""
需求:     当用户点击支付宝去支付的时候,应该出现支付宝的支付界面

    我们通过 读取 接口文档 发现 需要让前端传递 订单id 给后端

    后端才可以根据订单 获取订单金额 ,从而生成 order_string


思路:
    这个接口 必须是登陆用户调用

    1.接收订单order_id
    2.根据订单id查询订单信息(金额 订单的支付状态,订单的支付方式)
    3. 创建alipay实例对象
    4. 调用alipay的支付接口 生成 order_string
    5. 拼接支付的url

请求方式和路由

    GET     /pay/orders/(?P<order_id>)\d+/


"""
class PayUrlAPIView(APIView):

    def get(self,request,order_id):

        pass