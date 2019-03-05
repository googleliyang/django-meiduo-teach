import re
from django_redis import get_redis_connection

from rest_framework import serializers

from goods.models import SKU
from users.models import User, Address
# serializers.ModelSerializer
# serializers.Serializer
from users.utils import generate_verify_url

"""
用户名,手机号,密码,确认密码,短信验证码,是否同意协议
"""
# 你课下写序列化器的时候 直接从我的笔记里 把代码赋值过来,不要按照我上课的思路自己写
class RegisterUserSerializer(serializers.ModelSerializer):

    password2=serializers.CharField(max_length=20,min_length=8,write_only=True,required=True,label='确认密码')
    sms_code=serializers.CharField(max_length=6,min_length=6,write_only=True,required=True,label='短信验证码')
    allow=serializers.CharField(required=True,write_only=True,label='是否同意协议')

    # token 是在序列化的时候 使用,在反序列化的时候 默认忽略
    # token = serializers.CharField()

    token = serializers.CharField(read_only=True)
    # password

    #write_only	表明该字段仅用于反序列化输入，默认False
    # 在序列化的时候 默认 忽略

    # 以上的三个字段 ,我们的期望只是在验证的时候 传入
    # 我们在进行 序列化(对象转字典)操作的时候,忽略这3个字段('allow','password2','sms_code')


    class Meta:
        model = User
        fields = ['username','mobile','password','allow','token','password2','sms_code']
        extra_kwargs = {
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    """
    ModelSerializer 自动生成 字段的原理是:
    根据 fields 中的字段,先到当前序列化中查询是否有自己实现的字段,
    如果有就不去模型中自动生成了
    如果没有,则去模型中查找,是否有一致对应的字段,有则生成,没有则报错

    """

    """
    验证数据:
        1.字段类型
        2.字段选项
        3.单个字段
        4.多个字段
    """

    #单个字段校验 手机号格式,是否同意协议
    def validate_mobile(self,value):

        #校验手机号
        if not re.match(r'1[3-9]\d{9}',value):
            raise serializers.ValidationError('手机号不满足规则')

        return value

    def validate_allow(self,value):

        if value != 'true':
            raise serializers.ValidationError('您未同意协议')

        return value
    #多个字段校验 密码和确认密码,短信验证码
    # def validate(self, data):
    def validate(self, attrs):

        #1.密码和确认密码
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password!=password2:
            raise serializers.ValidationError('密码不一致')

        # 2.短信验证码
        # 2.1 用户提交的短信
        sms_code = attrs.get('sms_code')
        #2.2 获取redis的短信
        #① 连接redis
        redis_conn = get_redis_connection('code')
        # ② 获取数据
        mobile = attrs.get('mobile')
        redis_code = redis_conn.get('sms_%s'%mobile)
        # ③ 判断数据是否存在(有有效期)
        if redis_code is None:
            raise serializers.ValidationError('短信验证码已过期')
        #2.3 比对
        if redis_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码输入错误')

        return attrs


    def create(self, validated_data):

        del validated_data['sms_code']
        del validated_data['allow']
        del validated_data['password2']

        user = User.objects.create(**validated_data)
        # 修改密码
        user.set_password(validated_data.get('password'))
        # 修改完模型的数据之后,要记得保存模型
        user.save()

        # 1.用户注册完成之后
        # 2.生成一个token

        from rest_framework_jwt.settings import api_settings

        #① 获取 jwt的2个方法
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        #② 将user信息 传递给 payload方法
        payload = jwt_payload_handler(user)

        #③ 对payload返回的数据进行编码,编码之后就是token
        token = jwt_encode_handler(payload)


        # 3.将token返回给前端
        # 让序列化器 来获取token

        user.token = token


        return user


# class Person(object):
#
#     name = 'itcast'
#
# p = Person()
#
# p.name = 'abc'
# p.age = 10
#
# p2 = Person()
# print(p2.age)

# serializers.ModelSerializer
# serializers.Serializer

class UserCenterInfoSerializer(serializers.ModelSerializer):



    class Meta:
        model = User
        fields = ['username','mobile','email','id','email_active']


class UserEmailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['email']

        extra_kwargs = {
            'email':{
                'required':True
            }
        }



    #保存完邮件信息之后

    def update(self, instance, validated_data):
        # instance = user
        #接收邮件信息
        email = validated_data.get('email')
        instance.email=email
        instance.save()

        #在这里发送邮件

        # from django.core.mail import send_mail
        # # send_mail(subject, message, from_email, recipient_list,)
        # # subject,          主题
        # subject = '美多商场激活邮件'
        # # message,          内容
        # message = ''
        # # from_email,       谁发送的
        # # 谁发送的
        # from_email = 'qi_rui_hua@163.com'
        # # recipient_list    收件人列表
        # recipient_list=[email]
        #
        # #生成一个激活的url
        # verify_url = generate_verify_url(instance.id,email)
        #
        # # from mall import settings
        # # from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
        # #
        # # s = Serializer(secret_key=settings.SECRET_KEY,expires_in=3600)
        # #
        # # token = s.dumps({'id':instance.id,'email':email})
        # #
        # #
        # # verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=%s'%token.decode()
        #
        #
        # html_message = '<p>尊敬的用户您好！</p>' \
        #                '<p>感谢您使用美多商城。</p>' \
        #                '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
        #                '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
        #
        # send_mail(subject,message,from_email,recipient_list,
        #           html_message=html_message)



        from celery_tasks.email.tasks import send_active_email

        send_active_email.delay(email,instance.id)

        return instance

class AddressSerializer(serializers.ModelSerializer):
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)

    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')


    def create(self, validated_data):
        # self.context 二级视图 自动的添加

        user = self.context['request'].user
        validated_data['user_id']=user.id

        # address = Address.objects.create(**validated_data)
        # return address

        address =  super().create(validated_data)
        return address

        # user = request.user
        # user_id = user.id

        # validated_data 缺少user_id的信息

        # print('aaa')
        # pass

######################################################

from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mall import settings

# 1. 创建序列化器
s = Serializer(secret_key=settings.SECRET_KEY,expires_in=300)

#2.组织数据
data = {
    'id':10,
    'email':'qi_rui_hua@163.com'
}

#3.对数据进行加密
token = s.dumps(data)



s.loads(token)



######################用户浏览记录#######################

class UserHistorySerializer(serializers.Serializer):

    sku_id = serializers.IntegerField(label='商品id',required=True)

    def validate_sku_id(self,value):

        # 校验 商品是否存在
        try:
            SKU.objects.get(pk=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')

        return value

    # def validate(self, attrs):
    #     pass
    # 因为我们是保存在redis中 ,所以 不能使用 ModelSerialzier 的create方法
    # 因为  ModelSerialzier 的create方法 是将数据保存在 数据库中
    def create(self, validated_data):

        user = self.context['request'].user
        sku_id = validated_data.get('sku_id')

        #1. 连接redis
        redis_conn = get_redis_connection('history')
        #2. 保存数据
        #2.1 我们在保存之前,先删掉 列表中可能存在的数据
        # [ 1,3,4,1,5,1,3,1]
        #
        redis_conn.lrem('history_%s'%user.id,0,sku_id)
        #2.2 再添加
        # 从左边加 ,因为左边都是最新的
        redis_conn.lpush('history_%s'%user.id,sku_id)

        #2.3 我们只需要保存 5条记录
        redis_conn.ltrim('history_%s'%user.id,0,4)

        return validated_data


class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')



