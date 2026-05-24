"""
test_device_upload.py - 传感器设备上传数据测试脚本
===============================================
用途：模拟 ESP32 / Android App / 蓝牙设备等向系统上传传感器数据。

使用前提：
    1. 确保 Flask 服务已启动: python app.py
    2. 运行本脚本: python test_device_upload.py

测试流程：
    1. 注册 3 个不同类型的设备
    2. 查看设备列表
    3. 各设备上传传感器数据（含自动分析）
    4. 查询最新读数和历史读数
    5. 测试异常数据拦截
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"


def p(title):
    """打印分隔标题。"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def api(method, path, **kwargs):
    """统一 API 调用。"""
    url = f"{BASE_URL}{path}"
    try:
        resp = requests.request(method, url, timeout=10, **kwargs)
        return resp.json()
    except requests.exceptions.ConnectionError:
        print(f"  ❌ 无法连接到 {BASE_URL}，请确保 Flask 服务已启动")
        return None
    except Exception as e:
        print(f"  ❌ 请求失败: {e}")
        return None


# ================================================================
# 测试 1: 注册设备
# ================================================================
p("测试 1: 注册设备")

devices = [
    {
        "device_name": "一号试验田传感器",
        "device_code": "ESP32-001",
        "device_type": "esp32",
        "field_id": 2,  # 一号试验田
    },
    {
        "device_name": "二号试验田蓝牙",
        "device_code": "BT-002",
        "device_type": "bluetooth",
        "field_id": 3,  # 二号试验田
    },
    {
        "device_name": "Android 移动采集",
        "device_code": "ANDROID-001",
        "device_type": "android",
        "field_id": None,  # 不绑定地块
    },
]

for dev in devices:
    result = api("POST", "/api/device/register", json=dev)
    if result:
        status = "✅" if result.get("success") else "⚠️"
        print(f"  {status} {dev['device_name']} ({dev['device_code']}): {result.get('message', '')}")


# ================================================================
# 测试 2: 查看设备列表
# ================================================================
p("测试 2: 查看设备列表")

result = api("GET", "/api/device/list")
if result and result.get("success"):
    data = result["data"]
    print(f"  共 {len(data)} 台设备:")
    for d in data:
        online = "🟢 在线" if d["status"] == "online" else "⚫ 离线"
        print(f"    [{d['device_type']}] {d['device_name']} ({d['device_code']}) — {online}")
else:
    print(f"  ❌ 查询失败: {result}")


# ================================================================
# 测试 3: 上传传感器数据（含自动分析）
# ================================================================
p("测试 3: 上传传感器数据")

readings = [
    {
        "desc": "ESP32-001 正常数据（果实膨大期）",
        "device_code": "ESP32-001",
        "ph": 6.0, "nitrogen": 80, "phosphorus": 45, "potassium": 280,
        "humidity": 25, "temperature": 26, "ec": 1200, "organic_matter": 3.5,
        "growth_stage": "expansion", "auto_analyze": True,
    },
    {
        "desc": "BT-002 酸性数据（幼苗期）",
        "device_code": "BT-002",
        "ph": 4.2, "nitrogen": 90, "phosphorus": 50, "potassium": 150,
        "humidity": 28, "temperature": 24, "ec": 1000, "organic_matter": 2.8,
        "growth_stage": "seedling", "auto_analyze": True,
    },
    {
        "desc": "ANDROID-001 高盐数据（采收期）",
        "device_code": "ANDROID-001",
        "ph": 7.2, "nitrogen": 45, "phosphorus": 25, "potassium": 120,
        "humidity": 18, "temperature": 24, "ec": 3200, "organic_matter": 0.8,
        "growth_stage": "harvest", "auto_analyze": True,
    },
    {
        "desc": "ESP32-001 仅上传不做分析",
        "device_code": "ESP32-001",
        "ph": 6.1, "nitrogen": 82, "phosphorus": 47, "potassium": 290,
        "humidity": 24, "temperature": 27, "ec": 1180, "organic_matter": 3.6,
        "growth_stage": "expansion", "auto_analyze": False,
    },
]

for rd in readings:
    result = api("POST", "/api/device/upload", json=rd)
    if result:
        status = "✅" if result.get("success") else "❌"
        extra = ""
        if result.get("record_id"):
            extra += f"  分析记录#{result['record_id']}"
            if result.get("health_score"):
                extra += f" 评分{result['health_score']}"
            if result.get("risk_level"):
                extra += f" ({result['risk_level']})"
        if result.get("alerts"):
            for a in result["alerts"]:
                extra += f"\n    🚨 预警: {a.get('name', a.get('level', ''))}"
        print(f"  {status} {rd['desc']}{extra}")
    else:
        print(f"  ❌ 请求失败")


# ================================================================
# 测试 4: 查询设备最新读数
# ================================================================
p("测试 4: 查询设备最新读数")

for code in ["ESP32-001", "BT-002"]:
    result = api("GET", f"/api/device/latest?device_code={code}")
    if result and result.get("success"):
        data = result["data"]
        if data:
            print(f"  📡 {code} 最新读数: pH={data['ph']}, N={data['nitrogen']}, P={data['phosphorus']}, K={data['potassium']}, 湿度={data['humidity']}%")
        else:
            print(f"  📡 {code}: 暂无读数")
    else:
        print(f"  ❌ {code} 查询失败")


# ================================================================
# 测试 5: 查询设备历史读数
# ================================================================
p("测试 5: 查询设备历史读数（ESP32-001，最近 5 条）")

result = api("GET", "/api/device/readings?device_code=ESP32-001&limit=5")
if result and result.get("success"):
    data = result["data"]
    print(f"  ESP32-001 共 {len(data)} 条读数记录:")
    for r in data:
        print(f"    [{r['created_at']}] pH={r['ph']} N={r['nitrogen']} P={r['phosphorus']} K={r['potassium']}")
else:
    print(f"  ❌ 查询失败")


# ================================================================
# 测试 6: 异常数据拦截
# ================================================================
p("测试 6: 异常数据拦截")

bad_data = [
    {
        "desc": "未注册的设备",
        "payload": {"device_code": "UNKNOWN-DEVICE", "ph": 6.0},
    },
    {
        "desc": "pH 超出范围",
        "payload": {"device_code": "ESP32-001", "ph": 15.0},
    },
    {
        "desc": "氮为负数",
        "payload": {"device_code": "ESP32-001", "nitrogen": -5},
    },
    {
        "desc": "湿度超出范围",
        "payload": {"device_code": "ESP32-001", "humidity": 150},
    },
]

for bad in bad_data:
    result = api("POST", "/api/device/upload", json=bad["payload"])
    if result:
        if result.get("success"):
            print(f"  ⚠️ {bad['desc']}: 未被拦截（预期应失败）")
        else:
            print(f"  ✅ {bad['desc']}: 正确拦截 — {result.get('message', '')}")
    else:
        print(f"  ❌ {bad['desc']}: 请求失败")


# ================================================================
# 测试 7: 重复注册测试
# ================================================================
p("测试 7: 重复注册测试")

dup = {
    "device_name": "重复设备",
    "device_code": "ESP32-001",  # 已存在
    "device_type": "sensor",
}
result = api("POST", "/api/device/register", json=dup)
if result:
    if result.get("success"):
        print(f"  ⚠️ 重复注册未被拦截")
    else:
        print(f"  ✅ 重复注册正确拦截: {result.get('message', '')}")


# ================================================================
# 完成
# ================================================================
p("测试完成")
print("  所有测试已执行完毕。")
print(f"  可以访问 {BASE_URL}/devices 查看设备管理页面。")
print(f"  可以访问 {BASE_URL}/history 查看自动分析生成的记录。")
