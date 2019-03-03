from django.shortcuts import render

# Create your views here.

"""
为什么要用静态化
    1. 首页访问是最频繁的
    2. 如果采用原有的方式:
        ① 查询数据库
        ② 将数据动态填充到html中
        会大大降低性能以及用户体验


    问题:
         经常查询数据库,对数据库压力比较大
         将数据动态填充到html中影响用户的体验
    解决:
        ① 针对于 经常查询的数据 可以做缓存处理
        针对与 第二个问题,我们作为后端,没有特别直接的解决方案
        ② 我们把 数据查询出来,然后填充好了,再让用户访问


静态化
     当用户访问我们的页面的时候,我们已经提前准备好了html页面,让用户直接访问就可以了


步骤:
    1.数据查询出来
    2.填充模板
    3.保存到指定的目录


"""

"""
列表页面的静态化

    1.列表页面的 分类需要做静态化
    2. 针对于页面中的用户交互的变化我们通过ajax来动态交互

    3. 列表页面不建议采用定时任务
        ① 频次 不好判定
        ② 应该在 分类数据修改(包括添加)的时候 应该重新生成
        ③ 就是我们在修改(包括添加) admin 后台分类数据的时候 触发 重新生成 列表页面

"""