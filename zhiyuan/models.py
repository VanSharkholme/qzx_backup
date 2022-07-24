from datetime import date
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


# Create your models here.

# 用户管理器
class CustomUserManager(BaseUserManager):
    # 重写createuser命令
    def create_user(self, stu_id, stu_name, email, password=None):
        if not stu_id:
            raise ValueError('请输入学号')
        if not stu_name:
            raise ValueError('请输入学生姓名')
        if not email:
            raise ValueError('请输入邮箱，用于找回密码')

        user = self.model(
            stu_id=stu_id,
            stu_name=stu_name,
            email=self.normalize_email(email),

        )
        user.set_password(password)
        user.save(using=self.db)
        return user

    # 重写createsuperuser命令
    def create_superuser(self, stu_id, stu_name, email, password=None):
        user = self.create_user(
            stu_id,
            stu_name,
            email,
            password=password
        )
        user.is_admin = True
        user.save(using=self.db)
        return user


# 用户模型
class StudentUser(AbstractBaseUser):
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    stu_id = models.CharField(
        max_length=10,
        verbose_name="学号",
        unique=True,
    )

    stu_name = models.CharField(
        max_length=20,
        verbose_name="姓名",
    )

    stu_academy = models.CharField(
        max_length=50,
        verbose_name="学院",
        blank=True
    )

    stu_class = models.CharField(
        max_length=20,
        verbose_name="班级",
        blank=True,
    )

    stu_time = models.FloatField(
        verbose_name="个人志愿总时长",
        default=0,
    )

    email = models.EmailField(
        verbose_name="email",
    )

    phone = models.CharField(
        verbose_name="学生手机号",
        max_length=11,
        blank=True
    )

    proj = models.ManyToManyField(
        to="Vol_Proj",
        verbose_name="志愿项目",
        related_name="STU",
        blank=True
    )
    # 用户权限设置
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = CustomUserManager()

    # 以学号作为登录验证
    USERNAME_FIELD = 'stu_id'
    EMAIL_FIELD = 'email'
    # 设置非空字段
    REQUIRED_FIELDS = ['stu_name', 'email']

    def get_short_name(self):
        return self.stu_name

    def __str__(self):
        return self.stu_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


# 定义志愿项目模型
class Vol_Proj(models.Model):
    class Meta:
        verbose_name = '志愿项目'
        verbose_name_plural = '志愿项目'

    proj_name = models.CharField(
        verbose_name="志愿项目名称",
        max_length=100,
    )

    proj_time = models.FloatField(
        verbose_name="计入时长",
        default=0,
    )

    category = models.CharField(
        max_length=100,
        verbose_name='项目类型',
    )

    commence_date = models.DateField(
        default=date.today,
        verbose_name="项目开始日期",
    )

    end_date = models.DateField(
        default=date.today,
        verbose_name="项目结束日期",
    )

    org = models.ForeignKey(
        to='Organize',
        verbose_name='负责单位及人员信息',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.proj_name


# 定义负责单位模型
class Organize(models.Model):
    class Meta:
        verbose_name = '负责单位及人员信息'
        verbose_name_plural = '负责单位及人员信息'

    department = models.CharField(
        max_length=200,
        verbose_name='负责单位',
    )

    organizer = models.CharField(
        max_length=30,
        verbose_name='负责人姓名'
    )

    organizer_phone = models.CharField(
        max_length=11,
        verbose_name='负责人手机号'
    )

    organizer_qq = models.CharField(
        max_length=20,
        verbose_name='负责人QQ'
    )

    def __str__(self):
        return self.department + self.organizer
