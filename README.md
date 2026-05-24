# 🥝 百香果智能土壤分析系统

> AI 驱动的百香果种植土壤健康诊断与智慧管理平台

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📋 目录

- [项目介绍](#-项目介绍)
- [功能总览](#-功能总览)
- [技术栈](#-技术栈)
- [项目结构](#-项目结构)
- [快速开始](#-快速开始)
  - [环境要求](#环境要求)
  - [本地运行](#本地运行)
  - [Docker 运行](#docker-运行)
- [页面说明](#-页面说明)
- [用户权限](#-用户权限)
- [API 接口](#-api-接口)
- [传感器设备接入](#-传感器设备接入)
- [数据库说明](#-数据库说明)
- [测试数据](#-测试数据)
- [常见问题](#-常见问题)
- [后续规划](#-后续规划)

---

## 🌟 项目介绍

「百香果智能土壤分析系统」是一个专为百香果种植设计的 **AI 土壤健康诊断平台**。系统通过分析土壤 pH、氮磷钾、湿度、温度、EC 电导率、有机质等关键指标，结合百香果不同生长阶段的需肥规律，输出专业的农业诊断报告，帮助种植者科学管理土壤。

### 核心价值

- **🧠 专家级诊断** — 基于农业研究数据的专业评分算法，非简单打分
- **🌱 生长阶段适配** — 针对幼苗期、伸蔓期、开花期等 6 个阶段动态调整分析权重
- **📊 多维可视化** — 雷达图、趋势图、NPK 柱状图、风险分布图
- **📱 全平台接入** — 支持 Web 手动录入 + 传感器设备自动上传（预留接口）
- **🔐 多用户支持** — 管理员与普通用户权限隔离，数据安全

---

## 🎯 功能总览

### 🔬 土壤分析
- ✅ 8 项核心指标分析（pH、氮、磷、钾、湿度、温度、EC、有机质）
- ✅ 三区间评分算法（最优/可接受/临界）
- ✅ 综合健康评分（0-100）
- ✅ 风险等级判定（低/中/高风险）
- ✅ 主要限制因子识别
- ✅ 百香果适配度评估
- ✅ 产量风险预测

### 🌿 生长阶段管理
- ✅ 6 个生长阶段专属分析模型
- ✅ 动态权重分配
- ✅ 阶段管理提醒

### 📋 分析报告
- ✅ 各维度详细分析文案
- ✅ Top 3 最严重问题
- ✅ Warning Tags 警告标签
- ✅ 施肥/灌溉/土壤改良建议
- ✅ 下一次检测建议
- ✅ PDF / Excel 报告导出

### 📡 数据管理
- ✅ 手动录入土壤检测数据
- ✅ 地块管理（多个种植地块）
- ✅ 历史记录查询与筛选
- ✅ 趋势图表（pH、评分）
- ✅ 传感器设备注册与数据上传（预留接口）
- ✅ 设备自动上传触发 AI 分析

### 👥 用户系统
- ✅ 用户注册 / 登录 / 退出
- ✅ Session 会话管理
- ✅ 密码哈希存储
- ✅ 管理员 / 普通用户权限隔离
- ✅ 管理员面板（用户管理）

---

## 🛠 技术栈

| 层 | 技术 | 说明 |
|------|------|------|
| **后端** | Python 3.8+ / Flask | Web 框架 |
| **数据库** | SQLite | 轻量级嵌入式数据库 |
| **前端** | HTML5 / CSS3 / JavaScript | 原生，无框架依赖 |
| **图表** | Chart.js 4.x | CDN 加载 |
| **PDF** | ReportLab | 报告导出 |
| **Excel** | OpenPyXL | 报表导出 |
| **认证** | Flask Session + Werkzeug | Session + 密码哈希 |
| **部署** | Docker / docker-compose | 容器化部署 |

---

## 📁 项目结构

```
passionfruit_soil_system/
├── app.py                    # Flask 主应用（路由 + API + 认证）
├── database.py               # SQLite 数据库模块
├── soil_analyzer.py          # 百香果土壤分析引擎（核心）
├── assistant.py              # AI 种植助手
├── requirements.txt          # Python 依赖
├── Dockerfile                # 容器构建文件
├── docker-compose.yml        # 容器编排文件
├── .env.example              # 环境变量示例
├── .gitignore                # Git 忽略规则
│
├── data/                     # SQLite 数据库目录（自动创建）
│   └── soil.db               # 数据库文件（不提交到 Git）
│
├── static/
│   ├── css/
│   │   └── style.css         # 全局样式
│   └── js/
│       ├── main.js           # 全局脚本（页面交互、图表）
│       └── input.js          # 录入页专用脚本
│
├── templates/
│   ├── base.html             # 基础模板（导航栏 + 登录状态）
│   ├── index.html            # 首页数据大屏
│   ├── input.html            # 土壤数据录入
│   ├── result.html           # 分析结果详情
│   ├── history.html          # 历史记录
│   ├── fields.html           # 地块管理
│   ├── devices.html          # 设备管理（仅 admin）
│   ├── assistant.html        # AI 种植助手
│   ├── admin.html            # 管理员面板
│   ├── login.html            # 登录页
│   └── register.html         # 注册页
│
├── reports/
│   ├── __init__.py
│   ├── pdf_generator.py      # PDF 报告生成
│   └── excel_generator.py    # Excel 报表生成
│
├── test_analyzer.py          # 分析引擎测试脚本
├── test_device_upload.py     # 设备上传测试脚本
├── test_auth_flow.py         # 用户认证全流程测试
├── test_field.py             # 地块测试
├── test_assistant.py         # AI 助手测试
└── seed_data.py              # 测试数据填充脚本
```

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- pip（Python 包管理器）
- Docker & Docker Compose（可选，用于容器部署）

### 本地运行

#### 1. 克隆项目

```bash
git clone https://github.com/your-username/passionfruit-soil-system.git
cd passionfruit-soil-system
```

#### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

#### 3. 安装依赖

```bash
pip install -r requirements.txt
```

#### 4. 启动服务

```bash
python app.py
```

#### 5. 打开浏览器

访问 **http://localhost:5000**，使用以下账号登录：

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | `admin` | `admin123` |
| 普通用户 | 注册新账号 | — |

> 首次启动会自动创建数据库和默认管理员账号。

---

### 🐳 Docker 运行

#### 方式一：Docker Compose（推荐）

```bash
docker-compose up -d
```

#### 方式二：手动构建

```bash
# 构建镜像
docker build -t passionfruit-soil-system .

# 运行容器
docker run -d -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  -e FLASK_SECRET_KEY=your-secret-key \
  --name passionfruit-soil \
  passionfruit-soil-system
```

然后访问 **http://localhost:5000**

#### 停止容器

```bash
docker-compose down
# 或
docker stop passionfruit-soil
```

---

## 📄 页面说明

| 页面 | 路由 | 说明 | 权限 |
|------|------|------|------|
| **数据大屏** | `/` | 健康评分、KPI 卡片、趋势图、风险分布 | 所有已登录用户 |
| **数据录入** | `/input` | 填写土壤指标、选择生长阶段、提交 AI 分析 | 所有已登录用户 |
| **分析结果** | `/result/<id>` | 完整诊断报告（评分/风险/问题/建议） | 所有已登录用户 |
| **历史记录** | `/history` | 检测记录列表，支持筛选 | 普通用户看自己的，admin 看全部 |
| **地块管理** | `/fields` | 管理种植地块 | 普通用户看自己的，admin 看全部 |
| **设备管理** | `/devices` | 注册/管理传感器设备，模拟上传 | 仅 admin |
| **AI 助手** | `/assistant` | 百香果种植智能问答 | 所有已登录用户 |
| **管理员** | `/admin` | 查看所有用户 | 仅 admin |
| **登录** | `/login` | 用户登录 | 未登录 |
| **注册** | `/register` | 注册新账号 | 未登录 |

---

## 🔐 用户权限

| 功能 | 未登录 | user（普通用户） | admin（管理员） |
|------|--------|-----------------|----------------|
| 系统核心页面 | ❌ 重定向到登录 | ✅ | ✅ |
| 地块管理 | ❌ | ✅ 仅自己的 | ✅ 全部 |
| 历史记录 | ❌ | ✅ 仅自己的 | ✅ 全部 |
| 设备管理 | ❌ | ❌ | ✅ |
| 管理员面板 | ❌ | ❌ | ✅ |
| AI 助手 | ❌ | ✅ | ✅ |
| 数据录入 | ❌ | ✅ | ✅ |

---

## 📡 API 接口

### 认证相关

| 方法 | 路由 | 说明 |
|------|------|------|
| POST | `/login` | 用户登录 |
| POST | `/register` | 用户注册 |
| GET | `/logout` | 退出登录 |

### 土壤分析

| 方法 | 路由 | 说明 |
|------|------|------|
| POST | `/api/soil/analyze` | 提交土壤数据并执行 AI 分析 |
| GET | `/api/soil/history` | 获取历史检测记录列表 |
| GET | `/api/soil/result/<id>` | 获取单条分析结果详情 |
| GET | `/api/soil/trends` | 获取趋势数据（用于图表） |

### 仪表盘

| 方法 | 路由 | 说明 |
|------|------|------|
| GET | `/api/dashboard/summary` | 综合概览数据 |
| GET | `/api/dashboard/latest` | 最近一次检测数据 |
| GET | `/api/dashboard/risk-stats` | 风险等级分布统计 |

### 设备管理（传感器接入）

| 方法 | 路由 | 说明 |
|------|------|------|
| POST | `/api/device/register` | 注册新设备 |
| GET | `/api/device/list` | 获取所有设备列表 |
| POST | `/api/device/upload` | 设备上传传感器数据（支持自动分析） |
| GET | `/api/device/latest` | 查询设备最新读数 |
| GET | `/api/device/readings` | 查询设备历史读数 |

### 地块管理

| 方法 | 路由 | 说明 |
|------|------|------|
| GET | `/api/fields` | 获取地块列表 |
| POST | `/api/fields` | 创建新地块 |
| PUT | `/api/fields/<id>` | 更新地块信息 |
| DELETE | `/api/fields/<id>` | 删除地块 |

### 报告导出

| 方法 | 路由 | 说明 |
|------|------|------|
| GET | `/api/export/pdf/<id>` | 导出单条记录 PDF 报告 |
| GET | `/api/export/excel/<id>` | 导出单条记录 Excel 报告 |
| GET | `/api/export/history/excel` | 导出全部历史记录 Excel |

**设备上传数据示例：**

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

---

## 📡 传感器设备接入

系统预留了完整的传感器数据接入能力：

- **设备注册** — 支持 ESP32、蓝牙设备、Android App、模拟器等多种设备类型
- **自动分析** — 设备上传数据可选择自动触发 AI 土壤分析
- **数据预警** — 检测到中/高风险数据时自动生成预警
- **在线状态** — 设备在线/离线状态实时显示
- **设备管理** — 设备绑定地块、查看历史上传记录

> 📌 第一阶段无需真实硬件，可以通过 `/devices` 页面的模拟上传功能测试。

---

## 🗄 数据库说明

系统使用 **SQLite** 作为数据库，文件存储在 `data/soil.db`（首次启动自动创建）。

### 表结构

| 表名 | 说明 | 关键字段 |
|------|------|---------|
| `users` | 用户 | id, username, password_hash, email, role |
| `fields` | 地块 | id, field_name, location, area, soil_type, user_id |
| `soil_records` | 土壤检测记录 | id, field_id, user_id, ph, nitrogen, ..., growth_stage |
| `analysis_results` | 分析结果 | id, soil_record_id, user_id, health_score, risk_level, summary, detail_json |
| `devices` | 传感器设备 | id, device_name, device_code, device_type, field_id, user_id, status |
| `sensor_readings` | 传感器读数 | id, device_id, field_id, ph, nitrogen, ..., created_at |

### 数据库迁移

系统启动时会自动检查并执行以下迁移：
- 为旧表添加 `user_id` 字段（兼容旧数据）
- 为旧表添加 `field_id` 字段（兼容旧数据）
- 创建默认管理员账号（`admin / admin123`）

---

## 🧪 测试数据

```bash
# 运行土壤分析引擎测试（6组测试数据）
python soil_analyzer.py

# 运行设备上传测试
pip install requests
python test_device_upload.py

# 运行用户认证全流程测试
python test_auth_flow.py

# 填充演示数据（可选）
python seed_data.py
```

---

## ❓ 常见问题

### Q: 启动报错 "ModuleNotFoundError: No module named 'reportlab'"

```bash
pip install reportlab openpyxl
```

### Q: 忘记管理员密码怎么办？

删除 `data/soil.db` 文件，重新启动服务即可重置（会自动创建默认管理员 `admin / admin123`）。

### Q: 如何导入旧数据？

系统启动时自动执行数据库迁移，旧数据中的 `user_id` 字段会设为 `NULL`（兼容处理）。管理员可以在登录后查看所有数据。

### Q: 生产环境部署需要注意什么？

1. 修改 `.env` 中的 `FLASK_SECRET_KEY` 为随机字符串
2. 设置 `FLASK_DEBUG=0`
3. 建议使用 Gunicorn 或 uWSGI 替代 Flask 开发服务器
4. 配置 Nginx 反向代理

### Q: 如何修改默认的管理员密码？

登录 admin 账号后，暂时不支持在线修改密码。可以通过直接在数据库中更新（需要 SQLite 工具）或删除 `soil.db` 重新创建。

---

## 📌 后续规划

- [ ] 短信/邮件预警通知
- [ ] 移动端 App（Android / iOS）
- [ ] ESP32 真实硬件接入
- [ ] 蓝牙传感器实时数据采集
- [ ] 多语言支持
- [ ] 数据导出为 CSV
- [ ] 批量导入历史数据
- [ ] 用户个人中心（修改密码/资料）
- [ ] 种植日志记录
- [ ] 气象数据集成

---

## 📄 License

MIT License © 2024

---

<p align="center">
  Made with 🥝 for Passion Fruit Growers
</p>
