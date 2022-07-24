import csv
import re
import datetime
import pandas as pd
import zhiyuan
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .forms import UserImportForm
from .models import StudentUser, Vol_Proj, Organize


# Create your views here.
# 反馈部分
def feedback(request):
    # 通过POST获取用户输入的内容
    msg = request.POST.get('feedback')
    # print(msg)
    li = []
    f = open("feedback.csv", 'a+', newline='')
    # 获取当前用户名（学号）
    cur_username = request.user.get_username()
    # 若已登录则在csv中记录学号和姓名
    if cur_username:
        u = StudentUser.objects.get(stu_id=cur_username)
        li.append(u.stu_name)
        li.append(u.stu_id)
    # 否则不记录
    else:
        li.append(' ')
        li.append(' ')
    li.append(msg)
    writer = csv.writer(f)
    writer.writerow(li)
    f.close()
    # print(msg)
    # message = '提交成功'
    # context = {'message': message}
    return render(request, 'zhiyuan/Feedback.html')


# 只有在登录状态下才能访问志愿时长
@login_required
def time(request):
    # 获取用户名
    cur_username = request.user.get_username()
    # 在数据库中查找对应当前用户的数据
    u = StudentUser.objects.get(stu_id=cur_username)
    # 计算记录总数
    record_num = u.proj.count()
    # 在志愿项目模型中查找多对多键(学号)为当前用户学号的信息并放入list
    vol_pks = list(Vol_Proj.objects.filter(STU__stu_id=u.stu_id))
    # 计算总时长
    totaltime = u.stu_time
    # 将需要传至网页的内容放入context字典以通过render函数传递
    context = {
        'username': u.stu_name,
        'record_num': record_num,
        'vol_pks': vol_pks,
        'totaltime': totaltime,
    }
    return render(request, 'zhiyuan/Time.html', context)


# 获取部门信息
def department(request):
    id = request.GET.get('id')
    dirt = Organize.objects.filter(department=id)
    return render(request, 'zhiyuan/department.html', {"dirt": dirt})

# 批量导入用户
