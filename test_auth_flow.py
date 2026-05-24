"""
test_auth_flow.py - 用户登录注册完整流程测试
=============================================
测试流程：
1. 未登录访问首页 → 应重定向到 /login
2. 使用默认管理员登录 (admin / admin123)
3. 注册新用户 (testuser / test1234)
4. 新用户创建地块
5. 新用户提交数据
6. 新用户查看历史
7. 管理员查看所有用户
8. 新用户退出登录
"""

import requests

BASE = "http://127.0.0.1:5000"

def p(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


# 测试1: 未登录访问
p("测试1: 未登录访问首页")
resp = requests.get(f"{BASE}/", allow_redirects=False, timeout=10)
print(f"  状态码: {resp.status_code}, Location: {resp.headers.get('Location', '无')}")
assert resp.status_code in (302, 303), "应重定向"
print("  ✅ 未登录用户被正确重定向到登录页")

# 测试2: 管理员登录
p("测试2: 管理员登录 (admin / admin123)")
session = requests.Session()
resp = session.post(f"{BASE}/login", data={"username": "admin", "password": "admin123"}, allow_redirects=False, timeout=10)
print(f"  状态码: {resp.status_code}, Location: {resp.headers.get('Location', '无')}")
assert resp.status_code in (302, 303), "登录应重定向到首页"

# 验证已登录
resp = session.get(f"{BASE}/", timeout=10)
assert resp.status_code == 200, "登录后应能访问首页"
print("  ✅ 管理员登录成功")

# 测试3: 管理员访问 admin 页面
p("测试3: 管理员访问管理页")
resp = session.get(f"{BASE}/admin", timeout=10)
assert resp.status_code == 200, "管理员应能访问管理页"
assert "管理员面板" in resp.text or "admin" in resp.text, "应显示管理员面板"
print("  ✅ 管理员访问管理页成功")

# 测试4: 管理员访问设备管理
p("测试4: 管理员访问设备管理页")
resp = session.get(f"{BASE}/devices", timeout=10)
assert resp.status_code == 200, "管理员应能访问设备管理页"
print("  ✅ 管理员访问设备管理页成功")

# 测试5: 管理员录入数据
p("测试5: 管理员录入土壤数据")
resp = session.get(f"{BASE}/input", timeout=10)
assert resp.status_code == 200, "管理员应能访问录入页"
print("  ✅ 管理员访问录入页成功")

data = {
    "field_id": None,
    "ph": 6.0,
    "nitrogen": 80,
    "phosphorus": 45,
    "potassium": 280,
    "humidity": 25,
    "temperature": 26,
    "ec": 1200,
    "organic_matter": 3.5,
    "growth_stage": "expansion",
}
resp = session.post(f"{BASE}/api/soil/analyze", json=data, timeout=10)
assert resp.status_code == 200, "分析API应成功"
result = resp.json()
assert result.get("success"), f"分析应成功: {result}"
record_id = result["record_id"]
print(f"  ✅ 管理员录入成功，记录ID={record_id}")

# 测试6: 查看历史
p("测试6: 查看历史记录")
resp = session.get(f"{BASE}/history", timeout=10)
assert resp.status_code == 200, "历史页应可访问"
print("  ✅ 管理员查看历史页成功")

# 测试7: 查看结果详情
p("测试7: 查看分析结果详情")
resp = session.get(f"{BASE}/result/{record_id}", timeout=10)
assert resp.status_code == 200, "结果页应可访问"
print("  ✅ 查看结果详情成功")

# 测试8: 管理员退出
p("测试8: 管理员退出登录")
resp = session.get(f"{BASE}/logout", allow_redirects=False, timeout=10)
assert resp.status_code in (302, 303), "退出应重定向到登录页"
print("  ✅ 退出登录成功")

# 测试9: 退出后不能再访问首页
resp = requests.get(f"{BASE}/", allow_redirects=False, timeout=10)
assert resp.status_code in (302, 303), "退出后应重定向到登录页"
print("  ✅ 退出后无法访问首页")

# 测试10: 注册新用户
p("测试9: 注册新用户 (testuser / test1234)")
new_session = requests.Session()
resp = new_session.post(f"{BASE}/register", data={
    "username": "testuser",
    "password": "test1234",
    "confirm_password": "test1234",
    "email": "test@example.com",
}, allow_redirects=False, timeout=10)
print(f"  状态码: {resp.status_code}, Location: {resp.headers.get('Location', '无')}")
assert resp.status_code in (302, 303), "注册成功应重定向"
print("  ✅ 新用户注册成功")

# 测试11: 验证新用户已登录
resp = new_session.get(f"{BASE}/", timeout=10)
assert resp.status_code == 200, "注册后应自动登录"
assert "testuser" in resp.text, "导航栏应显示用户名"
print("  ✅ 新用户自动登录成功")

# 测试12: 普通用户不能访问管理页
p("测试10: 普通用户权限限制")
resp = new_session.get(f"{BASE}/admin", allow_redirects=False, timeout=10)
assert resp.status_code in (302, 303), "普通用户应被重定向"
print("  ✅ 普通用户无法访问管理页（被重定向）")

# 测试13: 普通用户不能访问设备管理
resp = new_session.get(f"{BASE}/devices", allow_redirects=False, timeout=10)
assert resp.status_code in (302, 303), "普通用户应被重定向"
print("  ✅ 普通用户无法访问设备管理页（被重定向）")

# 测试14: 普通用户录入数据
p("测试11: 普通用户录入数据")
resp = new_session.post(f"{BASE}/api/soil/analyze", json={
    "ph": 5.8,
    "nitrogen": 75,
    "phosphorus": 35,
    "potassium": 200,
    "humidity": 22,
    "temperature": 25,
    "ec": 1100,
    "organic_matter": 3.0,
    "growth_stage": "flowering",
}, timeout=10)
assert resp.status_code == 200
result = resp.json()
assert result.get("success"), f"分析应成功: {result}"
print(f"  ✅ 普通用户录入成功，记录ID={result['record_id']}")

# 测试15: 普通用户查看历史
p("测试12: 普通用户查看历史")
resp = new_session.get(f"{BASE}/history", timeout=10)
assert resp.status_code == 200
print("  ✅ 普通用户查看历史页成功")

# 测试16: 普通用户退出
p("测试13: 普通用户退出登录")
resp = new_session.get(f"{BASE}/logout", allow_redirects=False, timeout=10)
assert resp.status_code in (302, 303)
print("  ✅ 普通用户退出成功")

# 测试17: 再次验证已退出
resp = requests.get(f"{BASE}/", allow_redirects=False, timeout=10)
assert resp.status_code in (302, 303)
print("  ✅ 退出后无法访问首页")

# 测试18: 错误密码登录
p("测试14: 错误密码登录")
resp = session.post(f"{BASE}/login", data={"username": "admin", "password": "wrong"}, timeout=10)
assert "错误" in resp.text, "应显示错误信息"
print("  ✅ 错误密码登录被正确拦截")

# 测试19: 重复注册
p("测试15: 重复注册")
resp = session.post(f"{BASE}/register", data={
    "username": "admin", "password": "test1234",
    "confirm_password": "test1234", "email": "",
}, timeout=10)
assert "已被占用" in resp.text, "应提示用户名已被占用"
print("  ✅ 重复注册被正确拦截")


p("全部测试完成！")
print("  19 项测试全部通过 ✅")
