from django.db import models
from django.utils.safestring import mark_safe


# 学生表
class Students(models.Model):
    id = models.AutoField(verbose_name="编号", primary_key=True)
    name = models.CharField(verbose_name="姓名", max_length=22, default='')
    password = models.CharField(verbose_name="密码", max_length=128, default='')
    phone = models.CharField(verbose_name="手机号", max_length=11, default='')
    email = models.CharField(verbose_name="邮箱", max_length=22, default='')
    time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    photo = models.FileField(verbose_name="头像", default='', upload_to="Students/photo/")
    last_login = models.DateTimeField(verbose_name="上次登录", null=True, blank=True)
    # integral = models.IntegerField(verbose_name="积分", default=100)
    is_active = models.BooleanField(verbose_name="活跃状态", default=True)
    
    # 新增字段：常用自习室偏好
    preferred_room = models.ForeignKey(verbose_name="常用自习室", to='Rooms', on_delete=models.SET_NULL, 
                                       null=True, blank=True)
    
    # 新增字段：个人简介
    bio = models.TextField(verbose_name="个人简介", max_length=500, default='', blank=True)
    
    # 新增字段：学习偏好
    study_preference = models.CharField(verbose_name="学习偏好", max_length=50, choices=[
        ('quiet', '安静学习'),
        ('group', '小组讨论'),
        ('flexible', '灵活适应'),
        ('other', '其他')
    ], default='quiet', blank=True)

    def admin_sample(self):
        return mark_safe('<img src="/media/%s" height="60" width="60" />' % (self.photo,))

    admin_sample.short_description = '  学生图片'
    admin_sample.allow_tags = True

    def __str__(self):
        return self.name

    class Meta:
        # 数据库列表名
        db_table = 'Students'
        # 后台管理名
        verbose_name_plural = '学生管理'

    # def viewed(self):
    #     """
    #     增加阅读数
    #     :return:
    #     """
    #     self.traffic += 1
    #     self.save(update_fields=['traffic'])


# 自习室
class Rooms(models.Model):
    id = models.AutoField(verbose_name="编号", primary_key=True)
    name = models.CharField(verbose_name="名称", max_length=22, default='')
    number = models.IntegerField(verbose_name="座位数量", default=0)
    photo = models.FileField(verbose_name="头像", default='', upload_to="Room/photo/")
    time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    is_active = models.BooleanField(verbose_name="活跃状态", default=True)

    def admin_sample(self):
        return mark_safe('<img src="/media/%s" height="60" width="60" />' % (self.photo,))

    admin_sample.short_description = '  学生图片'
    admin_sample.allow_tags = True

    def __str__(self):
        return self.name

    class Meta:
        # 数据库列表名
        db_table = 'Room'
        # 后台管理名
        verbose_name_plural = '自习室管理'


# 预约管理
class Bookings(models.Model):
    id = models.AutoField(verbose_name="编号", primary_key=True)
    students = models.ForeignKey(verbose_name="学生", to='Students', null=True, on_delete=models.CASCADE)
    number = models.IntegerField(verbose_name="预约座位号", default=0)
    room = models.ForeignKey(verbose_name="自习室", to='Rooms', on_delete=models.CASCADE, null=True)
    # 1.上午 2.下午 3.晚自习
    time_choice = (
        (1, '上午'),
        (2, '下午'),
        (3, '晚自习'),
    )
    is_choice = (
        (1, "预约"),
        (2, "已签到"),
        (3, "未签到"),
        (4, "已取消")
    )
    period = models.IntegerField(verbose_name="时间段", choices=time_choice, default=1)
    time = models.DateTimeField(verbose_name="预约时间", auto_now_add=True)
    # 新增：预约日期（要去自习室的日期）
    booking_date = models.DateField(verbose_name="预约日期", null=True, blank=True)
    is_active = models.IntegerField(verbose_name="活跃状态", choices=is_choice, default=1)

    def __str__(self):
        return self.students.name

    class Meta:
        # 数据库列表名
        db_table = 'Booking'
        # 后台管理名
        verbose_name_plural = '预约管理'

    def admin_sample(self):
        return mark_safe('<img src="/media/%s" height="60" width="60" />' % (self.students.photo,))

    admin_sample.short_description = '  学生图片'
    admin_sample.allow_tags = True


# 警告管理
class Integrals(models.Model):
    id = models.AutoField(verbose_name="编号", primary_key=True)
    student = models.ForeignKey(verbose_name="学生", to='Students', on_delete=models.CASCADE)
    # integral = models.IntegerField(verbose_name="扣积分", default=0)
    title = models.CharField(verbose_name="警告题目", max_length=220, default='')
    text = models.TextField(verbose_name="警告内容内容", max_length=220, default='')
    time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    is_active = models.BooleanField(verbose_name="活跃状态", default=True)

    def __str__(self):
        return self.student.name

    class Meta:
        # 数据库列表名
        db_table = 'Integral'
        # 后台管理名
        verbose_name_plural = '扣积分管理'

    def admin_sample(self):
        return mark_safe('<img src="/media/%s" height="60" width="60" />' % (self.student.photo,))

    admin_sample.short_description = '  学生图片'
    admin_sample.allow_tags = True


# 签到码
class SignCode(models.Model):
    id = models.AutoField(verbose_name="编号", primary_key=True)
    text = models.TextField(verbose_name="内容", default='')
    time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    is_active = models.BooleanField(verbose_name="活跃状态", default=True)

    def __str__(self):
        return self.text

    class Meta:
        # 数据库列表名
        db_table = 'sign_code'
        # 后台管理名
        verbose_name_plural = '签到码'


def __str__(self):
    return self.admin_sample


# 用户评价管理
class UserEvaluation(models.Model):
    id = models.AutoField(verbose_name="编号", primary_key=True)
    student = models.ForeignKey(verbose_name="学生", to='Students', on_delete=models.CASCADE)
    room = models.ForeignKey(verbose_name="自习室", to='Rooms', on_delete=models.CASCADE)
    rating = models.IntegerField(verbose_name="评分", choices=[(1, '1星'), (2, '2星'), (3, '3星'), (4, '4星'), (5, '5星')], default=5)
    comment = models.TextField(verbose_name="评价内容", default='')
    time = models.DateTimeField(verbose_name="评价时间", auto_now_add=True)
    is_active = models.BooleanField(verbose_name="活跃状态", default=True)
    is_approved = models.BooleanField(verbose_name="审核状态", default=False)

    def __str__(self):
        return f"{self.student.name} - {self.room.name}"

    class Meta:
        db_table = 'user_evaluation'
        verbose_name_plural = '用户评价管理'


# 用户投诉管理
class UserComplaint(models.Model):
    id = models.AutoField(verbose_name="编号", primary_key=True)
    student = models.ForeignKey(verbose_name="投诉学生", to='Students', on_delete=models.CASCADE)
    complaint_type = models.CharField(verbose_name="投诉类型", max_length=50, choices=[
        ('facility', '设施问题'),
        ('service', '服务问题'),
        ('environment', '环境问题'),
        ('other', '其他问题')
    ], default='other')
    title = models.CharField(verbose_name="投诉标题", max_length=100, default='')
    content = models.TextField(verbose_name="投诉内容", default='')
    time = models.DateTimeField(verbose_name="投诉时间", auto_now_add=True)
    status = models.CharField(verbose_name="处理状态", max_length=20, choices=[
        ('pending', '待处理'),
        ('processing', '处理中'),
        ('resolved', '已解决'),
        ('closed', '已关闭')
    ], default='pending')
    is_active = models.BooleanField(verbose_name="活跃状态", default=True)

    def __str__(self):
        return f"{self.student.name} - {self.title}"

    class Meta:
        db_table = 'user_complaint'
        verbose_name_plural = '用户投诉管理'


# 投诉反馈信息
class ComplaintFeedback(models.Model):
    id = models.AutoField(verbose_name="编号", primary_key=True)
    complaint = models.ForeignKey(verbose_name="投诉记录", to='UserComplaint', on_delete=models.CASCADE)
    admin_user = models.CharField(verbose_name="处理管理员", max_length=50, default='')
    feedback_content = models.TextField(verbose_name="反馈内容", default='')
    feedback_time = models.DateTimeField(verbose_name="反馈时间", auto_now_add=True)
    is_active = models.BooleanField(verbose_name="活跃状态", default=True)

    def __str__(self):
        return f"{self.complaint.title} - 反馈"

    class Meta:
        db_table = 'complaint_feedback'
        verbose_name_plural = '投诉反馈信息'


# 黑名单管理
class Blacklist(models.Model):
    id = models.AutoField(verbose_name="编号", primary_key=True)
    student = models.ForeignKey(verbose_name="学生", to='Students', on_delete=models.CASCADE)
    reason = models.TextField(verbose_name="拉黑原因", default='')
    start_time = models.DateTimeField(verbose_name="开始时间", auto_now_add=True)
    end_time = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)
    is_active = models.BooleanField(verbose_name="活跃状态", default=True)

    def __str__(self):
        return f"{self.student.name} - 黑名单"

    class Meta:
        db_table = 'blacklist'
        verbose_name_plural = '黑名单管理'


# 黑名单撤销申请
class BlacklistRemovalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('approved', '已批准'),
        ('rejected', '已拒绝'),
    ]
    
    id = models.AutoField(verbose_name="编号", primary_key=True)
    blacklist = models.ForeignKey(verbose_name="黑名单记录", to='Blacklist', on_delete=models.CASCADE)
    student = models.ForeignKey(verbose_name="学生", to='Students', on_delete=models.CASCADE)
    appeal_reason = models.TextField(verbose_name="申诉理由")
    status = models.CharField(verbose_name="审核状态", max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(verbose_name="申请时间", auto_now_add=True)
    reviewed_at = models.DateTimeField(verbose_name="审核时间", null=True, blank=True)
    admin_comment = models.TextField(verbose_name="管理员备注", blank=True)

    def __str__(self):
        return f"{self.student.name} - 黑名单撤销申请"

    class Meta:
        db_table = 'blacklist_removal_request'
        verbose_name_plural = '黑名单撤销申请'
