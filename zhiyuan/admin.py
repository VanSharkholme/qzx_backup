from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError
from .models import StudentUser, Vol_Proj, Organize


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
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('stu_id', 'stu_name', 'stu_time')   # 显示的字段
    list_filter = ('is_admin', 'is_active')  # 通过这些字段筛选
    search_fields = ('stu_name', 'stu_id')  # 通过这些字段搜索

    fieldsets = (   # 显示的字段
        (None, {'fields': ('stu_id', 'stu_name', 'password')}),
        ('学生信息', {'fields': ('email', 'phone')}),
        ('志愿信息', {'fields': ('stu_time', 'proj')}),
        ('权限设置', {'fields': ('is_active', 'is_admin')}),
    )
    add_fieldsets = (
        (None, {'fields': ('stu_id', 'stu_name', 'password1', 'password2')}),
        ('学生信息', {'fields': ('email', 'phone')}),
        ('志愿信息', {'fields': ('stu_time', 'proj')}),
        ('权限设置', {'fields': ('is_active', 'is_admin')}),
    )
    filter_horizontal = ()

    ordering = ('stu_id',)  # 按学号排序


admin.site.register(StudentUser, UserAdmin)
admin.site.register(Vol_Proj)
admin.site.register(Organize)

admin.site.unregister(Group)
