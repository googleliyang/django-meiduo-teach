from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import OrderInfo
from pay.models import Payment

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
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from alipay import AliPay
from mall import settings

class PayUrlAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request,order_id):
        # 1.接收订单order_id
        # 2.根据订单id查询订单信息(金额 订单的支付状态,订单的支付方式)
        try:
            # 为了让订单查询的更准确,我们需要再额外添加 几个查询条件
            # 1.查询未支付的
            # 2.用户
            order = OrderInfo.objects.get(order_id=order_id,
                                          status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'],
                                          user=request.user)
        except OrderInfo.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 3. 创建alipay实例对象


        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()


        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug = settings.DEBUG  # 默认False
        )

        # 4. 调用alipay的支付接口 生成 order_string
        # 如果你是 Python 3的用户，使用默认的字符串即可
        subject = "测试订单"

        # 电脑网站支付，需要跳转到https://openapi.alipay.com/gateway.do? + order_string
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(order.total_amount), # decemal 需要转换为字符串
            subject=subject,
            return_url="http://www.meiduo.site:8080/pay_success.html"
        )

        #app_id=2016091600523030&biz_content=%7B%22subject%22%3A%22%5Cu6d4b%5Cu8bd5%5Cu8ba2%5Cu5355%22%2C%22out_trade_no%22%3A%2220190308040334000000010%22%2C%22total_amount%22%3A%2234164.00%22%2C%22product_code%22%3A%22FAST_INSTANT_TRADE_PAY%22%7D&charset=utf-8&method=alipay.trade.page.pay&return_url=http%3A%2F%2Fwww.meiduo.site%3A8080%2Fpay_success.html&sign_type=RSA2&timestamp=2019-03-08+16%3A31%3A56&version=1.0&sign=fAZ1mvP9No1Yfo1vqBiUn4MEFwp37qaVffm8Qsa2vS5LXXXwpogJYbO%2FNsvUHzVswCawjqaeodzl6iXvPNxj1GYb0Lm4T7mO3m%2F9odRF9pzs0GOJrXvxAyzBHYGjriJiljZAxlgcu%2BLZ2uUOsqZB1Stb96etP3wZEtkWPQ8lBUnECb8z1Au%2FXcw%2Bl4x%2F3Zg4ojSC4eiUPbG1ZebR7XCfdQSnEIQL59affczuPGFRxBwcGcFl2aWc3mSy55v6EslfzjgI7aSsOtiKdNDQRRkcYM8OGtcUts6maLNiK3wjKsoctltIQTyURQJVRNh33hEk5WGdDsa5G82g3VvxrMOq3A%3D%3D

        # 5. 拼接支付的url
        alipay_url = 'https://openapi.alipaydev.com/gateway.do?' + order_string

        return Response({'alipay_url':alipay_url})


    """
    当支付成功之后,在回调页面的请求参数中 有我们需要的数据 (支付宝的交易流水号和商户的交易id)
    这个时候 让前端 传递给后端

    思路:
        1. 接收数据
        2. 按照支付宝的文档进行校验
        3.如果支付成功,则将 支付宝流水号和商品交易号保存起来
        4. 更新一下订单的状态

        put   /pay/stuts/?key=xxxx...
    """
class PayStatusAPIView(APIView):

    def put(self,request):


        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()

        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=settings.DEBUG  # 默认False
        )


        data = request.query_params.dict()
        # sign 不能参与签名验证
        signature = data.pop("sign")


        # verify
        success = alipay.verify(data, signature)
        if success:
            # 成功
            # 获取 支付宝的交易流水号 和 商家的交易流水号
            # trade_no 支付宝
            # out_trade_no 商家
            trade_no = data.get('trade_no')
            out_trade_no = data.get('out_trade_no')

            Payment.objects.create(
                order_id=out_trade_no,
                trade_id=trade_no
            )


            # 更新订单的状态
            # OrderInfo.objects.filter(order_id=out_trade_no).update(status=2)
            OrderInfo.objects.filter(order_id=out_trade_no).update(status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])

            return Response({'trade_id':trade_no})
        else:
            # 失败
            return Response(status=status.HTTP_400_BAD_REQUEST)



