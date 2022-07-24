from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from .models import StudentUser, Vol_Proj, Organize
from django.urls import path
import re
import datetime
import pandas as pd
import zhiyuan
from django.shortcuts import render
from .forms import UserImportForm


# Register your models here.

# 管理员站点中新增用户的表单重写
class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='密码', widget=forms.PasswordInput)
    password2 = forms.CharField(label='确认密码', widget=forms.PasswordInput)

    class Meta:
        model = StudentUser
        fields = ('stu_id', 'stu_name', 'stu_class', 'email', 'phone')  # 创建用户要填写的字段

    def clean_password2(self):  # 确保两次输入的密码一致
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("两次密码不一致")
        return password2

    def save(self, commit=True):  # 将数据保存到数据库
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# 修改用户表单
class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = StudentUser
        fields = ('stu_id', 'stu_name', 'stu_class', 'email')


# 管理员站点页面用户模型显示
class UserAdmin(BaseUserAdmin):
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import', self.admin_site.admin_view(self.user_import))
        ]
        return my_urls + urls

    def user_import(self, request):
        if request.method == 'POST':
            form = UserImportForm(request.POST)
            xlsx = pd.read_excel(request.FILES['xlsx'], sheet_name='Sheet1', skiprows=1)
            cname = {}
            for name in xlsx.columns:
                if re.search(r'姓名', name):
                    cname['姓名'] = name
                if re.search(r'学院', name):
                    cname['学院'] = name
                if re.search(r'班级', name):
                    cname['班级'] = name
                if re.search(r'学号', name):
                    cname['学号'] = name
                if re.search(r'联系', name):
                    cname['用户手机'] = name
                if re.search(r'时长', name):
                    cname['时长'] = name
                if re.search(r'名称', name):
                    cname['项目名称'] = name
                if re.search(r'类别', name):
                    cname['项目类别'] = name
                if re.search(r'单位', name):
                    cname['举办单位'] = name
                if re.search(r'负责人姓名', name):
                    cname['负责人姓名'] = name
                if re.search(r'负责人电话', name):
                    cname['负责人电话'] = name
                if re.search(r'QQ|qq', name):
                    cname['负责人qq'] = name
                if re.search(r'备注', name):
                    cname['备注'] = name
                if re.search(r'日期', name):
                    cname['日期'] = name
            # data = []
            for i in xlsx.index:
                row = xlsx.iloc[i]
                if pd.isnull(row['学号']):
                    continue
                stunum = int(row['学号'])
                user_phone = str(row[cname['用户手机']].astype('int64'))[:11]
                org_phone = str(row[cname['负责人电话']].astype('int64'))[:11]
                org_qq = str(row[cname['负责人qq']].astype('int64'))
                # data.append(list(xlsx.iloc[i]))

                default_email = str(stunum) + "@mail.ecust.edu.cn"
                default_password = 'S' + str(stunum)
                try:
                    stu = StudentUser.objects.get(stu_id=stunum)
                    print(stu.stu_name)
                except StudentUser.DoesNotExist:
                    StudentUser.objects.create_user(stunum, row['姓名'], default_email, default_password)
                    stu = StudentUser.objects.get(stu_id=stunum)
                    print('user created')

                date = row[cname['日期']]
                print(type(row[cname['日期']]))
                start = {}
                end = {}
                begin = datetime.datetime.now().date()
                last = datetime.datetime.now().date()
                try:
                    if re.search(r'-', date):
                        date = str(date).split('-')
                        start['year'] = int(re.search(r'[0-9]{4}(?=年)', date[0]).group())
                        start['month'] = int(re.search(r'[0-9]{1,2}(?=月)', date[0]).group())
                        start['day'] = int(re.search(r'[0-9]{1,2}(?=日)', date[0]).group())
                        try:
                            end['year'] = int(re.search(r'[0-9]{4}(?=年)', date[1]).group())
                        except AttributeError:
                            end['year'] = start['year']
                        end['month'] = int(re.search(r'[0-9]{1,2}(?=月)', date[1]).group())
                        end['day'] = int(re.search(r'[0-9]{1,2}(?=日)', date[1]).group())
                        begin = datetime.date(start['year'], start['month'], start['day'])
                        last = datetime.date(end['year'], end['month'], end['day'])
                except TypeError:
                    begin = last = date.date()

                try:
                    new_proj = Vol_Proj.objects.filter(proj_name=row[cname['项目名称']]).filter(commence_date=begin).get(
                        end_date=last)
                    stu.proj.add(new_proj)
                except zhiyuan.models.Vol_Proj.DoesNotExist:
                    try:
                        org = Organize.objects.filter(department=row[cname['举办单位']]).get(organizer=row[cname['负责人姓名']])
                    except Organize.DoesNotExist:
                        org = Organize.objects.create(
                            department=row[cname['举办单位']],
                            organizer=row[cname['负责人姓名']],
                            organizer_qq=org_qq,
                            organizer_phone=org_phone
                        )

                        pass
                    new_proj = Vol_Proj.objects.create(
                        proj_name=row[cname['项目名称']],
                        proj_time=row[cname['时长']],
                        category=row[cname['项目类别']],
                        commence_date=begin,
                        end_date=last,
                        org=org
                    )
                    stu.proj.add(new_proj)
                if not stu.phone:
                    stu.phone = user_phone
                if not stu.stu_class:
                    stu.stu_class = row[cname['班级']]
                if not stu.stu_academy:
                    stu.stu_academy = row[cname['学院']]
                vol_pks = list(Vol_Proj.objects.filter(STU__stu_id=stu.stu_id))
                # 计算总时长
                totaltime = 0
                for item in vol_pks:
                    totaltime += item.proj_time
                stu.stu_time = totaltime
                stu.save()

                # for j in range(1, len(data[i])):
                #     print(data[i][j])
                # print(data[i][4])

                print('==========line%d==========' % i)
            print("=========all done!!!!=========")
        else:
            form = UserImportForm()
        return render(request, '../templates/import/form.html', {'form': form})

    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('stu_id', 'stu_name', 'stu_time')  # 显示的字段
    list_filter = ('is_admin', 'is_active')  # 通过这些字段筛选
    search_fields = ('stu_name', 'stu_id')  # 通过这些字段搜索

    fieldsets = (  # 显示的字段
        (None, {'fields': ('stu_id', 'stu_name')}),
        ('学生信息', {'fields': ('email', 'phone', 'stu_academy', 'stu_class')}),
        ('志愿信息', {'fields': ('stu_time', 'proj')}),
        ('权限设置', {'fields': ('is_active', 'is_admin')}),
    )
    add_fieldsets = (
        (None, {'fields': ('stu_id', 'stu_name', 'password1', 'password2')}),
        ('学生信息', {'fields': ('email', 'phone', 'stu_academy', 'stu_class')}),
        ('志愿信息', {'fields': ('stu_time', 'proj')}),
        ('权限设置', {'fields': ('is_active', 'is_admin')}),
    )
    filter_horizontal = ['proj']
    ordering = ('stu_id',)  # 按学号排序


class ProjAdmin(admin.ModelAdmin):
    search_fields = ['proj_name', 'org__organizer']
    date_hierarchy = 'commence_date'
    autocomplete_fields = ['org']
    list_display = ('proj_name', 'proj_time', 'org', 'commence_date', 'end_date')
    ordering = ('proj_time', 'commence_date', 'end_date')


class OrgAdmin(admin.ModelAdmin):
    search_fields = ['organizer', 'department']
    list_display = ['department', 'organizer', 'organizer_phone', 'organizer_qq']


admin.site.register(StudentUser, UserAdmin)
admin.site.register(Vol_Proj, ProjAdmin)
admin.site.register(Organize, OrgAdmin)

admin.site.unregister(Group)
