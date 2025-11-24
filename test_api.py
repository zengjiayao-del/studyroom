#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试数据分析API的脚本
"""
import os
import sys
import django
import json
from datetime import datetime, timedelta

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'studyroom.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_data_analysis_api():
    """测试数据分析API"""
    client = Client()
    
    # 模拟管理员会话
    session = client.session
    session['is_admin'] = True
    session['admin_name'] = {"name": "test_admin"}
    session.save()
    
    print("=" * 50)
    print("测试数据分析API")
    print("=" * 50)
    
    # 测试今日数据
    print("\n1. 测试今日数据:")
    response = client.get('/login/admin/data_analysis/api/?date=today')
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ API调用成功")
        print(f"   📊 分析信息: {data.get('analysisInfo', {})}")
        print(f"   📈 今日预约量: {data['statistics']['todayBookings']}")
        print(f"   📊 当前使用率: {data['statistics']['currentUsage']}%")
        print(f"   🏆 高峰时段: {data['statistics']['peakTime']}")
        print(f"   😊 用户满意度: {data['statistics']['satisfactionRate']}%")
        print(f"   ⚠️ 违规次数: {data['statistics']['violationCount']}")
        
        # 检查时段使用率数据
        usage_by_time = data.get('usageByTime', {})
        if usage_by_time.get('values'):
            print(f"   ⏰ 时段使用率数据: {len(usage_by_time['values'])}个时段")
            for i, (label, value) in enumerate(zip(usage_by_time['labels'], usage_by_time['values'])):
                print(f"      {label}: {value}%")
        
        # 检查周趋势数据
        weekly_trend = data.get('weeklyTrend', {})
        if weekly_trend.get('bookings'):
            print(f"   📅 周趋势数据: {len(weekly_trend['bookings'])}天")
            total_bookings = sum(weekly_trend['bookings'])
            total_violations = sum(weekly_trend['violations'])
            print(f"      本周总预约: {total_bookings}")
            print(f"      本周总违规: {total_violations}")
        
        # 检查自习室使用率
        room_usage = data.get('roomUsage', [])
        print(f"   🏢 自习室使用率: {len(room_usage)}个自习室")
        for room in room_usage:
            print(f"      {room['name']}: {room['usageRate']}% ({room['todayBookings']}/{room['totalSeats']})")
        
        # 检查建议
        suggestions = data.get('suggestions', [])
        print(f"   💡 系统建议: {len(suggestions)}条")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"      {i}. [{suggestion['priority']}] {suggestion['text']}")
            
    else:
        print(f"   ❌ API调用失败: {response.status_code}")
        print(f"   错误信息: {response.content.decode()}")
    
    # 测试周数据
    print("\n2. 测试近7天数据:")
    response = client.get('/login/admin/data_analysis/api/?date=week')
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ API调用成功")
        print(f"   📊 分析信息: {data.get('analysisInfo', {})}")
    else:
        print(f"   ❌ API调用失败: {response.status_code}")
    
    # 测试月数据
    print("\n3. 测试近30天数据:")
    response = client.get('/login/admin/data_analysis/api/?date=month')
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ API调用成功")
        print(f"   📊 分析信息: {data.get('analysisInfo', {})}")
    else:
        print(f"   ❌ API调用失败: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("测试完成！")
    print("=" * 50)

if __name__ == '__main__':
    test_data_analysis_api()