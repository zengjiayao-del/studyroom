# from django.utils import timezone
import email
import random
import time
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.utils import timezone
import socket
from login.models import *
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.urls import reverse
import re
from django.conf import settings
from .models import TodoItem, BackgroundMusic
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
from django.views import View
from datetime import timedelta

# Create your views here.


def index(request):
    """首页视图"""
    if not request.session.get('name'):
        return redirect('login')
    return render(request, 'index/index.html')


def bookings(request):
    try:
        room = Rooms.objects.filter(is_active=True)

    except Exception as e:
        print(e)

    return render(request, 'index/Bookings.html', {"room": room})


def seat(request, id):
    try:
        room = Rooms.objects.get(id=id)
        rooms = Rooms.objects.filter(is_active=True)
    except Exception as e:
        print(e)
    if request.method == "GET":
        room_selected = request.GET.get('room_id')
        if room_selected:

            time_selected_r = int(request.GET.get('day'))  # 日期
            time_selected_s = int(request.GET.get('time'))  # 时间

            # 日期判断
            d1 = timezone.now()
            time = int(d1.day)
            if time_selected_r == 1:
                time = time
            elif time_selected_r == 2:
                time = time + 1
            # print(time)
            try:
                room_1 = Rooms.objects.get(id=room_selected)
                booking = Bookings.objects.filter(
                    time__day=time,
                    period=time_selected_s,
                    room_id=room_1,
                    is_active=True)

            except Exception as e:
                print(e)
            seat_dict = {}
            for i in range(1, room.number + 1):
                seat_dict[str(i)] = 0
            for i in booking:
                # print("座位号", i.id)
                seat_dict[str(i.number)] = 1

            return render(request, 'index/seat_id.html', {"room": room,
                                                          "rooms": rooms,
                                                          "seat": seat_dict,
                                                          "room_id": room_selected,  # 选择上页自习室一致
                                                          "time_selected_r": time_selected_r,
                                                          "time_selected_s": time_selected_s,
                                                          "room_1": room_1.name,
                                                          })
        else:
            return render(request, 'index/seat.html', {"room": room,
                                                       "rooms": rooms,
                                                       "room_id": room.id})
    elif request.method == 'POST':
        try:
            room_1 = request.POST['room']
            number = request.POST['number']
            period = int(request.POST['time'])
            name = request.session.get('name')
            name = name['name']
            day_selection = int(request.POST['day'])
            # print(room_1, number, period, day_selection, name)
        except Exception as e:
            print(f"Error parsing POST data: {e}")
            return HttpResponseRedirect(request.path_info)

        today_date = timezone.now().date()
        if day_selection == 1:
            target_date = today_date
        elif day_selection == 2:
            target_date = today_date + timedelta(days=1)
        else:
            print("Invalid day selection received in POST")
            return HttpResponseRedirect(request.path_info)

        try:
            student = Students.objects.get(name=name)
            existing_booking = Bookings.objects.filter(
                students_id=student.id,
                time__date=target_date,
                period=period,
                is_active=True
            ).first()

        except Students.DoesNotExist:
            print(f"Student {name} not found.")
            return HttpResponseRedirect(request.path_info)
        except Exception as e:
            print(f"Error querying existing bookings: {e}")
            return HttpResponseRedirect(request.path_info)

        if existing_booking:
            msg = "alert-warning"
            message_text = f"您在 {target_date.strftime('%Y-%m-%d')} 的该时间段已有预约，无法重复预约。"
            room = Rooms.objects.get(id=room_1)
            rooms = Rooms.objects.filter(is_active=True)
            return render(request, 'index/seat.html', {
                "rooms": rooms, 
                "room": room, 
                "room_id": room.id, 
                "msg": msg, 
                "message_text": message_text
            })
        else:
            try:
                booking = Bookings.objects.create(
                    students=student,
                    number=int(number),
                    room_id=room_1,
                    period=period,
                    time=timezone.make_aware(timezone.datetime.combine(target_date, timezone.datetime.min.time()))
                )
                if student.email:
                    student_email = student.email
                    student_name = student.name
                    print(f"Booking confirmation email logic for {student_name} ({student_email})")
                    try:
                        send_booking_confirmation(student_email, student_name)
                        print(f"Successfully attempted to send booking confirmation to {student_email}")
                    except Exception as mail_error:
                        print(f"Error sending booking confirmation email to {student_email}: {mail_error}")
                else:
                    print(f"学生 {student.name} 信息中没有邮箱")
            except Exception as e:
                print(f"Error creating new booking: {e}")
            return HttpResponseRedirect(reverse('recording'))


def recording(request):
    # 检查用户是否已登录
    student_session = request.session.get('name')
    if not student_session:
        # 如果用户未登录，重定向到登录页面
        return HttpResponseRedirect('/login/')
    
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    student_name = student_session['name']
    id = request.GET.get('id')
    if id:
        try:
            booking = Bookings.objects.get(id=id)
        except Exception as e:
            print(e)
        booking.is_active = False
        booking.save()
        return HttpResponseRedirect("/index/recording/")
    try:
        student = Students.objects.get(name=student_name).id
        booking = Bookings.objects.filter(students_id=student).order_by('-time')
        # 日期判断
        d1 = timezone.now()
        day = int(d1.day)
        month = int(d1.month)
        return render(request, 'index/Recording.html', {"booking": booking, "day": day, "month": month, "ip": ip})
    except Exception as e:
        print(e)
        # 如果查询出错，返回空列表
        return render(request, 'index/Recording.html', {"booking": [], "day": 0, "month": 0, "ip": ip})


def warn(request):
    # 检查用户是否已登录
    student_session = request.session.get('name')
    if not student_session:
        # 如果用户未登录，重定向到登录页面
        return redirect('/login/')
    
    try:
        student_name = student_session['name']
        student = Students.objects.get(name=student_name)
        integrals = Integrals.objects.filter(is_active=True, student_id=student.id)
        return render(request, 'index/warn.html', {"integrals": integrals})
    except Exception as e:
        print(f"警告记录页面错误: {e}")
        # 如果出现其他错误，也重定向到登录页面
        return redirect('/login/')


def sign_url(request):
    if request.method == 'GET':
        student = request.session.get('name')
        student = student['name']
        code = request.GET.get('sign_code', '')

        if code:
            # 获取最新的签到码（10分钟内有效）
            from django.utils import timezone
            from datetime import timedelta
            
            ten_minutes_ago = timezone.now() - timedelta(minutes=10)
            sign = SignCode.objects.filter(time__gte=ten_minutes_ago).order_by('-time').first()
            
            if not sign:
                msg = "签到码已过期，请重新获取！"
                alert = "alert"
                return render(request, 'index/sign_url.html', {"alert": alert, "msg": msg})
            
            if str(sign.text) != code:
                msg = "签到码错误！"
                alert = "alert"
                return render(request, 'index/sign_url.html', {"alert": alert, "msg": msg})
            d1 = timezone.now()
            new_period = d1.hour
            if 7 <= new_period <= 12:  # 早上7点到中午12点
                period = 1
            elif 12 < new_period <= 14:  # 中午12点到下午2点
                period = 2
            elif 14 < new_period <= 22:  # 下午2点到晚上10点
                period = 3
            else:
                msg = "你不在签到时间内！"
                alert = "alert"
                return render(request, 'index/sign_url.html', {"alert": alert, "msg": msg})
            try:

                time = int(d1.day)
                student = Students.objects.get(name=student)
                book = Bookings.objects.filter(
                    students_id=student.id,
                    time__day=time,
                    period=period,
                    is_active=1)

                if book:
                    print('if book')
                    book[0].is_active = 2
                    book[0].save()
                    msg = "签到成功！！"
                    alert = "alert"
                    return render(request, 'index/sign_url.html', {"alert": alert, "msg": msg})
                else:
                    msg = "你没有预约！"
                    alert = "alert"
                    return render(request, 'index/sign_url.html', {"alert": alert, "msg": msg})

            except Exception as e:
                msg = "你没有预约！"
                alert = "alert"
                return render(request, 'index/sign_url.html', {"alert": alert, "msg": msg})

        return render(request, 'index/sign_url.html')
    elif request.method == 'POST':
        return render(request, 'index/sign_url.html')


def sign_code(request):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]

    code = ''
    for i in range(1, 7):
        code += str(random.randint(0, 9))
    
    # 创建新的签到码记录
    sign_code_obj = SignCode.objects.create(text=int(code))
    
    # 获取当前时间
    from django.utils import timezone
    current_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return render(request, 'index/sign_code.html', {
        'sign_code': int(code), 
        "local_ip": ip,
        "current_time": current_time
    })

def get_sign_code():
    # 获取最新的签到码记录
    latest_sign_code = SignCode.objects.order_by('-id').first()
    if latest_sign_code:
        # 如果存在最新的签到码记录，直接返回它的文本内容
        return str(latest_sign_code.text)
    else:
        # 如果数据库中没有签到码记录，生成一个新的签到码并返回
        new_code = str(random.randint(100, 999))
        SignCode.objects.create(text=new_code)
        return new_code

def send_confirmation_email(to_email, subject, message):
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [to_email], fail_silently=False)
        print(f"邮件已发送到 {to_email}")
    except Exception as e:
        print(f"发送邮件时出现错误：{e}")

def send_booking_confirmation(student_email, student_name):
    subject = '自习室预约确认'
    message = f'亲爱的{student_name}，\n\n您的自习室预约已成功！\n\n祝您学习愉快！'
    send_confirmation_email(student_email, subject, message)

def logout(request):
    """用户退出登录"""
    if request.session.get('name'):
        # 清除 session 的所有内容可能更彻底
        request.session.flush()
        # 或者只删除特定的键
        # del request.session['name']
    # 重定向到Django的用户登录页面
    return HttpResponseRedirect('/login/')

@csrf_exempt
def add_todo(request):
    """添加待办事项"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            content = data.get('content')
            if not content:
                return JsonResponse({'status': 'error', 'message': '内容不能为空'}, status=400)
                
            # 从 session 中获取用户信息
            user_info = request.session.get('name')
            if not user_info or not isinstance(user_info, dict):
                return JsonResponse({'status': 'error', 'message': '用户会话无效'}, status=401)
                
            # 使用用户名查找用户
            try:
                user = Students.objects.get(name=user_info['name'])
            except Students.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=400)
                
            todo = TodoItem.objects.create(user=user, content=content)
            return JsonResponse({
                'status': 'success',
                'message': '添加成功',
                'id': todo.id,
                'content': todo.content
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的 JSON 数据'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': '无效的请求'}, status=400)

@csrf_exempt
def get_todos(request):
    """获取用户的所有待办事项"""
    try:
        # 从 session 中获取用户信息
        user_info = request.session.get('name')
        if not user_info or not isinstance(user_info, dict):
            return JsonResponse({'status': 'error', 'message': '用户会话无效'}, status=401)
            
        # 使用用户名查找用户
        try:
            user = Students.objects.get(name=user_info['name'])
        except Students.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=400)
            
        todos = TodoItem.objects.filter(user=user).order_by('-id')
        todos_data = [{
            'id': todo.id,
            'content': todo.content,
            'completed': todo.completed
        } for todo in todos]
        return JsonResponse({
            'status': 'success',
            'todos': todos_data
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@csrf_exempt
def update_todo(request, todo_id):
    """更新待办事项状态"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            completed = data.get('completed', False)
            
            # 从 session 中获取用户信息
            user_info = request.session.get('name')
            if not user_info or not isinstance(user_info, dict):
                return JsonResponse({'status': 'error', 'message': '用户会话无效'}, status=401)
                
            # 使用用户名查找用户
            try:
                user = Students.objects.get(name=user_info['name'])
            except Students.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=400)
                
            # 确保待办事项属于当前用户
            todo = TodoItem.objects.get(id=todo_id, user=user)
            todo.completed = completed
            todo.save()
            
            return JsonResponse({
                'status': 'success',
                'message': '更新成功'
            })
        except TodoItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '待办事项不存在或无权限'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': '无效的 JSON 数据'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': '无效的请求'}, status=400)

@csrf_exempt
def delete_todo(request, todo_id):
    """删除待办事项"""
    if request.method == 'POST':
        try:
            # 从 session 中获取用户信息
            user_info = request.session.get('name')
            if not user_info or not isinstance(user_info, dict):
                return JsonResponse({'status': 'error', 'message': '用户会话无效'}, status=401)
                
            # 使用用户名查找用户
            try:
                user = Students.objects.get(name=user_info['name'])
            except Students.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=400)
                
            # 确保待办事项属于当前用户
            todo = TodoItem.objects.get(id=todo_id, user=user)
            todo.delete()
            
            return JsonResponse({
                'status': 'success',
                'message': '删除成功'
            })
        except TodoItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '待办事项不存在或无权限'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': '无效的请求'}, status=400)

def change_password(request):
    """修改密码视图"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            old_password = data.get('old_password')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')
            
            if not all([old_password, new_password, confirm_password]):
                return JsonResponse({'status': 'error', 'message': '所有字段都必须填写'}, status=400)
                
            if new_password != confirm_password:
                return JsonResponse({'status': 'error', 'message': '两次输入的新密码不一致'}, status=400)
                
            user = Students.objects.get(id=request.session['name'])
            if user.password != old_password:  # 在实际应用中应该使用加密后的密码比较
                return JsonResponse({'status': 'error', 'message': '原密码错误'}, status=400)
                
            user.password = new_password  # 在实际应用中应该存储加密后的密码
            user.save()
            return JsonResponse({'status': 'success', 'message': '密码修改成功'})
            
        except Students.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return render(request, 'index/change_password.html')

def change_avatar(request):
    if not request.session.get('is_login', None):
        return redirect('/login/')
    
    if request.method == 'POST':
        avatar = request.FILES.get('avatar')
        if avatar:
            # 生成唯一的文件名
            file_ext = os.path.splitext(avatar.name)[1]
            new_filename = f"Students/photo/{request.session['user_id']}_{avatar.name}"
            
            # 保存文件
            path = default_storage.save(new_filename, ContentFile(avatar.read()))
            
            # 更新数据库
            student = Students.objects.get(id=request.session['user_id'])
            student.photo = path
            student.save()
            
            # 更新session中的头像信息
            request.session['name']['photo'] = path
            request.session.modified = True
            
            messages.success(request, '头像更新成功！')
            return redirect('/')
        else:
            messages.error(request, '请选择要上传的头像文件！')
    
    return render(request, 'index/change_avatar.html')

class MusicListView(View):
    def get(self, request):
        try:
            music_list = BackgroundMusic.objects.filter(is_active=True)
            music_data = [{
                'id': music.id,
                'title': music.title,
                'audio_file': f'/static/{music.audio_file}'
            } for music in music_list]
            
            return JsonResponse({
                'status': 'success',
                'data': music_data
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

class MusicDetailView(View):
    def get(self, request, music_id):
        try:
            music = BackgroundMusic.objects.get(id=music_id, is_active=True)
            return JsonResponse({
                'status': 'success',
                'data': {
                    'id': music.id,
                    'title': music.title,
                    'audio_url': f'/static/{music.audio_file}'
                }
            })
        except BackgroundMusic.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': '音乐不存在'
            }, status=404)


# ==================== 用户管理功能 ====================

def user_management(request):
    """用户信息管理页面"""
    if not request.session.get('is_login'):
        return redirect('/login/')
    
    user_id = request.session.get('user_id')
    try:
        user = Students.objects.get(id=user_id)
        
        # 获取用户的评价记录
        evaluations = UserEvaluation.objects.filter(student=user).order_by('-time')
        
        # 获取所有自习室数据
        rooms = Rooms.objects.filter(is_active=True)
        
        context = {
            'user': user,
            'evaluations': evaluations,
            'rooms': rooms  # 添加自习室数据
        }
        
        return render(request, 'index/user_management.html', context)
        
    except Students.DoesNotExist:
        return redirect('/login/')


def complaint_management(request):
    """用户投诉管理页面"""
    if not request.session.get('is_login'):
        return redirect('/login/')
    
    user_id = request.session.get('user_id')
    try:
        user = Students.objects.get(id=user_id)
        
        # 获取用户的投诉记录
        complaints = UserComplaint.objects.filter(student=user).order_by('-time')
        
        context = {
            'user': user,
            'complaints': complaints
        }
        
        return render(request, 'index/complaint_management.html', context)
        
    except Students.DoesNotExist:
        return redirect('/login/')


def complaint_feedback_view(request, complaint_id):
    """投诉反馈信息页面"""
    if not request.session.get('is_login'):
        return redirect('/login/')
    
    try:
        complaint = UserComplaint.objects.get(id=complaint_id)
        feedbacks = ComplaintFeedback.objects.filter(complaint=complaint).order_by('-feedback_time')
        
        context = {
            'complaint': complaint,
            'feedbacks': feedbacks
        }
        
        return render(request, 'index/complaint_feedback.html', context)
        
    except UserComplaint.DoesNotExist:
        messages.error(request, '投诉记录不存在')
        return redirect('complaint_management')


def blacklist_management(request):
    """用户端黑名单管理页面 - 查看个人黑名单状态和申请撤销"""
    # 检查用户是否登录 - 使用多种方式检查登录状态
    if not request.session.get('is_login') and not request.session.get('name'):
        return redirect('/login/')
    
    # 获取当前用户
    user_id = request.session.get('user_id')
    user_name = None
    
    # 如果user_id不存在，尝试从session['name']中获取用户名
    if not user_id and request.session.get('name'):
        user_name = request.session['name'].get('name')
        if user_name:
            try:
                current_user = Students.objects.get(name=user_name)
                user_id = current_user.id
                # 更新session中的user_id
                request.session['user_id'] = user_id
                request.session['is_login'] = True
            except Students.DoesNotExist:
                return redirect('/login/')
    
    if not user_id:
        return redirect('/login/')
    
    try:
        current_user = Students.objects.get(id=user_id)
    except Students.DoesNotExist:
        return redirect('/login/')
    
    # 获取当前用户的黑名单记录 - 使用first()确保只返回一个记录
    blacklist_record = None
    removal_request = None
    
    try:
        # 使用first()而不是get()，确保即使有多个记录也只返回第一个
        blacklist_record = Blacklist.objects.filter(student=current_user, is_active=True).first()
        
        # 如果找到黑名单记录，获取对应的撤销申请记录
        if blacklist_record:
            removal_request = BlacklistRemovalRequest.objects.filter(
                student=current_user, 
                blacklist=blacklist_record
            ).order_by('-created_at').first()
    except Exception as e:
        print(f"获取黑名单记录时出错: {e}")
        blacklist_record = None
    
    # 获取历史黑名单记录（曾经被加入过黑名单但已撤销的记录）
    historical_blacklist_records = Blacklist.objects.filter(
        student=current_user, 
        is_active=False
    ).order_by('-start_time')
    
    # 获取历史撤销申请记录
    historical_removal_requests = BlacklistRemovalRequest.objects.filter(
        student=current_user
    ).exclude(status='pending').order_by('-created_at')
    
    if request.method == 'POST':
        # 处理撤销申请
        appeal_reason = request.POST.get('appeal_reason')
        
        if blacklist_record and appeal_reason:
            # 创建撤销申请
            BlacklistRemovalRequest.objects.create(
                blacklist=blacklist_record,
                student=current_user,
                appeal_reason=appeal_reason,
                status='pending'
            )
            messages.success(request, '撤销申请已提交，等待管理员审核')
            return redirect('blacklist_management')
        else:
            messages.error(request, '请填写申诉理由')
    
    context = {
        'blacklist_record': blacklist_record,
        'removal_request': removal_request,
        'current_user': current_user,
        'historical_blacklist_records': historical_blacklist_records,
        'historical_removal_requests': historical_removal_requests
    }
    
    return render(request, 'index/blacklist_management.html', context)


def submit_complaint(request):
    """提交投诉处理视图"""
    if not request.session.get('is_login'):
        return redirect('/login/')
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            complaint_type = request.POST.get('complaint_type')
            complaint_title = request.POST.get('complaint_title')
            complaint_content = request.POST.get('complaint_content')
            
            # 验证必填字段
            if not all([complaint_type, complaint_title, complaint_content]):
                messages.error(request, '请填写完整的投诉信息')
                return redirect('complaint_management')
            
            # 获取当前用户
            user_id = request.session.get('user_id')
            user = Students.objects.get(id=user_id)
            
            # 创建投诉记录
            complaint = UserComplaint.objects.create(
                student=user,
                complaint_type=complaint_type,
                title=complaint_title,
                content=complaint_content,
                status='pending'
            )
            
            messages.success(request, '投诉提交成功！我们会尽快处理您的反馈。')
            return redirect('complaint_management')
            
        except Students.DoesNotExist:
            messages.error(request, '用户信息不存在')
            return redirect('/login/')
        except Exception as e:
            messages.error(request, f'提交投诉时发生错误: {str(e)}')
            return redirect('complaint_management')
    
    # 如果不是POST请求，重定向到投诉管理页面
    return redirect('complaint_management')


# ==================== 违约记录功能 ====================

@csrf_exempt
def get_user_violation_count(request):
    """获取用户违约记录数量"""
    try:
        # 从 session 中获取用户信息
        user_info = request.session.get('name')
        if not user_info or not isinstance(user_info, dict):
            return JsonResponse({'status': 'error', 'message': '用户会话无效'}, status=401)
            
        # 使用用户名查找用户
        try:
            user = Students.objects.get(name=user_info['name'])
        except Students.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=400)
            
        # 获取用户的违约记录数量
        violation_count = Integrals.objects.filter(student=user, is_active=True).count()
        
        return JsonResponse({
            'status': 'success',
            'violation_count': violation_count
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def manual_check_violations(request):
    """管理员手动检查违约记录页面"""
    # 检查是否为管理员
    if not request.session.get('is_admin'):
        return redirect('/admin/login/')
    
    # 获取所有违约记录
    violations = Integrals.objects.filter(is_active=True).order_by('-time')
    
    # 获取所有学生信息
    students = Students.objects.all()
    
    context = {
        'violations': violations,
        'students': students
    }
    
    return render(request, 'index/manual_check_violations.html', context)


# ==================== 用户管理功能 ====================

def user_management(request):
    """用户信息管理页面"""
    if not request.session.get('is_login'):
        return redirect('/login/')
    
    user_id = request.session.get('user_id')
    try:
        user = Students.objects.get(id=user_id)
        
        # 获取用户的评价记录
        evaluations = UserEvaluation.objects.filter(student=user).order_by('-time')
        
        # 获取所有自习室数据
        rooms = Rooms.objects.filter(is_active=True)
        
        context = {
            'user': user,
            'evaluations': evaluations,
            'rooms': rooms  # 添加自习室数据
        }
        
        return render(request, 'index/user_management.html', context)
        
    except Students.DoesNotExist:
        return redirect('/login/')


def complaint_management(request):
    """用户投诉管理页面"""
    if not request.session.get('is_login'):
        return redirect('/login/')
    
    user_id = request.session.get('user_id')
    try:
        user = Students.objects.get(id=user_id)
        
        # 获取用户的投诉记录
        complaints = UserComplaint.objects.filter(student=user).order_by('-time')
        
        context = {
            'user': user,
            'complaints': complaints
        }
        
        return render(request, 'index/complaint_management.html', context)
        
    except Students.DoesNotExist:
        return redirect('/login/')


def complaint_feedback_view(request, complaint_id):
    """投诉反馈信息页面"""
    if not request.session.get('is_login'):
        return redirect('/login/')
    
    try:
        complaint = UserComplaint.objects.get(id=complaint_id)
        feedbacks = ComplaintFeedback.objects.filter(complaint=complaint).order_by('-feedback_time')
        
        context = {
            'complaint': complaint,
            'feedbacks': feedbacks
        }
        
        return render(request, 'index/complaint_feedback.html', context)
        
    except UserComplaint.DoesNotExist:
        messages.error(request, '投诉记录不存在')
        return redirect('complaint_management')


def blacklist_management(request):
    """用户端黑名单管理页面 - 查看个人黑名单状态和申请撤销"""
    # 检查用户是否登录 - 使用多种方式检查登录状态
    if not request.session.get('is_login') and not request.session.get('name'):
        return redirect('/login/')
    
    # 获取当前用户
    user_id = request.session.get('user_id')
    user_name = None
    
    # 如果user_id不存在，尝试从session['name']中获取用户名
    if not user_id and request.session.get('name'):
        user_name = request.session['name'].get('name')
        if user_name:
            try:
                current_user = Students.objects.get(name=user_name)
                user_id = current_user.id
                # 更新session中的user_id
                request.session['user_id'] = user_id
                request.session['is_login'] = True
            except Students.DoesNotExist:
                return redirect('/login/')
    
    if not user_id:
        return redirect('/login/')
    
    try:
        current_user = Students.objects.get(id=user_id)
    except Students.DoesNotExist:
        return redirect('/login/')
    
    # 获取当前用户的黑名单记录 - 使用first()确保只返回一个记录
    blacklist_record = None
    removal_request = None
    
    try:
        # 使用first()而不是get()，确保即使有多个记录也只返回第一个
        blacklist_record = Blacklist.objects.filter(student=current_user, is_active=True).first()
        
        # 如果找到黑名单记录，获取对应的撤销申请记录
        if blacklist_record:
            removal_request = BlacklistRemovalRequest.objects.filter(
                student=current_user, 
                blacklist=blacklist_record
            ).order_by('-created_at').first()
    except Exception as e:
        print(f"获取黑名单记录时出错: {e}")
        blacklist_record = None
    
    # 获取历史黑名单记录（曾经被加入过黑名单但已撤销的记录）
    historical_blacklist_records = Blacklist.objects.filter(
        student=current_user, 
        is_active=False
    ).order_by('-start_time')
    
    # 获取历史撤销申请记录
    historical_removal_requests = BlacklistRemovalRequest.objects.filter(
        student=current_user
    ).exclude(status='pending').order_by('-created_at')
    
    if request.method == 'POST':
        # 处理撤销申请
        appeal_reason = request.POST.get('appeal_reason')
        
        if blacklist_record and appeal_reason:
            # 创建撤销申请
            BlacklistRemovalRequest.objects.create(
                blacklist=blacklist_record,
                student=current_user,
                appeal_reason=appeal_reason,
                status='pending'
            )
            messages.success(request, '撤销申请已提交，等待管理员审核')
            return redirect('blacklist_management')
        else:
            messages.error(request, '请填写申诉理由')
    
    context = {
        'blacklist_record': blacklist_record,
        'removal_request': removal_request,
        'current_user': current_user,
        'historical_blacklist_records': historical_blacklist_records,
        'historical_removal_requests': historical_removal_requests
    }
    
    return render(request, 'index/blacklist_management.html', context)


def submit_complaint(request):
    """提交投诉处理视图"""
    if not request.session.get('is_login'):
        return redirect('/login/')
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            complaint_type = request.POST.get('complaint_type')
            complaint_title = request.POST.get('complaint_title')
            complaint_content = request.POST.get('complaint_content')
            
            # 验证必填字段
            if not all([complaint_type, complaint_title, complaint_content]):
                messages.error(request, '请填写完整的投诉信息')
                return redirect('complaint_management')
            
            # 获取当前用户
            user_id = request.session.get('user_id')
            user = Students.objects.get(id=user_id)
            
            # 创建投诉记录
            complaint = UserComplaint.objects.create(
                student=user,
                complaint_type=complaint_type,
                title=complaint_title,
                content=complaint_content,
                status='pending'
            )
            
            messages.success(request, '投诉提交成功！我们会尽快处理您的反馈。')
            return redirect('complaint_management')
            
        except Students.DoesNotExist:
            messages.error(request, '用户信息不存在')
            return redirect('/login/')
        except Exception as e:
            messages.error(request, f'提交投诉时发生错误: {str(e)}')
            return redirect('complaint_management')
    
    # 如果不是POST请求，重定向到投诉管理页面
    return redirect('complaint_management')


# ==================== 违约记录功能 ====================

@csrf_exempt
def get_user_violation_count(request):
    """获取用户违约记录数量"""
    try:
        # 从 session 中获取用户信息
        user_info = request.session.get('name')
        if not user_info or not isinstance(user_info, dict):
            return JsonResponse({'status': 'error', 'message': '用户会话无效'}, status=401)
            
        # 使用用户名查找用户
        try:
            user = Students.objects.get(name=user_info['name'])
        except Students.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用户不存在'}, status=400)
            
        # 获取用户的违约记录数量
        violation_count = Integrals.objects.filter(student=user, is_active=True).count()
        
        return JsonResponse({
            'status': 'success',
            'violation_count': violation_count
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


def manual_check_violations(request):
    """管理员手动检查违约记录页面"""
    # 检查是否为管理员
    if not request.session.get('is_admin'):
        return redirect('/admin/login/')
    
    # 获取所有违约记录
    violations = Integrals.objects.filter(is_active=True).order_by('-time')
    
    # 获取所有学生信息
    students = Students.objects.all()
    
    context = {
        'violations': violations,
        'students': students
    }
    
    return render(request, 'index/manual_check_violations.html', context)
