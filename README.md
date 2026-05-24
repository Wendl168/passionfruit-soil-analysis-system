<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.0%2B-green?style=flat-square&logo=flask" alt="Flask">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite" alt="SQLite">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square" alt="License">
</p>

<br>

<p align="center">
  <img src="assets/logo.png" alt="百香果智能土壤分析系统" width="120px" style="border-radius:20px;">
</p>

<h1 align="center">🥝 百香果智能土壤分析系统</h1>

<p align="center">
  <b>AI 驱动的百香果种植土壤健康诊断与智慧管理平台</b><br>
  专为百香果种植设计的专家级土壤分析引擎 · 多维度健康评分 · 物联网设备接入预留
</p>

<p align="center">
  <a href="#-项目简介">项目简介</a> •
  <a href="#-功能亮点">功能亮点</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-项目截图">项目截图</a> •
  <a href="#-页面路由一览">页面路由</a> •
  <a href="#-api-接口文档">API 文档</a> •
  <a href="#-项目结构">项目结构</a>
</p>

<br>

---

<h2>📌 项目简介</h2>

<b>百香果智能土壤分析系统</b> 是一个端到端的 AI 农业诊断 Web 平台。系统通过分析土壤 pH、氮磷钾含量、湿度、温度、EC 电导率、有机质等 8 项核心指标，结合百香果不同生长阶段（幼苗期→伸蔓期→开花期→坐果期→果实膨大期→采收期）的需肥规律，运用<b>三区间专业评分算法</b>输出完整的农业诊断报告。

从<b>单机演示</b>到<b>多用户系统</b>，从<b>简单打分</b>到<b>专家级诊断</b>，本项目完整展示了 Flask Web 开发 + 规则化 AI 分析引擎 + 数据可视化的全栈工程能力。

> 🎯 **适用场景**：课程设计展示 · GitHub 作品集 · 智慧农业 Demo · 全栈开发练习

<br>

---

<h2>✨ 功能亮点</h2>

<table>
<tr>
  <td width="50%" valign="top">
    <h3>🧠 专家级土壤诊断引擎</h3>
    <ul>
      <li>8 项核心指标三区间评分（最优/可接受/临界）</li>
      <li>综合健康评分 + 风险等级判定</li>
      <li>主要限制因子自动识别</li>
      <li>百香果适配度评估 + 产量风险预测</li>
      <li>Warning Tags 警告标签系统（PH_LOW, K_LOW, EC_HIGH...）</li>
    </ul>
  </td>
  <td width="50%" valign="top">
    <h3>🌱 生长阶段动态模型</h3>
    <ul>
      <li>6 个生长阶段各有独立权重配置</li>
      <li>幼苗期→pH/湿度/温度权重最高</li>
      <li>坐果期→钾/EC/湿度权重最高</li>
      <li>果实膨大期→钾/水分/有机质权重最高</li>
      <li>每个阶段输出专属管理提醒</li>
    </ul>
  </td>
</tr>
<tr>
  <td width="50%" valign="top">
    <h3>📊 多维数据可视化</h3>
    <ul>
      <li>首页 KPI 大屏 + 健康评分环形图</li>
      <li>pH 值趋势折线图 · 综合评分趋势</li>
      <li>NPK 柱状图 · 风险等级分布饼图</li>
      <li>分析结果页六维雷达图</li>
      <li>Chart.js 驱动，纯前端渲染</li>
    </ul>
  </td>
  <td width="50%" valign="top">
    <h3>📡 物联网设备接入预留</h3>
    <ul>
      <li>设备注册 → 数据上传 → AI 分析完整链路</li>
      <li>支持 ESP32 / 蓝牙 / Android App / 模拟器</li>
      <li>上传数据自动触发土壤分析</li>
      <li>异常数据实时预警（中/高风险 + danger 标签）</li>
      <li>设备在线状态 + 地块绑定</li>
    </ul>
  </td>
</tr>
<tr>
  <td width="50%" valign="top">
    <h3>📋 专业分析报告</h3>
    <ul>
      <li>各维度详细诊断文案（含农业专家建议）</li>
      <li>Top 3 最严重问题 + 优先处理建议</li>
      <li>分类建议：施肥 / 灌溉 / 土壤改良 / 阶段提醒</li>
      <li>下一次检测时间建议</li>
      <li>PDF + Excel 一键导出</li>
    </ul>
  </td>
  <td width="50%" valign="top">
    <h3>🔐 多用户权限系统</h3>
    <ul>
      <li>用户注册 / 登录 / Session 会话管理</li>
      <li>密码 bcrypt 哈希存储（werkzeug security）</li>
      <li>Admin / User 双角色权限隔离</li>
      <li>管理员面板：用户管理</li>
      <li>数据按用户隔离，互不可见</li>
    </ul>
  </td>
</tr>
</table>

<br>

---

<h2>🛠 技术栈</h2>

<table>
<tr><th>类别</th><th>技术</th><th>说明</th></tr>
<tr><td><b>后端框架</b></td><td>Python 3.10 · Flask 3.0</td><td>轻量级 Web 框架，RESTful API</td></tr>
<tr><td><b>数据库</b></td><td>SQLite</td><td>零配置嵌入式数据库，自动迁移</td></tr>
<tr><td><b>前端</b></td><td>HTML5 · CSS3 · JavaScript（原生）</td><td>无前端框架依赖，绿色农业主题</td></tr>
<tr><td><b>图表库</b></td><td>Chart.js 4.x（CDN）</td><td>环形图 · 折线图 · 柱状图 · 雷达图 · 饼图</td></tr>
<tr><td><b>AI 引擎</b></td><td>规则化农业专家系统（自研）</td><td>三区间评分 · 阶段权重 · 语义化建议</td></tr>
<tr><td><b>报告导出</b></td><td>ReportLab · OpenPyXL</td><td>PDF 诊断报告 · Excel 数据报表</td></tr>
<tr><td><b>认证</b></td><td>Flask Session · Werkzeug Security</td><td>Session 会话 + 密码哈希</td></tr>
<tr><td><b>部署</b></td><td>Docker · Docker Compose</td><td>容器化一键启动</td></tr>
</table>

<br>

---

<h2>🚀 快速开始</h2>

<h3>📋 环境要求</h3>

<ul>
  <li>Python 3.8+</li>
  <li>pip（Python 包管理器）</li>
  <li>Docker &amp; Docker Compose（可选，容器部署）</li>
</ul>

<br>

<h3>🔧 本地运行</h3>

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/passionfruit-soil-system.git
cd passionfruit-soil-system

# 2. 创建虚拟环境（推荐）
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动服务
python app.py
```

启动后终端会输出：
```
数据库初始化完成
启动服务: http://127.0.0.1:5000
```

<h3>🐳 Docker 运行</h3>

```bash
# 方式一：Docker Compose（推荐）
docker-compose up -d

# 方式二：手动构建
docker build -t passionfruit-soil-system .
docker run -d -p 5000:5000 -v $(pwd)/data:/app/data --name passionfruit-soil passionfruit-soil-system

# 停止
docker-compose down
```

<br>

<h3>🔑 默认账号</h3>

<p>首次启动自动创建以下账号，登录后即可使用全部功能：</p>

<table>
<tr><th>角色</th><th>用户名</th><th>密码</th><th>权限</th></tr>
<tr><td>👑 管理员</td><td><code>admin</code></td><td><code>admin123</code></td><td>查看/管理全部数据和用户</td></tr>
<tr><td>👤 普通用户</td><td colspan="2">在 <code>/register</code> 注册新账号</td><td>仅查看和管理自己的数据</td></tr>
</table>

<br>

<h3>🧪 运行测试</h3>

```bash
# 土壤分析引擎测试（6组测试数据）
python soil_analyzer.py

# 设备上传全流程测试
pip install requests
python test_device_upload.py

# 用户认证全流程测试（19项）
python test_auth_flow.py

# 填充演示数据
python seed_data.py
```

<br>

---

<h2>📸 项目截图</h2>

<blockquote>
  📷 <i>以下为截图占位区域。实际使用时，请用项目运行截图替换这些占位图。</i><br>
  <i>推荐截图工具：Windows 截图工具 / Snipaste / CleanShot</i>
</blockquote>

<br>

<table>
<tr>
  <td align="center" width="50%">
    <h3>🏠 首页数据大屏</h3>
    <img src="assets/screenshots/dashboard.png" alt="首页数据大屏" width="100%" style="border-radius:12px;border:1px solid #e5e7eb;">
    <p><i>KPI 卡片 · pH 趋势 · 评分趋势 · NPK 柱状图 · 风险分布</i></p>
  </td>
  <td align="center" width="50%">
    <h3>📝 土壤数据录入</h3>
    <img src="assets/screenshots/input.png" alt="土壤数据录入" width="100%" style="border-radius:12px;border:1px solid #e5e7eb;">
    <p><i>8 项指标 · 生长阶段选择 · 地块绑定 · 采样时间</i></p>
  </td>
</tr>
<tr>
  <td align="center" width="50%">
    <h3>📊 分析结果页</h3>
    <img src="assets/screenshots/result.png" alt="分析结果页" width="100%" style="border-radius:12px;border:1px solid #e5e7eb;">
    <p><i>综合评分 · 风险等级 · 六维雷达 · 分类建议 · Warning Tags</i></p>
  </td>
  <td align="center" width="50%">
    <h3>📋 历史记录页</h3>
    <img src="assets/screenshots/history.png" alt="历史记录" width="100%" style="border-radius:12px;border:1px solid #e5e7eb;">
    <p><i>筛选功能 · 风险标签 · 记录详情入口</i></p>
  </td>
</tr>
<tr>
  <td align="center" width="50%">
    <h3>🌾 地块管理</h3>
    <img src="assets/screenshots/fields.png" alt="地块管理" width="100%" style="border-radius:12px;border:1px solid #e5e7eb;">
    <p><i>多地块管理 · 检测记录数统计</i></p>
  </td>
  <td align="center" width="50%">
    <h3>🤖 AI 种植助手</h3>
    <img src="assets/screenshots/assistant.png" alt="AI 助手" width="100%" style="border-radius:12px;border:1px solid #e5e7eb;">
    <p><i>百香果种植智能问答 · 参考土壤记录分析</i></p>
  </td>
</tr>
</table>

<br>

---

<h2>📄 页面路由一览</h2>

<table>
<tr><th>页面</th><th>路由</th><th>核心功能</th><th>权限</th></tr>
<tr><td>🏠 数据大屏</td><td><code>/</code></td><td>KPI 指标、趋势图表、风险分布、快捷操作</td><td>已登录用户</td></tr>
<tr><td>📝 数据录入</td><td><code>/input</code></td><td>填写 8 项土壤指标，选择生长阶段，提交 AI 分析</td><td>已登录用户</td></tr>
<tr><td>📊 分析结果</td><td><code>/result/&lt;id&gt;</code></td><td>完整诊断报告：评分、风险、问题、建议、雷达图</td><td>已登录用户</td></tr>
<tr><td>📋 历史记录</td><td><code>/history</code></td><td>检测记录列表，按风险/阶段/地块筛选</td><td>普通用户看自己的 / admin 看全部</td></tr>
<tr><td>🌾 地块管理</td><td><code>/fields</code></td><td>新建/编辑/删除种植地块</td><td>普通用户看自己的 / admin 看全部</td></tr>
<tr><td>📡 设备管理</td><td><code>/devices</code></td><td>传感器设备注册、绑定地块、模拟上传数据</td><td>仅 admin</td></tr>
<tr><td>🤖 AI 助手</td><td><code>/assistant</code></td><td>百香果种植智能问答</td><td>已登录用户</td></tr>
<tr><td>👑 管理面板</td><td><code>/admin</code></td><td>查看所有注册用户</td><td>仅 admin</td></tr>
<tr><td>🔑 登录</td><td><code>/login</code></td><td>用户名密码登录</td><td>未登录</td></tr>
<tr><td>📝 注册</td><td><code>/register</code></td><td>注册新账号</td><td>未登录</td></tr>
</table>

<br>

---

<h2>📡 API 接口文档</h2>

<h3>认证</h3>

<table>
<tr><th>方法</th><th>路由</th><th>说明</th></tr>
<tr><td><code>POST</code></td><td><code>/login</code></td><td>用户登录（form 表单提交）</td></tr>
<tr><td><code>POST</code></td><td><code>/register</code></td><td>用户注册（form 表单提交）</td></tr>
<tr><td><code>GET</code></td><td><code>/logout</code></td><td>退出登录</td></tr>
</table>

<h3>土壤分析</h3>

<table>
<tr><th>方法</th><th>路由</th><th>说明</th></tr>
<tr><td><code>POST</code></td><td><code>/api/soil/analyze</code></td><td>提交土壤数据 → AI 分析 → 保存记录</td></tr>
<tr><td><code>GET</code></td><td><code>/api/soil/history</code></td><td>历史检测记录列表</td></tr>
<tr><td><code>GET</code></td><td><code>/api/soil/result/&lt;id&gt;</code></td><td>单条分析结果详情</td></tr>
<tr><td><code>GET</code></td><td><code>/api/soil/trends</code></td><td>趋势数据（pH / 评分历史）</td></tr>
</table>

<h3>仪表盘（首页大屏）</h3>

<table>
<tr><th>方法</th><th>路由</th><th>说明</th></tr>
<tr><td><code>GET</code></td><td><code>/api/dashboard/summary</code></td><td>综合概览数据</td></tr>
<tr><td><code>GET</code></td><td><code>/api/dashboard/latest</code></td><td>最近一次检测完整数据</td></tr>
<tr><td><code>GET</code></td><td><code>/api/dashboard/risk-stats</code></td><td>风险等级分布统计</td></tr>
</table>

<h3>传感器设备接入</h3>

<table>
<tr><th>方法</th><th>路由</th><th>说明</th></tr>
<tr><td><code>POST</code></td><td><code>/api/device/register</code></td><td>注册新设备</td></tr>
<tr><td><code>GET</code></td><td><code>/api/device/list</code></td><td>获取所有设备列表</td></tr>
<tr><td><code>POST</code></td><td><code>/api/device/upload</code></td><td>设备上传传感器数据（支持自动 AI 分析）</td></tr>
<tr><td><code>GET</code></td><td><code>/api/device/latest</code></td><td>查询设备最新读数</td></tr>
<tr><td><code>GET</code></td><td><code>/api/device/readings</code></td><td>查询设备历史读数列表</td></tr>
<tr><td><code>PUT</code></td><td><code>/api/device/&lt;id&gt;/bind</code></td><td>设备绑定/解绑地块</td></tr>
<tr><td><code>DELETE</code></td><td><code>/api/device/&lt;id&gt;</code></td><td>删除设备</td></tr>
</table>

<h3>地块管理</h3>

<table>
<tr><th>方法</th><th>路由</th><th>说明</th></tr>
<tr><td><code>GET</code></td><td><code>/api/fields</code></td><td>获取地块列表</td></tr>
<tr><td><code>POST</code></td><td><code>/api/fields</code></td><td>创建新地块</td></tr>
<tr><td><code>PUT</code></td><td><code>/api/fields/&lt;id&gt;</code></td><td>更新地块信息</td></tr>
<tr><td><code>DELETE</code></td><td><code>/api/fields/&lt;id&gt;</code></td><td>删除地块</td></tr>
</table>

<h3>报告导出</h3>

<table>
<tr><th>方法</th><th>路由</th><th>说明</th></tr>
<tr><td><code>GET</code></td><td><code>/api/export/pdf/&lt;id&gt;</code></td><td>导出单条记录 PDF 诊断报告</td></tr>
<tr><td><code>GET</code></td><td><code>/api/export/excel/&lt;id&gt;</code></td><td>导出单条记录 Excel 数据报表</td></tr>
<tr><td><code>GET</code></td><td><code>/api/export/history/excel</code></td><td>导出全部历史记录 Excel</td></tr>
</table>

<h3>设备上传示例（curl）</h3>

```bash
curl -X POST http://localhost:5000/api/device/upload \
  -H "Content-Type: application/json" \
  -d '{
    "device_code": "ESP32-001",
    "ph": 6.0,
    "nitrogen": 80,
    "phosphorus": 45,
    "potassium": 280,
    "humidity": 25,
    "temperature": 26,
    "ec": 1200,
    "organic_matter": 3.5,
    "growth_stage": "expansion",
    "auto_analyze": true
  }'
```

<br>

---

<h2>🗂 项目结构</h2>

<pre>
passionfruit_soil_system/
│
├── <b>app.py</b>                  # Flask 主应用·路由·API·认证
├── <b>database.py</b>             # SQLite 数据库模块·自动迁移
├── <b>soil_analyzer.py</b>        # ★ 核心：百香果土壤分析引擎
├── <b>assistant.py</b>            # AI 种植助手（规则问答）
├── <b>requirements.txt</b>        # Python 依赖包列表
├── <b>Dockerfile</b>              # 容器构建
├── <b>docker-compose.yml</b>      # 容器编排
├── <b>.env.example</b>            # 环境变量模板
├── <b>.gitignore</b>              # Git 忽略规则
├── <b>seed_data.py</b>            # 演示数据填充脚本
│
├── <b>data/</b>                   # SQLite 数据库（自动创建，不提交 Git）
│
├── <b>static/</b>
│   ├── css/<b>style.css</b>       # 全局样式（农业绿色主题）
│   └── js/<b>main.js</b>          # 全局脚本（页面交互 + 图表渲染）
│
├── <b>templates/</b>              # Jinja2 模板（11 个页面）
│   ├── <b>base.html</b>           # 基础骨架（导航栏 + 认证状态）
│   ├── <b>index.html</b>          # 数据大屏
│   ├── <b>input.html</b>          # 数据录入
│   ├── <b>result.html</b>         # 分析结果
│   ├── <b>history.html</b>        # 历史记录
│   ├── <b>fields.html</b>         # 地块管理
│   ├── <b>devices.html</b>        # 设备管理（admin only）
│   ├── <b>assistant.html</b>      # AI 助手
│   ├── <b>admin.html</b>          # 管理员面板
│   ├── <b>login.html</b>          # 登录页
│   └── <b>register.html</b>       # 注册页
│
├── <b>reports/</b>                # 报告导出模块
│   ├── <b>__init__.py</b>
│   ├── <b>pdf_generator.py</b>    # PDF 报告（ReportLab）
│   └── <b>excel_generator.py</b>  # Excel 报表（OpenPyXL）
│
└── <b>test_*.py</b>               # 自动化测试脚本（5 个）
</pre>

<br>

---

<h2>🗄 数据库设计</h2>

<p>系统使用 <b>SQLite</b>，零配置嵌入式数据库，文件存储在 <code>data/soil.db</code>（首次启动自动创建，已加入 <code>.gitignore</code>）。</p>

<table>
<tr><th>表名</th><th>说明</th><th>核心字段</th></tr>
<tr><td><code>users</code></td><td>用户</td><td>id, username, password_hash, email, role, created_at</td></tr>
<tr><td><code>fields</code></td><td>地块</td><td>id, field_name, location, area, soil_type, user_id</td></tr>
<tr><td><code>soil_records</code></td><td>土壤检测记录</td><td>id, field_id, user_id, ph, nitrogen, ..., growth_stage</td></tr>
<tr><td><code>analysis_results</code></td><td>分析结果</td><td>id, soil_record_id, user_id, health_score, risk_level, summary, detail_json</td></tr>
<tr><td><code>devices</code></td><td>传感器设备</td><td>id, device_name, device_code, device_type, field_id, user_id, status</td></tr>
<tr><td><code>sensor_readings</code></td><td>传感器读数</td><td>id, device_id, field_id, ph, nitrogen, ..., created_at</td></tr>
</table>

<blockquote>
  <b>兼容性：</b>系统启动时自动执行数据库迁移，为旧表添加 <code>user_id</code> 和 <code>field_id</code> 字段。<br>
  旧数据字段值为 NULL，管理员登录后可查看全部历史数据。
</blockquote>

<br>

---

<h2>❓ 常见问题</h2>

<details>
<summary><b>启动报错 "ModuleNotFoundError: No module named 'reportlab'"</b></summary>

```bash
pip install reportlab openpyxl
```

</details>

<details>
<summary><b>忘记管理员密码怎么办？</b></summary>

删除 <code>data/soil.db</code> 文件，重新启动服务即可重置（会自动创建默认管理员 <code>admin / admin123</code>）。

</details>

<details>
<summary><b>生产环境部署需要注意什么？</b></summary>

<ol>
  <li>修改 <code>FLASK_SECRET_KEY</code> 为随机字符串（可通过 <code>python -c "import secrets; print(secrets.token_hex(32))"</code> 生成）</li>
  <li>设置 <code>FLASK_DEBUG=0</code></li>
  <li>建议使用 Gunicorn + Nginx 反向代理</li>
  <li>做好数据库定期备份</li>
</ol>

</details>

<details>
<summary><b>如何导入旧数据？</b></summary>

系统启动时自动执行数据库迁移。旧数据中的 <code>user_id</code> 字段会设为 NULL，管理员可在登录后查看全部数据。

</details>

<br>

---

<h2>📌 后续规划</h2>

<table>
<tr><th>类别</th><th>规划内容</th><th>状态</th></tr>
<tr><td>🔔 通知</td><td>短信/邮件预警通知</td><td>⏳ Planned</td></tr>
<tr><td>📱 移动端</td><td>Android App + iOS App</td><td>⏳ Planned</td></tr>
<tr><td>🔌 硬件</td><td>ESP32 真实传感器接入</td><td>⏳ Planned</td></tr>
<tr><td>📶 蓝牙</td><td>蓝牙传感器实时数据采集</td><td>⏳ Planned</td></tr>
<tr><td>🌐 多语言</td><td>中英文双语界面</td><td>⏳ Planned</td></tr>
<tr><td>📤 导出</td><td>数据导出为 CSV</td><td>⏳ Planned</td></tr>
<tr><td>📥 导入</td><td>批量导入历史数据</td><td>⏳ Planned</td></tr>
<tr><td>👤 用户</td><td>个人中心（修改密码/资料）</td><td>⏳ Planned</td></tr>
<tr><td>📒 日志</td><td>种植日志记录</td><td>⏳ Planned</td></tr>
<tr><td>☁️ 天气</td><td>气象数据集成</td><td>⏳ Planned</td></tr>
</table>

<br>

---

<h2>📄 License</h2>

<p>MIT License © 2024</p>

<br>

---

<p align="center">
  <b>🥝 百香果智能土壤分析系统</b><br>
  <i>AI 驱动的智慧农业 · 从土壤到果实，科学种植每一步</i>
</p>

<p align="center">
  <a href="#">⬆ 返回顶部</a>
</p>
