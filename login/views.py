from django.urls import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
import json
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
# 移除对已删除的 tokens 模块的导入
# from .tokens import student_token_generator
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.core.exceptions import ValidationError
import random
import string
from datetime import datetime, timedelta, timezone as dt_timezone
import csv
import io
<<<<<<< HEAD
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import letter
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# from reportlab.lib import colors
# from reportlab.lib.units import inch
=======
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
>>>>>>> d3fdd8f653273883590632b92fe29518c3bf8876

from login.models import *
# 在现有导入语句后添加
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.db.models.functions import TruncHour, TruncDay, TruncWeek

# Create your views here.
@csrf_exempt
def login(request):
    print(">>> Entering login view <<<") # 添加入口打印
    path_url = '/' # Default redirect URL
    msg = None     # Initialize error message

    if request.method == 'POST':
        # 尝试从 POST 表单获取数据
        name = request.POST.get('name')
        password = request.POST.get('password')
        # 获取之前尝试访问的路径，作为登录后重定向的目标
        path_url = request.POST.get('path_url', '/') 

        if name and password: # Ensure name and password are provided
            try:
                user = Students.objects.get(name=name)
                
                # 支持哈希密码和明文密码两种验证方式
                login_successful = False
                password_needs_upgrade = False
                
                # 1. 尝试使用 check_password (适用于哈希密码)
                if check_password(password, user.password):
                    login_successful = True
                    print("Password check successful (hashed)")
                else:
                    # 2. 如果 check_password 失败，尝试明文比较 (兼容老账户)
                    if '$' not in user.password and user.password == password:
                        login_successful = True
                        password_needs_upgrade = True # 标记需要升级密码
                        print("Password check successful (plaintext) - upgrading hash.")
                    else:
                        print("Password incorrect")
                
                if login_successful:
                    # 如果是明文密码登录，立即升级为哈希
                    if password_needs_upgrade:
                        user.password = make_password(password)
                        # 在保存密码的同时更新 last_login，减少一次 save()
                        user.last_login = timezone.now()
                        user.save(update_fields=['password', 'last_login'])
                        print(f"Password for user {user.name} upgraded to hash.")
                    else:
                        # 如果密码已经是哈希，只更新 last_login
                        user.last_login = timezone.now()
                        user.save(update_fields=['last_login'])
                    
                    # 设置 session
                    request.session['name'] = {"name": user.name, "photo": str(user.photo)}
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['photo'] = str(user.photo)

                    print(f"Login successful for {name} via standard login form.")
                    # 重定向到最初请求的路径，如果没有则重定向到首页
                    # 如果 path_url 为空或'/', 则重定向到 '/index/' 可能更合适
                    redirect_target = path_url if path_url and path_url != '/' else '/index/'
                    return HttpResponseRedirect(redirect_target)
                else:
                    # 密码错误
                    print(f"Password incorrect for {name} via standard login form.")
                    msg = "账号或密码错误！！"
            except Students.DoesNotExist:
                # 用户不存在
                print(f"User {name} not found via standard login form.")
                msg = "账号或密码错误！！"
            except Exception as e:
                # 其他可能的错误
                print(f"Error during login for {name}: {e}")
                msg = "登录过程中发生错误，请稍后重试。"
        else:
            msg = "请输入用户名和密码。"

        # 登录失败，重新渲染登录页面并显示错误信息
        return render(request, 'login/login.html', {"msg": msg, "path_url": path_url})

    else:
        # GET 请求，显示登录页面
        # 获取 'path' 参数，如果存在的话
        path_url = request.GET.get('path', '/')
        return render(request, 'login/login.html', {"path_url": path_url})


def reginter(request):
    if request.method == 'POST':
        name = request.POST['name']
        password = request.POST['password']
        phone = request.POST['phone']
        email = request.POST['email']
        photo = request.FILES.get('photo')
        try:
            stu = Students.objects.filter(is_active=True, name=name)
        except Exception as e:
            print(e)
        if stu:
            msg = '用户已存在！'
            return render(request, 'login/register.html', {"msg": msg})
        else:
            try:
                stu = Students.objects.create(
                    name=name,
                    password=password,
                    phone=phone,
                    email=email,
                    photo=photo
                )
            except Exception as e:
                print(e)
            msg = "注册成功！"
            return render(request, 'login/login.html', {"msg": msg})

    return render(request, 'login/register.html')


def pswd_update(request):
    if request.method == "POST":
        name = request.session['name']
        password_1 = request.POST["password_1"]
        password_2 = request.POST["password_2"]

        try:
            stu = Students.objects.get(name=name['name'])
        except Exception as e:
            print(e)
        if stu.password == password_1:
            stu.password = password_2
            stu.save()
            return HttpResponseRedirect("/login/")
        else:
            msg = "账号或密码错误！"
            return render(request, 'login/pswd_update.html', {"msg": msg})
    else:
        return render(request, 'login/pswd_update.html')


def logout(request):
    """退出登录视图"""
    # 清除所有会话数据
    if 'name' in request.session:
        del request.session['name']
    if 'is_login' in request.session:
        del request.session['is_login']
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'photo' in request.session:
        del request.session['photo']

    # 检查是否是 AJAX 请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'redirect_url': '/login/'  # 重定向到Django登录页面
        })
    else:
        # 对于普通请求，直接重定向到Django登录页面
        return HttpResponseRedirect('/login/')


def index(request):
    bookings_url = reverse('Bookings')  # 确保这里使用了正确的名称
    return render(request, 'index/index.html', {'bookings_url': bookings_url})


def admin_login(request):
    """管理员登录视图 - 使用Django的admin认证系统"""
    # 如果用户已经通过Django认证，直接重定向到admin后台
    if request.user.is_authenticated and request.user.is_staff:
        request.session['is_admin'] = True
        request.session['admin_name'] = {"name": request.user.username}
        return HttpResponseRedirect('/admin/')
    
    msg = None
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # 使用Django的认证系统
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            # 使用Django的login函数，这样admin系统就能识别
            auth_login(request, user)
            # 设置管理员会话标识
            request.session['is_admin'] = True
            request.session['admin_name'] = {"name": user.username}
            return HttpResponseRedirect('/admin/')
        else:
            msg = "账号不存在或不是管理员！"
            return render(request, 'login/admin_login.html', {"msg": msg})
    
    return render(request, 'login/admin_login.html')


def admin_dashboard(request):
    """管理员后台仪表板"""
    # 检查管理员权限：Django认证或自定义会话
    if not (request.user.is_authenticated and request.user.is_staff) and not request.session.get('is_admin'):
        return redirect('/login/admin/')
    
    # 如果通过Django认证但自定义会话未设置，则设置自定义会话
    if request.user.is_authenticated and request.user.is_staff and not request.session.get('is_admin'):
        request.session['is_admin'] = True
        request.session['admin_name'] = {"name": request.user.username}
    
    # 获取统计数据
    total_users = Students.objects.filter(is_active=True).count()
    total_complaints = UserComplaint.objects.count()
    pending_complaints = UserComplaint.objects.filter(status='pending').count()
    blacklisted_users = Blacklist.objects.filter(is_active=True).count()
    
    # 获取最近的投诉记录
    recent_complaints = UserComplaint.objects.all().order_by('-time')[:5]
    
    context = {
        'total_users': total_users,
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'blacklisted_users': blacklisted_users,
        'recent_complaints': recent_complaints
    }
    
    return render(request, 'admin/dashboard.html', context)


@csrf_exempt
def api_login(request):
    if request.method == 'POST':
        try:
            print("Received login request with headers:", request.headers)
            data = json.loads(request.body)
            print("Received data:", data)
            
            name = data.get('name')
            password = data.get('password') # 用户输入的明文密码
            print(f"Attempting login for user: {name}")
            
            try:
                user = Students.objects.get(name=name)
                print(f"Found user: {user.name}, checking password")
                
                login_successful = False
                password_needs_upgrade = False

                # 1. 尝试使用 check_password (适用于哈希密码)
                if check_password(password, user.password):
                    login_successful = True
                    print("Password check successful (hashed)")
                else:
                    # 2. 如果 check_password 失败，尝试明文比较 (兼容老账户)
                    #    注意：这里假设老密码不包含 Django 哈希算法前缀 (如 pbkdf2_sha256$)
                    #    如果老密码可能包含 '$'，这个判断需要更健壮
                    if '$' not in user.password and user.password == password:
                        login_successful = True
                        password_needs_upgrade = True # 标记需要升级密码
                        print("Password check successful (plaintext) - upgrading hash.")
                    else:
                        print("Password incorrect")

                # 如果登录成功 (无论是哈希还是明文)
                if login_successful:
                    # 如果是明文密码登录，立即升级为哈希
                    if password_needs_upgrade:
                        user.password = make_password(password)
                        # 在保存密码的同时更新 last_login，减少一次 save()
                        user.last_login = timezone.now()
                        user.save(update_fields=['password', 'last_login'])
                        print(f"Password for user {user.name} upgraded to hash.")
                        print(f"Updated last_login for user {user.name}")
                    else:
                        # 如果密码已经是哈希，只更新 last_login
                        user.last_login = timezone.now()
                        user.save(update_fields=['last_login'])
                        print(f"Updated last_login for user {user.name}")
                    
                    # 设置session
                    request.session['name'] = {"name": user.name, "photo": str(user.photo)}
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['photo'] = str(user.photo)
                    
                    response_data = {
                        'success': True,
                        'user': {
                            'id': user.id,
                            'username': user.name,
                            'photo': str(user.photo)
                        },
                        'redirect_url': 'http://localhost:8000/index/'  # 或者根据需要重定向到前端页面
                    }
                    print(f"Login successful, sending response: {response_data}")
                    return JsonResponse(response_data)
                else:
                    # 如果两种方式都验证失败
                    return JsonResponse({
                        'success': False,
                        'message': '用户名或密码错误' 
                    }, status=401)
                    
            except Students.DoesNotExist:
                print(f"User not found: {name}")
                return JsonResponse({
                    'success': False,
                    'message': '用户名或密码错误' 
                }, status=401)
                
        except json.JSONDecodeError as e:
            print(f"Invalid JSON data: {e}")
            return JsonResponse({
                'success': False,
                'message': '无效的请求数据'
            }, status=400)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'服务器错误: {str(e)}'
            }, status=500)
            
    return JsonResponse({
        'success': False,
        'message': '不支持的请求方法'
    }, status=405)


@csrf_exempt
def user_info(request):
    """获取当前登录用户信息"""
    if request.method == 'GET':
        if 'user_id' in request.session:
            try:
                user = Students.objects.get(id=request.session['user_id'])
                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.name,
                        'photo': str(user.photo)
                    }
                })
            except Students.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': '用户不存在'
                }, status=404)
        return JsonResponse({
            'success': False,
            'message': '未登录'
        }, status=401)
    return JsonResponse({
        'success': False,
        'message': '不支持的请求方法'
    }, status=405)


@csrf_exempt
def api_admin_login(request):
    """管理员登录API - 使用Django的admin认证系统"""
    if request.method == 'POST':
        try:
            print("Received admin login request with headers:", request.headers)
            data = json.loads(request.body)
            print("Received data:", data)
            
            username = data.get('name')
            password = data.get('password')
            print(f"Attempting admin login for user: {username}")
            
            # 使用Django的认证系统
            user = authenticate(request, username=username, password=password)
            
            if user is not None and user.is_staff:
                # 使用Django的login函数，这样admin系统就能识别
                auth_login(request, user)
                
                response_data = {
                    'success': True,
                    'user': {
                        'id': user.id,
                        'username': user.username,
                    },
                    'redirect_url': 'http://localhost:8000/admin/'
                }
                print(f"Admin login successful, sending response: {response_data}")
                return JsonResponse(response_data)
            else:
                print("Admin authentication failed")
                return JsonResponse({
                    'success': False,
                    'message': '账号不存在或不是管理员'
                }, status=401)
                
        except json.JSONDecodeError as e:
            print(f"Invalid JSON data: {e}")
            return JsonResponse({
                'success': False,
                'message': '无效的请求数据'
            }, status=400)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JsonResponse({
                'success': False,
                'message': f'服务器错误: {str(e)}'
            }, status=500)
            
    return JsonResponse({
        'success': False,
        'message': '不支持的请求方法'
    }, status=405)


# ==================== 用户管理模块 ====================

def user_dashboard(request):
    """用户个人中心首页"""
    if not request.session.get('is_login'):
        return redirect('/login/')
    
    user_id = request.session.get('user_id')
    try:
        user = Students.objects.get(id=user_id)
        
        # 获取用户最近的评价记录
        recent_evaluations = UserEvaluation.objects.filter(student=user).order_by('-time')[:5]
        
        # 获取用户最近的投诉记录
        recent_complaints = UserComplaint.objects.filter(student=user).order_by('-time')[:5]
        
        # 获取用户预约统计
        total_bookings = Bookings.objects.filter(students=user).count()
        completed_bookings = Bookings.objects.filter(students=user, is_active=2).count()  # 已签到
        
        # 检查用户是否在黑名单中
        is_blacklisted = Blacklist.objects.filter(student=user, is_active=True).exists()
        
        # 获取学习偏好显示文本
        study_preference_display = dict([
            ('quiet', '安静学习'),
            ('group', '小组讨论'),
            ('flexible', '灵活适应'),
            ('other', '其他')
        ]).get(user.study_preference, '未设置')
        
        context = {
            'user': user,
            'recent_evaluations': recent_evaluations,
            'recent_complaints': recent_complaints,
            'total_bookings': total_bookings,
            'completed_bookings': completed_bookings,
            'is_blacklisted': is_blacklisted,
            'study_preference_display': study_preference_display
        }
        
        return render(request, 'user_management/dashboard.html', context)
        
    except Students.DoesNotExist:
        return redirect('/login/')


def user_profile(request):
    """用户个人信息管理"""
    if not request.session.get('is_login'):
        return redirect('/login/')
    
    user_id = request.session.get('user_id')
    try:
        user = Students.objects.get(id=user_id)
        
        # 获取所有自习室用于选择
        rooms = Rooms.objects.filter(is_active=True)
        
        if request.method == 'POST':
            # 处理个人信息更新
            name = request.POST.get('name')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            bio = request.POST.get('bio', '')
            preferred_room_id = request.POST.get('preferred_room')
            study_preference = request.POST.get('study_preference', 'quiet')
            photo = request.FILES.get('photo')
            
            # 更新用户信息
            user.name = name
            user.phone = phone
            user.email = email
            user.bio = bio
            user.study_preference = study_preference
            
            # 处理常用自习室
            if preferred_room_id:
                try:
                    preferred_room = Rooms.objects.get(id=preferred_room_id)
                    user.preferred_room = preferred_room
                except Rooms.DoesNotExist:
                    user.preferred_room = None
            else:
                user.preferred_room = None
                
            if photo:
                user.photo = photo
            
            user.save()
            
            # 更新session中的用户信息
            request.session['name'] = {"name": user.name, "photo": str(user.photo)}
            request.session['photo'] = str(user.photo)
            
            messages.success(request, '个人信息更新成功')
            return redirect('user_profile')
        
        context = {
            'user': user,
            'rooms': rooms
        }
        
        return render(request, 'user_management/profile.html', context)
        
    except Students.DoesNotExist:
        return redirect('/login/')


def user_evaluations(request):
    """用户评价管理"""
    if not request.session.get('is_login'):
        return redirect('/login/')
    
    user_id = request.session.get('user_id')
    try:
        user = Students.objects.get(id=user_id)
        
        # 获取用户的所有评价记录
        evaluations = UserEvaluation.objects.filter(student=user).order_by('-time')
        
        if request.method == 'POST':
            # 处理新评价提交
            room_id = request.POST.get('room_id')
            rating = request.POST.get('rating')
            comment = request.POST.get('comment')
            
            try:
                room = Rooms.objects.get(id=room_id)
                evaluation = UserEvaluation.objects.create(
                    student=user,
                    room=room,
                    rating=rating,
                    comment=comment
                )
                messages.success(request, '评价提交成功')
                return redirect('user_evaluations')
            except Rooms.DoesNotExist:
                messages.error(request, '自习室不存在')
        
        # 获取可评价的自习室列表
        rooms = Rooms.objects.filter(is_active=True)
        
        context = {
            'user': user,
            'evaluations': evaluations,
            'rooms': rooms
        }
        
        return render(request, 'user_management/evaluations.html', context)
        
    except Students.DoesNotExist:
        return redirect('/login/')


def user_complaints(request):
    """用户投诉管理"""
    if not request.session.get('is_login'):
        return redirect('/login/')
    
    user_id = request.session.get('user_id')
    try:
        user = Students.objects.get(id=user_id)
        
        # 获取用户的所有投诉记录
        complaints = UserComplaint.objects.filter(student=user).order_by('-time')
        
        if request.method == 'POST':
            # 处理新投诉提交
            complaint_type = request.POST.get('complaint_type')
            title = request.POST.get('title')
            content = request.POST.get('content')
            
            complaint = UserComplaint.objects.create(
                student=user,
                complaint_type=complaint_type,
                title=title,
                content=content,
                status='pending'
            )
            messages.success(request, '投诉提交成功')
            return redirect('user_complaints')
        
        context = {
            'user': user,
            'complaints': complaints
        }
        
        return render(request, 'user_management/complaints.html', context)
        
    except Students.DoesNotExist:
        return redirect('/login/')


def complaint_feedback(request, complaint_id):
    """投诉反馈详情"""
    if not request.session.get('is_login'):
        return redirect('/login/')
    
    try:
        complaint = UserComplaint.objects.get(id=complaint_id)
        feedbacks = ComplaintFeedback.objects.filter(complaint=complaint).order_by('-feedback_time')
        
        context = {
            'complaint': complaint,
            'feedbacks': feedbacks
        }
        
        return render(request, 'user_management/complaint_feedback.html', context)
        
    except UserComplaint.DoesNotExist:
        messages.error(request, '投诉记录不存在')
        return redirect('user_complaints')


# ==================== 管理员用户管理模块 ====================

def admin_user_management(request):
    """管理员用户管理"""
    # 检查管理员权限：Django认证或自定义会话
    if not (request.user.is_authenticated and request.user.is_staff) and not request.session.get('is_admin'):
        return redirect('/login/admin/')
    
    # 如果通过Django认证但自定义会话未设置，则设置自定义会话
    if request.user.is_authenticated and request.user.is_staff and not request.session.get('is_admin'):
        request.session['is_admin'] = True
        request.session['admin_name'] = {"name": request.user.username}
    
    # 获取所有用户
    users = Students.objects.filter(is_active=True).order_by('-time')
    
    # 获取黑名单用户
    blacklisted_users = Blacklist.objects.filter(is_active=True)
    
    context = {
        'users': users,
        'blacklisted_users': blacklisted_users
    }
    
    return render(request, 'admin/user_management.html', context)


def admin_complaint_management(request):
    """管理员投诉管理"""
    # 检查管理员权限：Django认证或自定义会话
    if not (request.user.is_authenticated and request.user.is_staff) and not request.session.get('is_admin'):
        return redirect('/login/admin/')
    
    # 如果通过Django认证但自定义会话未设置，则设置自定义会话
    if request.user.is_authenticated and request.user.is_staff and not request.session.get('is_admin'):
        request.session['is_admin'] = True
        request.session['admin_name'] = {"name": request.user.username}
    
    # 获取所有投诉记录
    complaints = UserComplaint.objects.all().order_by('-time')
    
    context = {
        'complaints': complaints
    }
    
    return render(request, 'admin/complaint_management.html', context)


def admin_complaint_detail(request, complaint_id):
    """管理员投诉详情"""
    # 检查管理员权限：Django认证或自定义会话
    if not (request.user.is_authenticated and request.user.is_staff) and not request.session.get('is_admin'):
        return redirect('/login/admin/')
    
    # 如果通过Django认证但自定义会话未设置，则设置自定义会话
    if request.user.is_authenticated and request.user.is_staff and not request.session.get('is_admin'):
        request.session['is_admin'] = True
        request.session['admin_name'] = {"name": request.user.username}
    
    try:
        complaint = UserComplaint.objects.get(id=complaint_id)
        feedbacks = ComplaintFeedback.objects.filter(complaint=complaint).order_by('-feedback_time')
        
        if request.method == 'POST':
            # 处理投诉状态更新和反馈
            status = request.POST.get('status')
            feedback_content = request.POST.get('feedback_content')
            
            # 更新投诉状态
            complaint.status = status
            complaint.save()
            
            # 添加反馈
            if feedback_content:
                admin_user = request.session.get('admin_name', {}).get('name', '管理员')
                ComplaintFeedback.objects.create(
                    complaint=complaint,
                    admin_user=admin_user,
                    feedback_content=feedback_content
                )
            
            messages.success(request, '投诉处理成功')
            return redirect('admin_complaint_detail', complaint_id=complaint_id)
        
        context = {
            'complaint': complaint,
            'feedbacks': feedbacks
        }
        
        return render(request, 'admin/complaint_detail.html', context)
        
    except UserComplaint.DoesNotExist:
        messages.error(request, '投诉记录不存在')
        return redirect('admin_complaint_management')


def admin_blacklist_management(request):
    """管理员黑名单管理"""
    # 检查管理员权限：Django认证或自定义会话
    if not (request.user.is_authenticated and request.user.is_staff) and not request.session.get('is_admin'):
        return redirect('/login/admin/')
    
    # 如果通过Django认证但自定义会话未设置，则设置自定义会话
    if request.user.is_authenticated and request.user.is_staff and not request.session.get('is_admin'):
        request.session['is_admin'] = True
        request.session['admin_name'] = {"name": request.user.username}
    
    # 获取所有黑名单记录
    blacklist_records = Blacklist.objects.all().order_by('-start_time')
    # 获取所有用户列表，用于下拉选择
    users = Students.objects.all().order_by('name')
    # 获取待处理的撤销申请
    removal_requests = BlacklistRemovalRequest.objects.filter(status='pending').order_by('-created_at')
    
    if request.method == 'POST':
        # 处理黑名单操作
        student_id = request.POST.get('student_id')
        reason = request.POST.get('reason')
        action = request.POST.get('action')  # add 或 remove
        
        # 处理撤销申请操作
        request_id = request.POST.get('request_id')
        removal_action = request.POST.get('removal_action')  # approve 或 reject
        admin_comment = request.POST.get('admin_comment', '')
        
        try:
            # 处理撤销申请
            if request_id and removal_action:
                removal_request = BlacklistRemovalRequest.objects.get(id=request_id)
                
                if removal_action == 'approve':
                    # 批准撤销申请
                    removal_request.status = 'approved'
                    removal_request.reviewed_at = timezone.now()
                    removal_request.admin_comment = admin_comment
                    removal_request.save()
                    
                    # 解除黑名单
                    blacklist_record = removal_request.blacklist
                    blacklist_record.is_active = False
                    blacklist_record.save()
                    
                    messages.success(request, f'已批准 {removal_request.student.name} 的黑名单撤销申请')
                elif removal_action == 'reject':
                    # 拒绝撤销申请
                    removal_request.status = 'rejected'
                    removal_request.reviewed_at = timezone.now()
                    removal_request.admin_comment = admin_comment
                    removal_request.save()
                    
                    messages.success(request, f'已拒绝 {removal_request.student.name} 的黑名单撤销申请')
            
            # 处理黑名单操作
            elif student_id and action:
                student = Students.objects.get(id=student_id)
                
                if action == 'add':
                    # 添加到黑名单
                    Blacklist.objects.create(
                        student=student,
                        reason=reason
                    )
                    messages.success(request, f'用户 {student.name} 已添加到黑名单')
                elif action == 'remove':
                    # 从黑名单移除
                    blacklist_record = Blacklist.objects.get(student=student, is_active=True)
                    blacklist_record.is_active = False
                    blacklist_record.save()
                    messages.success(request, f'用户 {student.name} 已从黑名单移除')
            
        except Students.DoesNotExist:
            messages.error(request, '用户不存在')
        except Blacklist.DoesNotExist:
            messages.error(request, '黑名单记录不存在')
        except BlacklistRemovalRequest.DoesNotExist:
            messages.error(request, '撤销申请记录不存在')
        
        return redirect('admin_blacklist_management')
    
    context = {
        'blacklist_records': blacklist_records,
        'users': users,
        'removal_requests': removal_requests
    }
    
    return render(request, 'admin/blacklist_management.html', context)


def admin_evaluation_management(request):
    """管理员全平台评价管理"""
    # 检查管理员权限：Django认证或自定义会话
    if not (request.user.is_authenticated and request.user.is_staff) and not request.session.get('is_admin'):
        return redirect('/login/admin/')
    
    # 如果通过Django认证但自定义会话未设置，则设置自定义会话
    if request.user.is_authenticated and request.user.is_staff and not request.session.get('is_admin'):
        request.session['is_admin'] = True
        request.session['admin_name'] = {"name": request.user.username}
    
    # 获取所有评价记录
    evaluations = UserEvaluation.objects.all().order_by('-time')
    
    if request.method == 'POST':
        # 处理评价操作
        evaluation_id = request.POST.get('evaluation_id')
        action = request.POST.get('action')  # delete 或 approve
        
        try:
            evaluation = UserEvaluation.objects.get(id=evaluation_id)
            
            if action == 'delete':
                # 删除违规评价
                evaluation.delete()
                messages.success(request, '评价删除成功')
            elif action == 'approve':
                # 审核通过评价
                evaluation.is_approved = True
                evaluation.save()
                messages.success(request, '评价审核通过')
            
        except UserEvaluation.DoesNotExist:
            messages.error(request, '评价记录不存在')
        
        return redirect('admin_evaluation_management')
    
    context = {
        'evaluations': evaluations
    }
    
    return render(request, 'admin/evaluation_management.html', context)


def admin_complaint_feedback(request):
    """管理员投诉反馈信息管理"""
    # 检查管理员权限：Django认证或自定义会话
    if not (request.user.is_authenticated and request.user.is_staff) and not request.session.get('is_admin'):
        return redirect('/login/admin/')
    
    # 如果通过Django认证但自定义会话未设置，则设置自定义会话
    if request.user.is_authenticated and request.user.is_staff and not request.session.get('is_admin'):
        request.session['is_admin'] = True
        request.session['admin_name'] = {"name": request.user.username}
    
    # 获取所有投诉反馈记录
    feedbacks = ComplaintFeedback.objects.all().order_by('-feedback_time')
    
    if request.method == 'POST':
        # 处理反馈操作
        feedback_id = request.POST.get('feedback_id')
        action = request.POST.get('action')  # view 或 respond
        response_content = request.POST.get('response_content', '')
        
        try:
            feedback = ComplaintFeedback.objects.get(id=feedback_id)
            
            if action == 'respond' and response_content:
                # 添加管理员回复
                feedback.admin_response = response_content
                feedback.response_time = timezone.now()
                feedback.save()
                messages.success(request, '回复提交成功')
            
        except ComplaintFeedback.DoesNotExist:
            messages.error(request, '反馈记录不存在')
        
        return redirect('admin_complaint_feedback')
    
    context = {
        'feedbacks': feedbacks
    }
    
    return render(request, 'admin/complaint_feedback.html', context)


def admin_blacklist_removal_requests(request):
    """管理员黑名单撤销申请管理"""
    # 检查管理员权限：Django认证或自定义会话
    if not (request.user.is_authenticated and request.user.is_staff) and not request.session.get('is_admin'):
        return redirect('/login/admin/')
    
    # 如果通过Django认证但自定义会话未设置，则设置自定义会话
    if request.user.is_authenticated and request.user.is_staff and not request.session.get('is_admin'):
        request.session['is_admin'] = True
        request.session['admin_name'] = {"name": request.user.username}
    
    # 获取所有待审核的撤销申请
    removal_requests = BlacklistRemovalRequest.objects.filter(status='pending').order_by('-created_at')
    
    if request.method == 'POST':
        # 处理撤销申请审核
        request_id = request.POST.get('request_id')
        action = request.POST.get('action')  # approve 或 reject
        admin_comment = request.POST.get('admin_comment', '')
        
        try:
            removal_request = BlacklistRemovalRequest.objects.get(id=request_id)
            
            if action == 'approve':
                # 批准撤销申请
                removal_request.status = 'approved'
                removal_request.reviewed_at = timezone.now()
                removal_request.admin_comment = admin_comment
                removal_request.save()
                
                # 解除黑名单
                blacklist_record = removal_request.blacklist
                blacklist_record.is_active = False
                blacklist_record.save()
                
                messages.success(request, f'已批准 {removal_request.student.name} 的黑名单撤销申请')
            elif action == 'reject':
                # 拒绝撤销申请
                removal_request.status = 'rejected'
                removal_request.reviewed_at = timezone.now()
                removal_request.admin_comment = admin_comment
                removal_request.save()
                
                messages.success(request, f'已拒绝 {removal_request.student.name} 的黑名单撤销申请')
            
        except BlacklistRemovalRequest.DoesNotExist:
            messages.error(request, '撤销申请记录不存在')
        
        return redirect('admin_blacklist_removal_requests')
    
    context = {
        'removal_requests': removal_requests
    }
    
    return render(request, 'admin/blacklist_removal_requests.html', context)


@csrf_exempt
def api_register(request):
    if request.method == 'POST':
        # 从 POST 数据中获取字段
        name = request.POST.get('name')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        photo = request.FILES.get('photo') # 从 FILES 中获取图片

        # 简单的验证
        if not all([name, password, phone, email, photo]):
            return JsonResponse({'success': False, 'message': '所有字段都是必填的'}, status=400)

        # 检查用户名是否已存在
        if Students.objects.filter(name=name).exists():
            return JsonResponse({'success': False, 'message': '用户名已存在'}, status=400)

        # 检查邮箱是否已存在
        if Students.objects.filter(email=email).exists():
             return JsonResponse({'success': False, 'message': '邮箱已被注册'}, status=400)

        try:
            # 哈希密码
            hashed_password = make_password(password)
            stu = Students.objects.create(
                name=name,
                password=hashed_password, # 存储哈希后的密码
                phone=phone,
                email=email,
                photo=photo,
                is_active=True # 默认激活
            )
            return JsonResponse({'success': True, 'message': '注册成功'})
        except Exception as e:
            print(f"Error creating student: {e}") # 记录错误日志
            return JsonResponse({'success': False, 'message': '注册过程中发生错误，请稍后重试'}, status=500)

    else:
        return JsonResponse({'success': False, 'message': '仅支持 POST 请求'}, status=405)


# ==================== 数据分析模块 ====================

def admin_data_analysis(request):
    """管理员数据分析页面"""
    # 检查管理员权限：Django认证或自定义会话
    if not (request.user.is_authenticated and request.user.is_staff) and not request.session.get('is_admin'):
        return redirect('/login/admin/')
    
    # 如果通过Django认证但自定义会话未设置，则设置自定义会话
    if request.user.is_authenticated and request.user.is_staff and not request.session.get('is_admin'):
        request.session['is_admin'] = True
        request.session['admin_name'] = {"name": request.user.username}
    
    return render(request, 'admin/data_analysis.html')


@csrf_exempt
def admin_data_analysis_api(request):
    """数据分析API接口"""
    # 检查管理员权限
    if not (request.user.is_authenticated and request.user.is_staff) and not request.session.get('is_admin'):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        # 支持日期范围查询参数
        date_param = request.GET.get('date', 'today')  # today, week, month, 或具体日期 YYYY-MM-DD
        today = timezone.now().date()
        
        # 根据参数确定分析日期
        if date_param == 'today':
            analysis_date = today
            date_label = "今日"
        elif date_param == 'week':
            analysis_date = today - timedelta(days=7)
            date_label = "近7天"
        elif date_param == 'month':
            analysis_date = today - timedelta(days=30)
            date_label = "近30天"
        else:
            # 尝试解析具体日期
            try:
                analysis_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                date_label = analysis_date.strftime('%Y-%m-%d')
            except ValueError:
                analysis_date = today
                date_label = "今日"
        today_bookings = Bookings.objects.filter(
            time__date=today,
            is_active__in=[1, 2]  # 已预约或已签到
        ).count()
        
        # 获取昨日预约量
        yesterday = today - timedelta(days=1)
        yesterday_bookings = Bookings.objects.filter(
            time__date=yesterday,
            is_active__in=[1, 2]
        ).count()
        
        # 计算变化率
        booking_change = 0
        if yesterday_bookings > 0:
            booking_change = round(((today_bookings - yesterday_bookings) / yesterday_bookings) * 100, 1)
        
        # 获取当前使用率（当前时间段的预约情况）
        current_hour = timezone.now().hour
        current_usage = 0
        peak_time_info = "暂无数据"
        
        # 获取自习室总数和当前使用数
        total_rooms = Rooms.objects.filter(is_active=True)
        if total_rooms.exists():
            # 使用实际的座位数量计算
            total_seats = sum(room.number for room in total_rooms)
            current_bookings = Bookings.objects.filter(
                time__hour=current_hour,
                is_active__in=[1, 2]
            ).count()
            current_usage = round((current_bookings / total_seats) * 100, 1) if total_seats > 0 else 0
            
            # 智能检测高峰时段（基于最近7天的数据）
            peak_usage = 0
            peak_hour_range = ""
            
            # 分析最近7天各时段的使用率
            for start_hour in range(8, 22, 2):  # 8:00-10:00, 10:00-12:00, ..., 20:00-22:00
                end_hour = start_hour + 2
                
                # 计算该时段在最近7天的平均使用率
                period_total_bookings = 0
                for day_offset in range(7):
                    check_date = today - timedelta(days=day_offset)
                    period_bookings = Bookings.objects.filter(
                        time__date=check_date,
                        time__hour__gte=start_hour,
                        time__hour__lt=end_hour,
                        is_active__in=[1, 2]
                    ).count()
                    period_total_bookings += period_bookings
                
                avg_period_usage = (period_total_bookings / 7) / total_seats * 100 if total_seats > 0 else 0
                
                if avg_period_usage > peak_usage:
                    peak_usage = avg_period_usage
                    peak_hour_range = f"{start_hour:02d}:00-{end_hour:02d}:00"
            
            if peak_hour_range:
                peak_time_info = f"{peak_hour_range} (平均使用率: {peak_usage:.1f}%)"
        
        # 获取用户满意度（基于评价的平均分）
        satisfaction_rate = 0
        evaluation_count = UserEvaluation.objects.count()
        if evaluation_count > 0:
            avg_rating = UserEvaluation.objects.aggregate(avg_rating=Avg('rating'))['avg_rating']
            satisfaction_rate = round((avg_rating / 5) * 100, 1) if avg_rating else 0
        
        # 获取违规次数
        violation_count = Blacklist.objects.filter(is_active=True).count()
        
        # 获取上周违规次数
        last_week = today - timedelta(weeks=1)
        last_week_violations = Blacklist.objects.filter(
            start_time__date__gte=last_week,
            start_time__date__lt=today
        ).count()
        
        # 计算违规变化率
        violation_change = 0
        if last_week_violations > 0:
            violation_change = round(((violation_count - last_week_violations) / last_week_violations) * 100, 1)
        
        # 每日各时段自习室使用率数据（基于真实数据）
        time_periods = [
            (8, 10, '08:00-10:00'),
            (10, 12, '10:00-12:00'),
            (12, 14, '12:00-14:00'),
            (14, 16, '14:00-16:00'),
            (16, 18, '16:00-18:00'),
            (18, 20, '18:00-20:00'),
            (20, 22, '20:00-22:00')
        ]
        
        usage_by_time_labels = []
        usage_by_time_values = []
        
        # 获取总座位数
        total_seats_all = sum(room.number for room in Rooms.objects.filter(is_active=True))
        
        for start_hour, end_hour, label in time_periods:
            usage_by_time_labels.append(label)
            
            # 获取该时间段今日的预约数
            period_bookings = Bookings.objects.filter(
                time__date=today,
                time__hour__gte=start_hour,
                time__hour__lt=end_hour,
                is_active__in=[1, 2]  # 已预约或已签到
            ).count()
            
            # 计算使用率
            usage_rate = round((period_bookings / total_seats_all) * 100, 1) if total_seats_all > 0 else 0
            usage_by_time_values.append(usage_rate)
        
        usage_by_time = {
            'labels': usage_by_time_labels,
            'values': usage_by_time_values
        }
        
        # 每周预约量/违规次数变化趋势（基于真实数据）
        weekly_trend_labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekly_bookings = []
        weekly_violations = []
        
        # 获取本周和上周的日期范围
        today_weekday = today.weekday()  # 0=周一, 6=周日
        week_start = today - timedelta(days=today_weekday)
        week_end = week_start + timedelta(days=6)
        
        # 获取上周的日期范围
        last_week_start = week_start - timedelta(weeks=1)
        last_week_end = week_start - timedelta(days=1)
        
        for i, day_name in enumerate(weekly_trend_labels):
            current_day = week_start + timedelta(days=i)
            
            # 获取该日的预约数
            day_bookings = Bookings.objects.filter(
                time__date=current_day,
                is_active__in=[1, 2]
            ).count()
            weekly_bookings.append(day_bookings)
            
            # 获取该日的违规数（黑名单新增数）
            day_violations = Blacklist.objects.filter(
                start_time__date=current_day
            ).count()
            weekly_violations.append(day_violations)
        
        weekly_trend = {
            'labels': weekly_trend_labels,
            'bookings': weekly_bookings,
            'violations': weekly_violations
        }
        
        # 自习室使用率统计
        room_usage = []
        rooms = Rooms.objects.filter(is_active=True)
        for room in rooms:
            # 获取该自习室今日预约数
            room_bookings = Bookings.objects.filter(
                room=room,
                time__date=today,
                is_active__in=[1, 2]
            ).count()
            
            # 使用实际的座位数量
            total_seats = room.number
            usage_rate = round((room_bookings / total_seats) * 100, 1) if total_seats > 0 else 0
            
            # 获取该自习室平均评分
            avg_rating = UserEvaluation.objects.filter(room=room).aggregate(avg_rating=Avg('rating'))['avg_rating']
            avg_rating = round(avg_rating, 1) if avg_rating else 0
            
            room_usage.append({
                'name': room.name,
                'totalSeats': total_seats,
                'currentUsage': room_bookings,
                'usageRate': usage_rate,
                'todayBookings': room_bookings,
                'averageRating': avg_rating
            })
        
        # 系统决策建议（基于真实数据的智能分析）
        suggestions = []
        
        # 1. 检查高使用率自习室
        high_usage_rooms = [room for room in room_usage if room['usageRate'] >= 80]
        medium_usage_rooms = [room for room in room_usage if 60 <= room['usageRate'] < 80]
        
        if high_usage_rooms:
            room_names = ", ".join([room['name'] for room in high_usage_rooms])
            suggestions.append({
                'text': f"{room_names} 使用率超过80%，建议：1) 增加临时座位 2) 实施预约时段分流 3) 引导用户选择其他自习室",
                'priority': '高'
            })
        
        if medium_usage_rooms:
            room_names = ", ".join([room['name'] for room in medium_usage_rooms])
            suggestions.append({
                'text': f"{room_names} 使用率较高(60-80%)，建议：1) 关注高峰时段管理 2) 准备应急预案 3) 优化座位分配",
                'priority': '中'
            })
        
        # 2. 基于时段使用率的建议
        if usage_by_time['values']:
            max_usage_idx = usage_by_time['values'].index(max(usage_by_time['values']))
            peak_period = usage_by_time['labels'][max_usage_idx]
            peak_usage = usage_by_time['values'][max_usage_idx]
            
            if peak_usage > 85:
                suggestions.append({
                    'text': f"{peak_period}为高峰时段(使用率{peak_usage}%)，建议：1) 增加该时段管理员巡查 2) 实施预约限制 3) 错峰使用引导",
                    'priority': '高'
                })
        
        # 3. 违规情况分析
        if violation_count > 0:
            # 分析违规类型和趋势
            recent_violations = Blacklist.objects.filter(
                start_time__date__gte=today - timedelta(days=7)
            )
            
            if recent_violations.count() > 3:
                suggestions.append({
                    'text': f"本周新增违规{recent_violations.count()}次，趋势上升，建议：1) 加强用户行为规范培训 2) 完善违规处理流程 3) 建立预警机制",
                    'priority': '高'
                })
            elif recent_violations.count() > 0:
                suggestions.append({
                    'text': f"本周有{recent_violations.count()}次违规记录，建议关注用户行为规范，及时处理违规情况",
                    'priority': '中'
                })
        
        # 4. 用户满意度分析
        if evaluation_count > 0:
            # 分析低分评价
            low_ratings = UserEvaluation.objects.filter(rating__in=[1, 2]).count()
            if low_ratings > evaluation_count * 0.2:  # 如果低分评价超过20%
                suggestions.append({
                    'text': f"低分评价占比{round(low_ratings/evaluation_count*100, 1)}%，建议：1) 分析低分原因 2) 改善服务质量 3) 主动联系用户解决问题",
                    'priority': '高'
                })
            elif evaluation_count < 10:
                suggestions.append({
                    'text': "用户评价数量较少，建议：1) 设置评价激励机制 2) 简化评价流程 3) 定期推送评价邀请",
                    'priority': '中'
                })
        else:
            suggestions.append({
                'text': "暂无用户评价数据，建议：1) 建立评价体系 2) 鼓励用户反馈 3) 收集使用体验信息",
                'priority': '中'
            })
        
        # 5. 预约趋势分析
        if weekly_bookings:
            avg_daily_bookings = sum(weekly_bookings) / len(weekly_bookings)
            if today_bookings < avg_daily_bookings * 0.7:
                suggestions.append({
                    'text': f"今日预约量({today_bookings})低于本周平均值({round(avg_daily_bookings)})，建议：1) 检查系统状态 2) 分析下降原因 3) 加强宣传推广",
                    'priority': '中'
                })
        
        # 6. 资源利用率建议
        low_usage_rooms = [room for room in room_usage if room['usageRate'] < 30]
        if low_usage_rooms:
            room_names = ", ".join([room['name'] for room in low_usage_rooms])
            suggestions.append({
                'text': f"{room_names} 使用率较低(<30%)，建议：1) 分析原因 2) 优化环境配置 3) 调整开放时间 4) 加强宣传推广",
                'priority': '低'
            })
        
        # 7. 如果没有特殊建议，添加默认建议
        if not suggestions:
            suggestions.append({
                'text': "系统运行良好，各项指标正常。建议：1) 继续保持当前管理策略 2) 定期监控关键指标 3) 持续优化用户体验",
                'priority': '低'
            })
        
        # 构建返回数据
        data = {
            'analysisInfo': {
                'date': date_label,
                'analysisDate': analysis_date.strftime('%Y-%m-%d'),
                'totalRooms': len(room_usage),
                'totalSeats': sum(room['totalSeats'] for room in room_usage)
            },
            'statistics': {
                'todayBookings': today_bookings,
                'bookingChange': booking_change,
                'currentUsage': current_usage,
                'peakTime': peak_time_info,
                'satisfactionRate': satisfaction_rate,
                'evaluationCount': evaluation_count,
                'violationCount': violation_count,
                'violationChange': violation_change
            },
            'usageByTime': usage_by_time,
            'weeklyTrend': weekly_trend,
            'roomUsage': room_usage,
            'suggestions': suggestions
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        print(f"Error in data analysis API: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
def api_password_reset_request(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '无效的请求格式'}, status=400)

        if not email:
            return JsonResponse({'success': False, 'message': '邮箱不能为空'}, status=400)

        user = Students.objects.filter(email=email, is_active=True).first()

        if user:
            # 生成 6 位数字验证码
            code = ''.join(random.choices(string.digits, k=6))
            # 设置验证码过期时间（例如 10 分钟后）
            expiry_time = datetime.now(dt_timezone.utc) + timedelta(minutes=10)

            # 将验证码和过期时间存储在 session 中 (与邮箱关联)
            request.session['reset_code'] = code
            request.session['reset_code_email'] = email
            request.session['reset_code_expiry'] = expiry_time.isoformat() # Store as string
            print(f"Stored reset code for {email}: {code}, expires: {expiry_time.isoformat()}")


            # 邮件内容
            subject = '您的密码重置验证码 - 自习室预约系统'
            message = f"""
您好 {user.name},

您正在请求重置密码。您的验证码是：

{code}

此验证码将在 10 分钟后过期。如果您没有请求重置密码，请忽略此邮件。

感谢！
自习室预约系统团队
            """
            from_email = settings.DEFAULT_FROM_EMAIL

            try:
                # 发送邮件 (当前配置为输出到控制台)
                send_mail(subject, message, from_email, [email])
                print(f"发送密码重置验证码邮件给 {email}，验证码: {code}")
                return JsonResponse({'success': True, 'message': '验证码已发送至您的邮箱，请注意查收。'})
            except Exception as e:
                print(f"Error sending reset code email: {e}")
                # 清除 session 中的无效数据
                if 'reset_code' in request.session: del request.session['reset_code']
                if 'reset_code_email' in request.session: del request.session['reset_code_email']
                if 'reset_code_expiry' in request.session: del request.session['reset_code_expiry']
                return JsonResponse({'success': False, 'message': '发送验证码邮件时出错，请稍后重试'}, status=500)
        else:
            # 即使邮箱不存在，也返回看似成功的消息，防止信息泄露
            print(f"密码重置请求，邮箱不存在或用户未激活: {email}")
            return JsonResponse({'success': True, 'message': '如果您的邮箱已注册，验证码已发送。'}) # 调整措辞

    else:
        return JsonResponse({'success': False, 'message': '仅支持 POST 请求'}, status=405)


# ==================== 数据分析模块 ====================

def admin_data_analysis(request):
    """管理员数据分析页面"""
    # 检查管理员权限：Django认证或自定义会话
    if not (request.user.is_authenticated and request.user.is_staff) and not request.session.get('is_admin'):
        return redirect('/login/admin/')
    
    # 如果通过Django认证但自定义会话未设置，则设置自定义会话
    if request.user.is_authenticated and request.user.is_staff and not request.session.get('is_admin'):
        request.session['is_admin'] = True
        request.session['admin_name'] = {"name": request.user.username}
    
    return render(request, 'admin/data_analysis.html')


@csrf_exempt
def admin_data_analysis_api(request):
    """数据分析API接口"""
    # 检查管理员权限
    if not (request.user.is_authenticated and request.user.is_staff) and not request.session.get('is_admin'):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        # 支持日期范围查询参数
        date_param = request.GET.get('date', 'today')  # today, week, month, 或具体日期 YYYY-MM-DD
        today = timezone.now().date()
        
        # 根据参数确定分析日期
        if date_param == 'today':
            analysis_date = today
            date_label = "今日"
        elif date_param == 'week':
            analysis_date = today - timedelta(days=7)
            date_label = "近7天"
        elif date_param == 'month':
            analysis_date = today - timedelta(days=30)
            date_label = "近30天"
        else:
            # 尝试解析具体日期
            try:
                analysis_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                date_label = analysis_date.strftime('%Y-%m-%d')
            except ValueError:
                analysis_date = today
                date_label = "今日"
        today_bookings = Bookings.objects.filter(
            time__date=today,
            is_active__in=[1, 2]  # 已预约或已签到
        ).count()
        
        # 获取昨日预约量
        yesterday = today - timedelta(days=1)
        yesterday_bookings = Bookings.objects.filter(
            time__date=yesterday,
            is_active__in=[1, 2]
        ).count()
        
        # 计算变化率
        booking_change = 0
        if yesterday_bookings > 0:
            booking_change = round(((today_bookings - yesterday_bookings) / yesterday_bookings) * 100, 1)
        
        # 获取当前使用率（当前时间段的预约情况）
        current_hour = timezone.now().hour
        current_usage = 0
        peak_time_info = "暂无数据"
        
        # 获取自习室总数和当前使用数
        total_rooms = Rooms.objects.filter(is_active=True)
        if total_rooms.exists():
            # 使用实际的座位数量计算
            total_seats = sum(room.number for room in total_rooms)
            current_bookings = Bookings.objects.filter(
                time__hour=current_hour,
                is_active__in=[1, 2]
            ).count()
            current_usage = round((current_bookings / total_seats) * 100, 1) if total_seats > 0 else 0
            
            # 智能检测高峰时段（基于最近7天的数据）
            peak_usage = 0
            peak_hour_range = ""
            
            # 分析最近7天各时段的使用率
            for start_hour in range(8, 22, 2):  # 8:00-10:00, 10:00-12:00, ..., 20:00-22:00
                end_hour = start_hour + 2
                
                # 计算该时段在最近7天的平均使用率
                period_total_bookings = 0
                for day_offset in range(7):
                    check_date = today - timedelta(days=day_offset)
                    period_bookings = Bookings.objects.filter(
                        time__date=check_date,
                        time__hour__gte=start_hour,
                        time__hour__lt=end_hour,
                        is_active__in=[1, 2]
                    ).count()
                    period_total_bookings += period_bookings
                
                avg_period_usage = (period_total_bookings / 7) / total_seats * 100 if total_seats > 0 else 0
                
                if avg_period_usage > peak_usage:
                    peak_usage = avg_period_usage
                    peak_hour_range = f"{start_hour:02d}:00-{end_hour:02d}:00"
            
            if peak_hour_range:
                peak_time_info = f"{peak_hour_range} (平均使用率: {peak_usage:.1f}%)"
        
        # 获取用户满意度（基于评价的平均分）
        satisfaction_rate = 0
        evaluation_count = UserEvaluation.objects.count()
        if evaluation_count > 0:
            avg_rating = UserEvaluation.objects.aggregate(avg_rating=Avg('rating'))['avg_rating']
            satisfaction_rate = round((avg_rating / 5) * 100, 1) if avg_rating else 0
        
        # 获取违规次数
        violation_count = Blacklist.objects.filter(is_active=True).count()
        
        # 获取上周违规次数
        last_week = today - timedelta(weeks=1)
        last_week_violations = Blacklist.objects.filter(
            start_time__date__gte=last_week,
            start_time__date__lt=today
        ).count()
        
        # 计算违规变化率
        violation_change = 0
        if last_week_violations > 0:
            violation_change = round(((violation_count - last_week_violations) / last_week_violations) * 100, 1)
        
        # 每日各时段自习室使用率数据（基于真实数据）
        time_periods = [
            (8, 10, '08:00-10:00'),
            (10, 12, '10:00-12:00'),
            (12, 14, '12:00-14:00'),
            (14, 16, '14:00-16:00'),
            (16, 18, '16:00-18:00'),
            (18, 20, '18:00-20:00'),
            (20, 22, '20:00-22:00')
        ]
        
        usage_by_time_labels = []
        usage_by_time_values = []
        
        # 获取总座位数
        total_seats_all = sum(room.number for room in Rooms.objects.filter(is_active=True))
        
        for start_hour, end_hour, label in time_periods:
            usage_by_time_labels.append(label)
            
            # 获取该时间段今日的预约数
            period_bookings = Bookings.objects.filter(
                time__date=today,
                time__hour__gte=start_hour,
                time__hour__lt=end_hour,
                is_active__in=[1, 2]  # 已预约或已签到
            ).count()
            
            # 计算使用率
            usage_rate = round((period_bookings / total_seats_all) * 100, 1) if total_seats_all > 0 else 0
            usage_by_time_values.append(usage_rate)
        
        usage_by_time = {
            'labels': usage_by_time_labels,
            'values': usage_by_time_values
        }
        
        # 每周预约量/违规次数变化趋势（基于真实数据）
        weekly_trend_labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekly_bookings = []
        weekly_violations = []
        
        # 获取本周和上周的日期范围
        today_weekday = today.weekday()  # 0=周一, 6=周日
        week_start = today - timedelta(days=today_weekday)
        week_end = week_start + timedelta(days=6)
        
        # 获取上周的日期范围
        last_week_start = week_start - timedelta(weeks=1)
        last_week_end = week_start - timedelta(days=1)
        
        for i, day_name in enumerate(weekly_trend_labels):
            current_day = week_start + timedelta(days=i)
            
            # 获取该日的预约数
            day_bookings = Bookings.objects.filter(
                time__date=current_day,
                is_active__in=[1, 2]
            ).count()
            weekly_bookings.append(day_bookings)
            
            # 获取该日的违规数（黑名单新增数）
            day_violations = Blacklist.objects.filter(
                start_time__date=current_day
            ).count()
            weekly_violations.append(day_violations)
        
        weekly_trend = {
            'labels': weekly_trend_labels,
            'bookings': weekly_bookings,
            'violations': weekly_violations
        }
        
        # 自习室使用率统计
        room_usage = []
        rooms = Rooms.objects.filter(is_active=True)
        for room in rooms:
            # 获取该自习室今日预约数
            room_bookings = Bookings.objects.filter(
                room=room,
                time__date=today,
                is_active__in=[1, 2]
            ).count()
            
            # 使用实际的座位数量
            total_seats = room.number
            usage_rate = round((room_bookings / total_seats) * 100, 1) if total_seats > 0 else 0
            
            # 获取该自习室平均评分
            avg_rating = UserEvaluation.objects.filter(room=room).aggregate(avg_rating=Avg('rating'))['avg_rating']
            avg_rating = round(avg_rating, 1) if avg_rating else 0
            
            room_usage.append({
                'name': room.name,
                'totalSeats': total_seats,
                'currentUsage': room_bookings,
                'usageRate': usage_rate,
                'todayBookings': room_bookings,
                'averageRating': avg_rating
            })
        
        # 系统决策建议（基于真实数据的智能分析）
        suggestions = []
        
        # 1. 检查高使用率自习室
        high_usage_rooms = [room for room in room_usage if room['usageRate'] >= 80]
        medium_usage_rooms = [room for room in room_usage if 60 <= room['usageRate'] < 80]
        
        if high_usage_rooms:
            room_names = ", ".join([room['name'] for room in high_usage_rooms])
            suggestions.append({
                'text': f"{room_names} 使用率超过80%，建议：1) 增加临时座位 2) 实施预约时段分流 3) 引导用户选择其他自习室",
                'priority': '高'
            })
        
        if medium_usage_rooms:
            room_names = ", ".join([room['name'] for room in medium_usage_rooms])
            suggestions.append({
                'text': f"{room_names} 使用率较高(60-80%)，建议：1) 关注高峰时段管理 2) 准备应急预案 3) 优化座位分配",
                'priority': '中'
            })
        
        # 2. 基于时段使用率的建议
        if usage_by_time['values']:
            max_usage_idx = usage_by_time['values'].index(max(usage_by_time['values']))
            peak_period = usage_by_time['labels'][max_usage_idx]
            peak_usage = usage_by_time['values'][max_usage_idx]
            
            if peak_usage > 85:
                suggestions.append({
                    'text': f"{peak_period}为高峰时段(使用率{peak_usage}%)，建议：1) 增加该时段管理员巡查 2) 实施预约限制 3) 错峰使用引导",
                    'priority': '高'
                })
        
        # 3. 违规情况分析
        if violation_count > 0:
            # 分析违规类型和趋势
            recent_violations = Blacklist.objects.filter(
                start_time__date__gte=today - timedelta(days=7)
            )
            
            if recent_violations.count() > 3:
                suggestions.append({
                    'text': f"本周新增违规{recent_violations.count()}次，趋势上升，建议：1) 加强用户行为规范培训 2) 完善违规处理流程 3) 建立预警机制",
                    'priority': '高'
                })
            elif recent_violations.count() > 0:
                suggestions.append({
                    'text': f"本周有{recent_violations.count()}次违规记录，建议关注用户行为规范，及时处理违规情况",
                    'priority': '中'
                })
        
        # 4. 用户满意度分析
        if evaluation_count > 0:
            # 分析低分评价
            low_ratings = UserEvaluation.objects.filter(rating__in=[1, 2]).count()
            if low_ratings > evaluation_count * 0.2:  # 如果低分评价超过20%
                suggestions.append({
                    'text': f"低分评价占比{round(low_ratings/evaluation_count*100, 1)}%，建议：1) 分析低分原因 2) 改善服务质量 3) 主动联系用户解决问题",
                    'priority': '高'
                })
            elif evaluation_count < 10:
                suggestions.append({
                    'text': "用户评价数量较少，建议：1) 设置评价激励机制 2) 简化评价流程 3) 定期推送评价邀请",
                    'priority': '中'
                })
        else:
            suggestions.append({
                'text': "暂无用户评价数据，建议：1) 建立评价体系 2) 鼓励用户反馈 3) 收集使用体验信息",
                'priority': '中'
            })
        
        # 5. 预约趋势分析
        if weekly_bookings:
            avg_daily_bookings = sum(weekly_bookings) / len(weekly_bookings)
            if today_bookings < avg_daily_bookings * 0.7:
                suggestions.append({
                    'text': f"今日预约量({today_bookings})低于本周平均值({round(avg_daily_bookings)})，建议：1) 检查系统状态 2) 分析下降原因 3) 加强宣传推广",
                    'priority': '中'
                })
        
        # 6. 资源利用率建议
        low_usage_rooms = [room for room in room_usage if room['usageRate'] < 30]
        if low_usage_rooms:
            room_names = ", ".join([room['name'] for room in low_usage_rooms])
            suggestions.append({
                'text': f"{room_names} 使用率较低(<30%)，建议：1) 分析原因 2) 优化环境配置 3) 调整开放时间 4) 加强宣传推广",
                'priority': '低'
            })
        
        # 7. 如果没有特殊建议，添加默认建议
        if not suggestions:
            suggestions.append({
                'text': "系统运行良好，各项指标正常。建议：1) 继续保持当前管理策略 2) 定期监控关键指标 3) 持续优化用户体验",
                'priority': '低'
            })
        
        # 构建返回数据
        data = {
            'analysisInfo': {
                'date': date_label,
                'analysisDate': analysis_date.strftime('%Y-%m-%d'),
                'totalRooms': len(room_usage),
                'totalSeats': sum(room['totalSeats'] for room in room_usage)
            },
            'statistics': {
                'todayBookings': today_bookings,
                'bookingChange': booking_change,
                'currentUsage': current_usage,
                'peakTime': peak_time_info,
                'satisfactionRate': satisfaction_rate,
                'evaluationCount': evaluation_count,
                'violationCount': violation_count,
                'violationChange': violation_change
            },
            'usageByTime': usage_by_time,
            'weeklyTrend': weekly_trend,
            'roomUsage': room_usage,
            'suggestions': suggestions
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        print(f"Error in data analysis API: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)


@csrf_exempt
def api_password_reset_with_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email') # 需要前端也把 email 传过来
            code = data.get('code')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')

            if not all([email, code, new_password, confirm_password]):
                return JsonResponse({'success': False, 'message': '缺少必要参数'}, status=400)

            if new_password != confirm_password:
                return JsonResponse({'success': False, 'message': '两次输入的密码不一致'}, status=400)

            # --- 验证 Session 中的验证码 ---
            stored_code = request.session.get('reset_code')
            stored_email = request.session.get('reset_code_email')
            stored_expiry_str = request.session.get('reset_code_expiry')

            print(f"Verifying code: Input Email={email}, Stored Email={stored_email}, Input Code={code}, Stored Code={stored_code}, Expiry={stored_expiry_str}")

            if not stored_code or not stored_email or not stored_expiry_str:
                return JsonResponse({'success': False, 'message': '验证码会话不存在，请重新请求'}, status=400)

            if email != stored_email:
                 return JsonResponse({'success': False, 'message': '邮箱与请求验证码时的邮箱不符'}, status=400)

            if code != stored_code:
                 return JsonResponse({'success': False, 'message': '验证码错误'}, status=400)

            # 检查验证码是否过期
            try:
                expiry_time = datetime.fromisoformat(stored_expiry_str)
                if datetime.now(dt_timezone.utc) > expiry_time:
                    # 清除过期的 session 数据
                    del request.session['reset_code']
                    del request.session['reset_code_email']
                    del request.session['reset_code_expiry']
                    return JsonResponse({'success': False, 'message': '验证码已过期，请重新请求'}, status=400)
            except ValueError:
                 # 清除格式错误的 session 数据
                 if 'reset_code_expiry' in request.session: del request.session['reset_code_expiry']
                 return JsonResponse({'success': False, 'message': '验证码有效期格式错误'}, status=500)


            # --- 验证通过，查找用户并重置密码 ---
            try:
                user = Students.objects.get(email=email, is_active=True) # 再次确认用户
            except Students.DoesNotExist:
                 return JsonResponse({'success': False, 'message': '用户不存在或未激活'}, status=404)

            try:
                user.password = make_password(new_password)
                user.save(update_fields=['password'])
                print(f"Password reset successful for user {user.name} via code.")

                # 密码重置成功后，清除 session 中的验证码信息
                del request.session['reset_code']
                del request.session['reset_code_email']
                del request.session['reset_code_expiry']

                return JsonResponse({'success': True, 'message': '密码重置成功！请使用新密码登录。'})
            except Exception as e:
                print(f"Error saving new password after code verification: {e}")
                return JsonResponse({'success': False, 'message': '保存新密码时出错'}, status=500)

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '无效的请求格式'}, status=400)
        except Exception as e:
            print(f"Unexpected error in password reset with code: {e}")
            return JsonResponse({'success': False, 'message': '处理密码重置时发生错误'}, status=500)

    else:
        return JsonResponse({'success': False, 'message': '仅支持 POST 请求'}, status=405)


# ==================== 数据分析模块 ====================

def admin_data_analysis(request):
    """管理员数据分析页面"""
    # 检查管理员权限：Django认证或自定义会话
    if not (request.user.is_authenticated and request.user.is_staff) and not request.session.get('is_admin'):
        return redirect('/login/admin/')
    
    # 如果通过Django认证但自定义会话未设置，则设置自定义会话
    if request.user.is_authenticated and request.user.is_staff and not request.session.get('is_admin'):
        request.session['is_admin'] = True
        request.session['admin_name'] = {"name": request.user.username}
    
    return render(request, 'admin/data_analysis.html')


@csrf_exempt
def admin_data_analysis_api(request):
    """数据分析API接口"""
    # 检查管理员权限
    if not (request.user.is_authenticated and request.user.is_staff) and not request.session.get('is_admin'):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        # 支持日期范围查询参数
        date_param = request.GET.get('date', 'today')  # today, week, month, 或具体日期 YYYY-MM-DD
        today = timezone.now().date()
        
        # 根据参数确定分析日期
        if date_param == 'today':
            analysis_date = today
            date_label = "今日"
        elif date_param == 'week':
            analysis_date = today - timedelta(days=7)
            date_label = "近7天"
        elif date_param == 'month':
            analysis_date = today - timedelta(days=30)
            date_label = "近30天"
        else:
            # 尝试解析具体日期
            try:
                analysis_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                date_label = analysis_date.strftime('%Y-%m-%d')
            except ValueError:
                analysis_date = today
                date_label = "今日"
        today_bookings = Bookings.objects.filter(
            time__date=today,
            is_active__in=[1, 2]  # 已预约或已签到
        ).count()
        
        # 获取昨日预约量
        yesterday = today - timedelta(days=1)
        yesterday_bookings = Bookings.objects.filter(
            time__date=yesterday,
            is_active__in=[1, 2]
        ).count()
        
        # 计算变化率
        booking_change = 0
        if yesterday_bookings > 0:
            booking_change = round(((today_bookings - yesterday_bookings) / yesterday_bookings) * 100, 1)
        
        # 获取当前使用率（当前时间段的预约情况）
        current_hour = timezone.now().hour
        current_usage = 0
        peak_time_info = "暂无数据"
        
        # 获取自习室总数和当前使用数
        total_rooms = Rooms.objects.filter(is_active=True)
        if total_rooms.exists():
            # 使用实际的座位数量计算
            total_seats = sum(room.number for room in total_rooms)
            current_bookings = Bookings.objects.filter(
                time__hour=current_hour,
                is_active__in=[1, 2]
            ).count()
            current_usage = round((current_bookings / total_seats) * 100, 1) if total_seats > 0 else 0
            
            # 智能检测高峰时段（基于最近7天的数据）
            peak_usage = 0
            peak_hour_range = ""
            
            # 分析最近7天各时段的使用率
            for start_hour in range(8, 22, 2):  # 8:00-10:00, 10:00-12:00, ..., 20:00-22:00
                end_hour = start_hour + 2
                
                # 计算该时段在最近7天的平均使用率
                period_total_bookings = 0
                for day_offset in range(7):
                    check_date = today - timedelta(days=day_offset)
                    period_bookings = Bookings.objects.filter(
                        time__date=check_date,
                        time__hour__gte=start_hour,
                        time__hour__lt=end_hour,
                        is_active__in=[1, 2]
                    ).count()
                    period_total_bookings += period_bookings
                
                avg_period_usage = (period_total_bookings / 7) / total_seats * 100 if total_seats > 0 else 0
                
                if avg_period_usage > peak_usage:
                    peak_usage = avg_period_usage
                    peak_hour_range = f"{start_hour:02d}:00-{end_hour:02d}:00"
            
            if peak_hour_range:
                peak_time_info = f"{peak_hour_range} (平均使用率: {peak_usage:.1f}%)"
        
        # 获取用户满意度（基于评价的平均分）
        satisfaction_rate = 0
        evaluation_count = UserEvaluation.objects.count()
        if evaluation_count > 0:
            avg_rating = UserEvaluation.objects.aggregate(avg_rating=Avg('rating'))['avg_rating']
            satisfaction_rate = round((avg_rating / 5) * 100, 1) if avg_rating else 0
        
        # 获取违规次数
        violation_count = Blacklist.objects.filter(is_active=True).count()
        
        # 获取上周违规次数
        last_week = today - timedelta(weeks=1)
        last_week_violations = Blacklist.objects.filter(
            start_time__date__gte=last_week,
            start_time__date__lt=today
        ).count()
        
        # 计算违规变化率
        violation_change = 0
        if last_week_violations > 0:
            violation_change = round(((violation_count - last_week_violations) / last_week_violations) * 100, 1)
        
        # 每日各时段自习室使用率数据（基于真实数据）
        time_periods = [
            (8, 10, '08:00-10:00'),
            (10, 12, '10:00-12:00'),
            (12, 14, '12:00-14:00'),
            (14, 16, '14:00-16:00'),
            (16, 18, '16:00-18:00'),
            (18, 20, '18:00-20:00'),
            (20, 22, '20:00-22:00')
        ]
        
        usage_by_time_labels = []
        usage_by_time_values = []
        
        # 获取总座位数
        total_seats_all = sum(room.number for room in Rooms.objects.filter(is_active=True))
        
        for start_hour, end_hour, label in time_periods:
            usage_by_time_labels.append(label)
            
            # 获取该时间段今日的预约数
            period_bookings = Bookings.objects.filter(
                time__date=today,
                time__hour__gte=start_hour,
                time__hour__lt=end_hour,
                is_active__in=[1, 2]  # 已预约或已签到
            ).count()
            
            # 计算使用率
            usage_rate = round((period_bookings / total_seats_all) * 100, 1) if total_seats_all > 0 else 0
            usage_by_time_values.append(usage_rate)
        
        usage_by_time = {
            'labels': usage_by_time_labels,
            'values': usage_by_time_values
        }
        
        # 每周预约量/违规次数变化趋势（基于真实数据）
        weekly_trend_labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekly_bookings = []
        weekly_violations = []
        
        # 获取本周和上周的日期范围
        today_weekday = today.weekday()  # 0=周一, 6=周日
        week_start = today - timedelta(days=today_weekday)
        week_end = week_start + timedelta(days=6)
        
        # 获取上周的日期范围
        last_week_start = week_start - timedelta(weeks=1)
        last_week_end = week_start - timedelta(days=1)
        
        for i, day_name in enumerate(weekly_trend_labels):
            current_day = week_start + timedelta(days=i)
            
            # 获取该日的预约数
            day_bookings = Bookings.objects.filter(
                time__date=current_day,
                is_active__in=[1, 2]
            ).count()
            weekly_bookings.append(day_bookings)
            
            # 获取该日的违规数（黑名单新增数）
            day_violations = Blacklist.objects.filter(
                start_time__date=current_day
            ).count()
            weekly_violations.append(day_violations)
        
        weekly_trend = {
            'labels': weekly_trend_labels,
            'bookings': weekly_bookings,
            'violations': weekly_violations
        }
        
        # 自习室使用率统计
        room_usage = []
        rooms = Rooms.objects.filter(is_active=True)
        for room in rooms:
            # 获取该自习室今日预约数
            room_bookings = Bookings.objects.filter(
                room=room,
                time__date=today,
                is_active__in=[1, 2]
            ).count()
            
            # 使用实际的座位数量
            total_seats = room.number
            usage_rate = round((room_bookings / total_seats) * 100, 1) if total_seats > 0 else 0
            
            # 获取该自习室平均评分
            avg_rating = UserEvaluation.objects.filter(room=room).aggregate(avg_rating=Avg('rating'))['avg_rating']
            avg_rating = round(avg_rating, 1) if avg_rating else 0
            
            room_usage.append({
                'name': room.name,
                'totalSeats': total_seats,
                'currentUsage': room_bookings,
                'usageRate': usage_rate,
                'todayBookings': room_bookings,
                'averageRating': avg_rating
            })
        
        # 系统决策建议（基于真实数据的智能分析）
        suggestions = []
        
        # 1. 检查高使用率自习室
        high_usage_rooms = [room for room in room_usage if room['usageRate'] >= 80]
        medium_usage_rooms = [room for room in room_usage if 60 <= room['usageRate'] < 80]
        
        if high_usage_rooms:
            room_names = ", ".join([room['name'] for room in high_usage_rooms])
            suggestions.append({
                'text': f"{room_names} 使用率超过80%，建议：1) 增加临时座位 2) 实施预约时段分流 3) 引导用户选择其他自习室",
                'priority': '高'
            })
        
        if medium_usage_rooms:
            room_names = ", ".join([room['name'] for room in medium_usage_rooms])
            suggestions.append({
                'text': f"{room_names} 使用率较高(60-80%)，建议：1) 关注高峰时段管理 2) 准备应急预案 3) 优化座位分配",
                'priority': '中'
            })
        
        # 2. 基于时段使用率的建议
        if usage_by_time['values']:
            max_usage_idx = usage_by_time['values'].index(max(usage_by_time['values']))
            peak_period = usage_by_time['labels'][max_usage_idx]
            peak_usage = usage_by_time['values'][max_usage_idx]
            
            if peak_usage > 85:
                suggestions.append({
                    'text': f"{peak_period}为高峰时段(使用率{peak_usage}%)，建议：1) 增加该时段管理员巡查 2) 实施预约限制 3) 错峰使用引导",
                    'priority': '高'
                })
        
        # 3. 违规情况分析
        if violation_count > 0:
            # 分析违规类型和趋势
            recent_violations = Blacklist.objects.filter(
                start_time__date__gte=today - timedelta(days=7)
            )
            
            if recent_violations.count() > 3:
                suggestions.append({
                    'text': f"本周新增违规{recent_violations.count()}次，趋势上升，建议：1) 加强用户行为规范培训 2) 完善违规处理流程 3) 建立预警机制",
                    'priority': '高'
                })
            elif recent_violations.count() > 0:
                suggestions.append({
                    'text': f"本周有{recent_violations.count()}次违规记录，建议关注用户行为规范，及时处理违规情况",
                    'priority': '中'
                })
        
        # 4. 用户满意度分析
        if evaluation_count > 0:
            # 分析低分评价
            low_ratings = UserEvaluation.objects.filter(rating__in=[1, 2]).count()
            if low_ratings > evaluation_count * 0.2:  # 如果低分评价超过20%
                suggestions.append({
                    'text': f"低分评价占比{round(low_ratings/evaluation_count*100, 1)}%，建议：1) 分析低分原因 2) 改善服务质量 3) 主动联系用户解决问题",
                    'priority': '高'
                })
            elif evaluation_count < 10:
                suggestions.append({
                    'text': "用户评价数量较少，建议：1) 设置评价激励机制 2) 简化评价流程 3) 定期推送评价邀请",
                    'priority': '中'
                })
        else:
            suggestions.append({
                'text': "暂无用户评价数据，建议：1) 建立评价体系 2) 鼓励用户反馈 3) 收集使用体验信息",
                'priority': '中'
            })
        
        # 5. 预约趋势分析
        if weekly_bookings:
            avg_daily_bookings = sum(weekly_bookings) / len(weekly_bookings)
            if today_bookings < avg_daily_bookings * 0.7:
                suggestions.append({
                    'text': f"今日预约量({today_bookings})低于本周平均值({round(avg_daily_bookings)})，建议：1) 检查系统状态 2) 分析下降原因 3) 加强宣传推广",
                    'priority': '中'
                })
        
        # 6. 资源利用率建议
        low_usage_rooms = [room for room in room_usage if room['usageRate'] < 30]
        if low_usage_rooms:
            room_names = ", ".join([room['name'] for room in low_usage_rooms])
            suggestions.append({
                'text': f"{room_names} 使用率较低(<30%)，建议：1) 分析原因 2) 优化环境配置 3) 调整开放时间 4) 加强宣传推广",
                'priority': '低'
            })
        
        # 7. 如果没有特殊建议，添加默认建议
        if not suggestions:
            suggestions.append({
                'text': "系统运行良好，各项指标正常。建议：1) 继续保持当前管理策略 2) 定期监控关键指标 3) 持续优化用户体验",
                'priority': '低'
            })
        
        # 构建返回数据
        data = {
            'analysisInfo': {
                'date': date_label,
                'analysisDate': analysis_date.strftime('%Y-%m-%d'),
                'totalRooms': len(room_usage),
                'totalSeats': sum(room['totalSeats'] for room in room_usage)
            },
            'statistics': {
                'todayBookings': today_bookings,
                'bookingChange': booking_change,
                'currentUsage': current_usage,
                'peakTime': peak_time_info,
                'satisfactionRate': satisfaction_rate,
                'evaluationCount': evaluation_count,
                'violationCount': violation_count,
                'violationChange': violation_change
            },
            'usageByTime': usage_by_time,
            'weeklyTrend': weekly_trend,
            'roomUsage': room_usage,
            'suggestions': suggestions
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        print(f"Error in data analysis API: {e}")
        return JsonResponse({'error': 'Internal server error'}, status=500)
