from django.contrib import admin

from login.models import *

# Register your models here.


admin.site.site_title = "自习室预约管理系统"
admin.site.site_header = "自习室预约管理系统"
admin.site.index_title = "自习室预约管理系统"


class StudentsManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('name', 'phone')
    list_display = ['id', 'name', 'phone', 'email', 'preferred_room', 'study_preference', 'time', 'is_active', 'admin_sample']


class BookingsManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('students', 'number')
    list_display = ['id', 'students', 'number', 'room', 'period', 'time', 'is_active', 'admin_sample']


class RoomsManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('name',)
    search_fields = ('name',)
    list_display = ['id', 'name', 'number', 'time', 'is_active', 'admin_sample']


class IntegralsManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('student',)
    list_display = ['id', 'student', 'title', 'text', 'time', 'is_active', 'admin_sample']


class BlacklistManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('student__name', 'reason')
    list_display = ['id', 'student', 'reason', 'start_time', 'end_time', 'is_active']
    list_filter = ['is_active', 'start_time']
    autocomplete_fields = ['student']


class UserEvaluationManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('student__name', 'room__name', 'comment')
    list_display = ['id', 'student', 'room', 'rating', 'time', 'is_active', 'is_approved']
    list_filter = ['rating', 'is_active', 'is_approved', 'time']
    autocomplete_fields = ['student', 'room']


class UserComplaintManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('student__name', 'title', 'content')
    list_display = ['id', 'student', 'complaint_type', 'title', 'status', 'time', 'is_active']
    list_filter = ['complaint_type', 'status', 'is_active', 'time']
    autocomplete_fields = ['student']


class ComplaintFeedbackManager(admin.ModelAdmin):
    # 列表页显示那些字段
    search_fields = ('complaint__title', 'admin_user', 'feedback_content')
    list_display = ['id', 'complaint', 'admin_user', 'feedback_time', 'is_active']
    list_filter = ['is_active', 'feedback_time']
    autocomplete_fields = ['complaint']


admin.site.register(Students, StudentsManager)
admin.site.register(Rooms, RoomsManager)
admin.site.register(Bookings, BookingsManager)
admin.site.register(Integrals, IntegralsManager)
admin.site.register(Blacklist, BlacklistManager)
admin.site.register(UserEvaluation, UserEvaluationManager)
admin.site.register(UserComplaint, UserComplaintManager)
admin.site.register(ComplaintFeedback, ComplaintFeedbackManager)
