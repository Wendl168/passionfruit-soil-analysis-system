/**
 * main.js - 百香果智能土壤分析系统 全局脚本
 * ==========================================
 * 职责：页面交互、表单处理、API 调用、图表渲染、工具函数
 */

(function() {
    'use strict';

    // ================================================================
    // 工具函数
    // ================================================================

    function showLoading(message) {
        message = message || 'AI 正在分析土壤数据...';
        hideLoading();
        var overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = 'loadingOverlay';
        overlay.innerHTML =
            '<div class="loading-spinner"></div>' +
            '<p class="loading-text">' + message + '</p>';
        document.body.appendChild(overlay);
    }

    function hideLoading() {
        var overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.remove();
    }

    function showMessage(message, type) {
        type = type || 'info';
        var msgEl = document.createElement('div');
        msgEl.style.cssText =
            'position:fixed;top:80px;right:20px;padding:1rem 1.5rem;border-radius:8px;' +
            'font-size:0.9375rem;font-weight:500;z-index:1001;animation:slideIn 0.3s ease;' +
            'max-width:400px;word-wrap:break-word;';
        if (type === 'success') {
            msgEl.style.background = '#d1fae5'; msgEl.style.color = '#065f46'; msgEl.style.border = '1px solid #a7f3d0';
        } else if (type === 'error') {
            msgEl.style.background = '#fee2e2'; msgEl.style.color = '#991b1b'; msgEl.style.border = '1px solid #fecaca';
        } else {
            msgEl.style.background = '#dbeafe'; msgEl.style.color = '#1e40af'; msgEl.style.border = '1px solid #bfdbfe';
        }
        msgEl.textContent = message;
        document.body.appendChild(msgEl);
        setTimeout(function() {
            msgEl.style.animation = 'slideOut 0.3s ease';
            setTimeout(function() { msgEl.remove(); }, 300);
        }, 3000);
    }

    function addAnimationStyles() {
        if (document.getElementById('animationStyles')) return;
        var style = document.createElement('style');
        style.id = 'animationStyles';
        style.textContent =
            '@keyframes slideIn{from{transform:translateX(100%);opacity:0}to{transform:translateX(0);opacity:1}}' +
            '@keyframes slideOut{from{transform:translateX(0);opacity:1}to{transform:translateX(100%);opacity:0}}';
        document.head.appendChild(style);
    }

    function formatDate(dateStr) {
        if (!dateStr) return '-';
        var date = new Date(dateStr);
        if (isNaN(date.getTime())) return dateStr;
        return date.toLocaleString('zh-CN', {
            year: 'numeric', month: '2-digit', day: '2-digit',
            hour: '2-digit', minute: '2-digit'
        });
    }

    function getScoreBadgeClass(score) {
        if (score >= 80) return 'badge-score-high';
        if (score >= 60) return 'badge-score-medium';
        return 'badge-score-low';
    }

    function getRiskBadgeClass(risk) {
        if (risk === '低风险') return 'badge-risk-low';
        if (risk === '中风险') return 'badge-risk-medium';
        return 'badge-risk-high';
    }

    var STAGE_NAMES = {
        seedling: '幼苗期', vine: '伸蔓期', flowering: '开花期',
        fruiting: '坐果期', expansion: '果实膨大期', harvest: '采收期'
    };

    // ================================================================
    // 图表工具
    // ================================================================

    /** 获取评分对应的颜色 */
    function scoreColor(score) {
        if (score >= 80) return '#22c55e';
        if (score >= 60) return '#f59e0b';
        return '#ef4444';
    }

    /** Chart.js 全局默认 */
    function setChartDefaults() {
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js 未加载，图表功能不可用');
            return false;
        }
        Chart.defaults.font.family = "'Inter','PingFang SC','Microsoft YaHei',sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = '#6b7280';
        Chart.defaults.plugins.legend.labels.usePointStyle = true;
        Chart.defaults.plugins.legend.labels.padding = 16;
        return true;
    }
    
    /** 检查 Chart.js 是否可用 */
    function isChartAvailable() {
        return typeof Chart !== 'undefined';
    }

    // ================================================================
    // 首页功能
    // ================================================================

    function initDashboard() {
        var dashboard = document.querySelector('.dashboard-container') || document.querySelector('.dashboard-grid');
        if (!dashboard) return;
        setChartDefaults();
        loadDashboardSummary();
        loadDashboardLatest();
        loadTrends();
        loadRiskStats();
    }

    /** 带超时的 fetch 请求 */
    function fetchWithTimeout(url, options, timeout) {
        timeout = timeout || 10000;
        options = options || {};
        var controller = new AbortController();
        var timeoutId = setTimeout(function() { controller.abort(); }, timeout);
        options.signal = controller.signal;
        return fetch(url, options).finally(function() {
            clearTimeout(timeoutId);
        });
    }

    /** 加载综合概览数据 → KPI 卡片 */
    function loadDashboardSummary() {
        fetchWithTimeout('/api/dashboard/summary', {}, 8000)
            .then(function(r) {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            })
            .then(function(res) {
                if (res.success && res.data) {
                    var d = res.data;
                    setText('kpiScore', d.avg_health_score ? Math.round(d.avg_health_score) + '分' : '暂无');
                    setText('kpiRisk', d.latest_risk_level || '暂无');
                    setText('kpiFields', d.total_fields || 0);
                    setText('kpiRecords', d.total_records || 0);
                    // 时间格式化
                    var timeEl = document.getElementById('kpiTime');
                    if (timeEl) {
                        timeEl.textContent = d.latest_record_time
                            ? formatTime(d.latest_record_time)
                            : '暂无';
                    }
                }
            })
            .catch(function(e) {
                console.warn('加载概览数据失败:', e.message || e);
            });
    }

    /** 加载最近一次检测数据 → 8 项指标 */
    function loadDashboardLatest() {
        fetchWithTimeout('/api/dashboard/latest', {}, 8000)
            .then(function(r) {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            })
            .then(function(res) {
                if (res.success && res.data) {
                    var d = res.data;
                    var grid = document.getElementById('metricsGrid');
                    if (grid) {
                        grid.innerHTML =
                            '<div class="metric-item"><div class="metric-label">pH</div><div class="metric-value">' + fmt(d.ph) + '</div></div>' +
                            '<div class="metric-item"><div class="metric-label">氮 N</div><div class="metric-value">' + fmt(d.nitrogen) + ' <span class="metric-unit">mg/kg</span></div></div>' +
                            '<div class="metric-item"><div class="metric-label">磷 P</div><div class="metric-value">' + fmt(d.phosphorus) + ' <span class="metric-unit">mg/kg</span></div></div>' +
                            '<div class="metric-item"><div class="metric-label">钾 K</div><div class="metric-value">' + fmt(d.potassium) + ' <span class="metric-unit">mg/kg</span></div></div>' +
                            '<div class="metric-item"><div class="metric-label">湿度</div><div class="metric-value">' + fmt(d.humidity) + ' <span class="metric-unit">%</span></div></div>' +
                            '<div class="metric-item"><div class="metric-label">温度</div><div class="metric-value">' + fmt(d.temperature) + ' <span class="metric-unit">°C</span></div></div>' +
                            '<div class="metric-item"><div class="metric-label">EC</div><div class="metric-value">' + fmt(d.ec) + ' <span class="metric-unit">μS/cm</span></div></div>' +
                            '<div class="metric-item"><div class="metric-label">有机质</div><div class="metric-value">' + fmt(d.organic_matter) + ' <span class="metric-unit">%</span></div></div>';
                    }
                    // NPK 柱状图
                    renderNPKBar(d.nitrogen, d.phosphorus, d.potassium);
                }
            })
            .catch(function(e) {
                console.warn('加载最近检测数据失败:', e.message || e);
            });
    }

    /** 加载趋势数据 → pH 折线图 + 评分趋势图 */
    function loadTrends() {
        fetchWithTimeout('/api/soil/trends?limit=20', {}, 8000)
            .then(function(r) {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            })
            .then(function(res) {
                if (res.success && res.data && res.data.labels && res.data.labels.length > 0) {
                    renderPHTrend(res.data);
                    renderScoreTrend(res.data);
                } else {
                    showEmptyChart('phTrendChart', '暂无趋势数据，请先录入土壤检测记录');
                    showEmptyChart('scoreTrendChart', '暂无评分数据');
                }
            })
            .catch(function(e) {
                console.warn('加载趋势数据失败:', e.message || e);
                showEmptyChart('phTrendChart', '加载失败，请刷新重试');
                showEmptyChart('scoreTrendChart', '加载失败，请刷新重试');
            });
    }

    /** 加载风险等级分布 → 饼图 */
    function loadRiskStats() {
        fetchWithTimeout('/api/dashboard/risk-stats', {}, 8000)
            .then(function(r) {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            })
            .then(function(res) {
                if (res.success && res.data) {
                    renderRiskPie(res.data);
                }
            })
            .catch(function(e) {
                console.warn('加载风险统计失败:', e.message || e);
                showEmptyChart('riskPieChart', '加载失败，请刷新重试');
            });
    }

    /* ── 工具函数 ── */
    function setText(id, val) {
        var el = document.getElementById(id);
        if (el) el.textContent = val;
    }
    function fmt(v) {
        return (v != null && v !== '') ? v : '-';
    }
    function formatTime(ts) {
        if (!ts) return '暂无';
        try {
            var d = new Date(ts);
            var m = (d.getMonth() + 1);
            var day = d.getDate();
            var h = String(d.getHours()).padStart(2, '0');
            var min = String(d.getMinutes()).padStart(2, '0');
            return m + '/' + day + ' ' + h + ':' + min;
        } catch (e) {
            return ts.slice(0, 16);
        }
    }

    /* ── 兼容旧版调用 ── */
    function loadDashboardStats() { loadDashboardSummary(); }
    function updateDashboardUI() {}
    function updateRecentMetrics() {}

    /** 显示空图表提示 */
    function showEmptyChart(canvasId, message) {
        var canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        // 获取 canvas 的父容器
        var container = canvas.parentElement;
        if (!container) return;
        
        // 设置容器样式以便显示空状态
        container.style.position = 'relative';
        container.style.minHeight = '200px';
        
        // 创建空状态提示元素
        var emptyDiv = document.createElement('div');
        emptyDiv.className = 'chart-empty-state';
        emptyDiv.innerHTML = 
            '<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;color:#9ca3af;">' +
            '<div style="font-size:3rem;margin-bottom:0.5rem;">📊</div>' +
            '<div style="font-size:0.9375rem;font-weight:500;">' + message + '</div>' +
            '</div>';
        
        // 隐藏 canvas，显示空状态
        canvas.style.display = 'none';
        container.appendChild(emptyDiv);
    }
    
    /** 清除空图表提示 */
    function clearEmptyChart(canvasId) {
        var canvas = document.getElementById(canvasId);
        if (!canvas) return;
        
        canvas.style.display = 'block';
        
        var container = canvas.parentElement;
        if (container) {
            var emptyState = container.querySelector('.chart-empty-state');
            if (emptyState) emptyState.remove();
        }
    }

    /** 渲染 pH 趋势折线图 */
    function renderPHTrend(trend) {
        var canvas = document.getElementById('phTrendChart');
        if (!canvas) return;
        
        if (!isChartAvailable()) {
            showEmptyChart('phTrendChart', '图表库加载中...');
            return;
        }
        
        if (!trend || !trend.labels || trend.labels.length === 0) {
            showEmptyChart('phTrendChart', '暂无趋势数据，请先录入土壤检测记录');
            return;
        }
        
        clearEmptyChart('phTrendChart');

        var phData = trend.ph.map(function(v) { return v !== null ? v : null; });

        new Chart(canvas, {
            type: 'line',
            data: {
                labels: trend.labels,
                datasets: [{
                    label: 'pH',
                    data: phData,
                    borderColor: '#22c55e',
                    backgroundColor: 'rgba(34,197,94,0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#22c55e',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    spanGaps: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 4, max: 9,
                        grid: { color: 'rgba(0,0,0,0.05)' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { maxRotation: 45, maxTicksLimit: 10 }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        cornerRadius: 8,
                        padding: 10
                    }
                }
            }
        });
    }

    /** 渲染 NPK 柱状图 */
    function renderNPKBar(n, p, k) {
        var canvas = document.getElementById('npkBarChart');
        if (!canvas) return;
        
        if (!isChartAvailable()) {
            showEmptyChart('npkBarChart', '图表库加载中...');
            return;
        }
        
        if (n == null && p == null && k == null) {
            showEmptyChart('npkBarChart', '暂无 NPK 数据');
            return;
        }
        
        clearEmptyChart('npkBarChart');

        new Chart(canvas, {
            type: 'bar',
            data: {
                labels: ['氮 (N)', '磷 (P)', '钾 (K)'],
                datasets: [{
                    label: '含量 (mg/kg)',
                    data: [n || 0, p || 0, k || 0],
                    backgroundColor: [
                        'rgba(59,130,246,0.8)',
                        'rgba(245,158,11,0.8)',
                        'rgba(139,92,246,0.8)'
                    ],
                    borderColor: [
                        'rgb(59,130,246)',
                        'rgb(245,158,11)',
                        'rgb(139,92,246)'
                    ],
                    borderWidth: 2,
                    borderRadius: 8,
                    barPercentage: 0.6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
                    x: { grid: { display: false } }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        cornerRadius: 8,
                        callbacks: {
                            label: function(ctx) { return ctx.parsed.y + ' mg/kg'; }
                        }
                    }
                }
            }
        });
    }

    /** 渲染综合评分趋势折线图 */
    function renderScoreTrend(trend) {
        var canvas = document.getElementById('scoreTrendChart');
        if (!canvas) return;

        if (!isChartAvailable()) {
            showEmptyChart('scoreTrendChart', '图表库加载中...');
            return;
        }

        if (!trend || !trend.health_scores || trend.health_scores.length === 0) {
            showEmptyChart('scoreTrendChart', '暂无评分数据');
            return;
        }

        clearEmptyChart('scoreTrendChart');

        var scores = trend.health_scores.map(function(v) { return v !== null ? v : null; });

        new Chart(canvas, {
            type: 'line',
            data: {
                labels: trend.labels,
                datasets: [{
                    label: '健康评分',
                    data: scores,
                    borderColor: '#16a34a',
                    backgroundColor: 'rgba(22,163,74,0.1)',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#16a34a',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    spanGaps: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: 0, max: 100,
                        grid: { color: 'rgba(0,0,0,0.05)' },
                        ticks: { callback: function(v) { return v + '分'; } }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { maxRotation: 45, maxTicksLimit: 10 }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        cornerRadius: 8,
                        callbacks: {
                            label: function(ctx) { return '评分: ' + ctx.parsed.y + '分'; }
                        }
                    }
                }
            }
        });
    }

    /** 渲染风险等级分布饼图 */
    function renderRiskPie(data) {
        var canvas = document.getElementById('riskPieChart');
        if (!canvas) return;

        if (!isChartAvailable()) {
            showEmptyChart('riskPieChart', '图表库加载中...');
            return;
        }

        if (!data || !data.counts || data.counts.every(function(c) { return c === 0; })) {
            showEmptyChart('riskPieChart', '暂无风险数据');
            return;
        }

        clearEmptyChart('riskPieChart');

        new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.counts,
                    backgroundColor: data.colors.map(function(c) { return c + 'cc'; }),
                    borderColor: data.colors,
                    borderWidth: 2,
                    hoverOffset: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '55%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { padding: 16, usePointStyle: true, pointStyleWidth: 10 }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        cornerRadius: 8,
                        callbacks: {
                            label: function(ctx) {
                                var total = ctx.dataset.data.reduce(function(a, b) { return a + b; }, 0);
                                var pct = total > 0 ? Math.round(ctx.parsed / total * 100) : 0;
                                return ctx.label + ': ' + ctx.parsed + '条 (' + pct + '%)';
                            }
                        }
                    }
                }
            }
        });
    }

    // ================================================================
    // 数据录入页功能
    // ================================================================

    function initInputForm() {
        var form = document.getElementById('soilForm');
        if (!form) return;
        var dateInput = document.getElementById('sample_time');
        if (dateInput && !dateInput.value) {
            dateInput.value = new Date().toISOString().slice(0, 16);
        }
        form.addEventListener('submit', handleFormSubmit);
    }

    function handleFormSubmit(e) {
        e.preventDefault();
        var formData = new FormData(e.target);
        var data = {
            field_id: parseInt(formData.get('field_id')) || null,
            ph: parseFloat(formData.get('ph')) || null,
            nitrogen: parseFloat(formData.get('nitrogen')) || null,
            phosphorus: parseFloat(formData.get('phosphorus')) || null,
            potassium: parseFloat(formData.get('potassium')) || null,
            humidity: parseFloat(formData.get('humidity')) || null,
            temperature: parseFloat(formData.get('temperature')) || null,
            ec: parseFloat(formData.get('ec')) || null,
            organic_matter: parseFloat(formData.get('organic_matter')) || null,
            growth_stage: formData.get('growth_stage') || null,
            sample_time: formData.get('sample_time') || null,
        };
        var hasData = Object.values(data).some(function(v) { return v !== null && v !== ''; });
        if (!hasData) { showMessage('请至少填写一项土壤指标', 'error'); return; }

        showLoading('AI 正在分析土壤数据...');
        fetch('/api/soil/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        })
        .then(function(r) { return r.json(); })
        .then(function(result) {
            hideLoading();
            if (result.success) {
                showMessage('分析完成！', 'success');
                window.location.href = '/result/' + result.record_id;
            } else {
                var msg = result.errors ? result.errors.join('\n') : result.message;
                showMessage(msg || '分析失败', 'error');
            }
        })
        .catch(function(err) {
            hideLoading();
            showMessage('网络错误，请检查服务是否正常运行', 'error');
        });
    }

    // ================================================================
    // 历史记录页功能（含筛选）
    // ================================================================

    var _allRecords = []; // 缓存全部记录用于前端筛选

    function initHistoryPage() {
        var table = document.getElementById('historyTable');
        if (!table) return;
        loadHistoryRecords();
        bindFilterEvents();
    }

    function loadHistoryRecords() {
        fetchWithTimeout('/api/soil/history?limit=200', {}, 10000)
            .then(function(r) { 
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json(); 
            })
            .then(function(data) {
                if (data.success) {
                    _allRecords = data.data || [];
                    renderHistoryTable(_allRecords);
                } else {
                    console.warn('加载历史记录失败:', data.message);
                    _allRecords = [];
                    renderHistoryTable([]);
                }
            })
            .catch(function(e) { 
                console.error('加载历史记录失败:', e.message || e);
                _allRecords = [];
                renderHistoryTable([]);
            });
    }

    function bindFilterEvents() {
        var btnFilter = document.getElementById('btnFilter');
        var btnReset = document.getElementById('btnReset');
        if (btnFilter) btnFilter.addEventListener('click', applyFilter);
        if (btnReset) btnReset.addEventListener('click', resetFilter);
    }

    function applyFilter() {
        var risk = document.getElementById('filterRisk').value;
        var stage = document.getElementById('filterStage').value;
        var fieldId = document.getElementById('filterField').value;

        // 如果选择了地块，重新从服务器获取该地块的记录
        if (fieldId) {
            loadHistoryByField(fieldId);
            return;
        }

        var filtered = _allRecords.filter(function(r) {
            if (risk && r.risk_level !== risk) return false;
            if (stage && r.growth_stage !== stage) return false;
            return true;
        });
        renderHistoryTable(filtered);
    }

    function loadHistoryByField(fieldId) {
        fetchWithTimeout('/api/soil/history?field_id=' + fieldId + '&limit=200', {}, 10000)
            .then(function(r) {
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json();
            })
            .then(function(data) {
                if (data.success) {
                    var records = data.data || [];
                    // 前端再筛选其他条件
                    var risk = document.getElementById('filterRisk').value;
                    var stage = document.getElementById('filterStage').value;
                    var filtered = records.filter(function(r) {
                        if (risk && r.risk_level !== risk) return false;
                        if (stage && r.growth_stage !== stage) return false;
                        return true;
                    });
                    renderHistoryTable(filtered);
                } else {
                    console.warn('加载地块记录失败:', data.message);
                    renderHistoryTable([]);
                }
            })
            .catch(function(e) {
                console.error('加载地块记录失败:', e.message || e);
                renderHistoryTable([]);
            });
    }

    function resetFilter() {
        document.getElementById('filterRisk').value = '';
        document.getElementById('filterStage').value = '';
        document.getElementById('filterField').value = '';
        renderHistoryTable(_allRecords);
    }

    function renderHistoryTable(records) {
        var tbody = document.querySelector('#historyTable tbody');
        if (!tbody) return;

        // 更新记录数
        var countEl = document.getElementById('recordCount');
        if (countEl) countEl.textContent = '共 ' + records.length + ' 条';

        if (records.length === 0) {
            tbody.innerHTML =
                '<tr><td colspan="9" class="empty-state">' +
                '<div class="empty-state-icon">📋</div>' +
                '<h3>暂无匹配记录</h3><p>尝试调整筛选条件</p></td></tr>';
            return;
        }

        tbody.innerHTML = records.map(function(r) {
            var stageName = STAGE_NAMES[r.growth_stage] || (r.growth_stage || '-');
            return '<tr data-id="' + r.id + '">' +
                '<td>' + formatDate(r.created_at) + '</td>' +
                '<td>' + stageName + '</td>' +
                '<td>' + (r.ph != null ? r.ph : '-') + '</td>' +
                '<td>' + (r.nitrogen != null ? r.nitrogen : '-') + '</td>' +
                '<td>' + (r.phosphorus != null ? r.phosphorus : '-') + '</td>' +
                '<td>' + (r.potassium != null ? r.potassium : '-') + '</td>' +
                '<td><span class="badge ' + getScoreBadgeClass(r.health_score) + '">' + (r.health_score || '-') + '</span></td>' +
                '<td><span class="badge ' + getRiskBadgeClass(r.risk_level) + '">' + (r.risk_level || '-') + '</span></td>' +
                '<td><a href="/result/' + r.id + '" class="btn btn-primary" style="padding:0.375rem 0.75rem;font-size:0.875rem;">查看详情</a></td>' +
                '</tr>';
        }).join('');
    }

    // ================================================================
    // 结果页功能（含雷达图）
    // ================================================================

    function initResultPage() {
        var resultContainer = document.querySelector('.result-container');
        if (!resultContainer) return;
        setChartDefaults();
        var pathMatch = window.location.pathname.match(/\/result\/(\d+)/);
        if (!pathMatch) return;
        loadResultDetail(pathMatch[1]);
    }

    function loadResultDetail(recordId) {
        fetchWithTimeout('/api/soil/result/' + recordId, {}, 10000)
            .then(function(r) { 
                if (!r.ok) throw new Error('HTTP ' + r.status);
                return r.json(); 
            })
            .then(function(data) {
                if (data.success) renderResultPage(data.data);
                else {
                    console.warn('加载结果失败:', data.message);
                    showMessage(data.message || '加载结果失败', 'error');
                }
            })
            .catch(function(e) { 
                console.error('加载分析结果失败:', e.message || e);
                showMessage('网络错误，无法加载分析结果', 'error'); 
            });
    }

    function renderResultPage(detail) {
        var analysis = detail.analysis_result;
        if (!analysis) { showMessage('该记录暂无分析数据', 'error'); return; }

        // 地块信息
        renderFieldInfo(detail.field);

        // 评分
        var scoreValue = document.querySelector('.result-score-value');
        if (scoreValue) scoreValue.textContent = analysis.total_score || analysis.health_score;

        // 生长阶段
        var stageLabel = document.getElementById('stageLabel');
        if (stageLabel && analysis.growth_stage) {
            stageLabel.textContent = analysis.growth_stage;
        }

        // 风险
        var riskBadge = document.querySelector('.result-risk-badge');
        if (riskBadge) {
            var rl = analysis.risk_level;
            riskBadge.className = 'result-risk-badge ' + (rl === '低风险' ? 'low' : rl === '中风险' ? 'medium' : 'high');
            riskBadge.innerHTML = (rl === '低风险' ? '✅' : rl === '中风险' ? '⚠️' : '🚨') + ' ' + rl;
        }

        // 多维评分
        renderMultiScores(analysis);

        // 专业诊断概览（新增）
        renderDiagnosticOverview(analysis);

        // 分析卡片
        renderAnalysisCards(analysis);

        // 雷达图
        renderRadarChart(analysis);

        // 总结
        var summaryText = document.querySelector('.summary-text');
        if (summaryText && analysis.summary) {
            // 处理换行符
            summaryText.innerHTML = analysis.summary.replace(/\n/g, '<br>');
        }

        // 建议
        renderRecommendations(analysis.recommendations);
    }

    /** 渲染地块信息 */
    function renderFieldInfo(field) {
        var banner = document.getElementById('fieldInfoBanner');
        var nameEl = document.getElementById('fieldName');
        var detailsEl = document.getElementById('fieldDetails');

        if (!banner || !field) {
            if (banner) banner.style.display = 'none';
            return;
        }

        banner.style.display = 'block';
        nameEl.textContent = field.field_name || '未命名地块';

        var details = [];
        if (field.location) details.push('📍 ' + field.location);
        if (field.area) details.push('📐 ' + field.area + ' 亩');
        if (field.passionfruit_variety) details.push('🥝 ' + field.passionfruit_variety);

        detailsEl.textContent = details.length > 0 ? ' | ' + details.join(' | ') : '';
    }

    /** 渲染多维评分 */
    function renderMultiScores(analysis) {
        // pH评分
        var phScoreEl = document.getElementById('phScore');
        if (phScoreEl) {
            var phScore = analysis.ph_score;
            phScoreEl.textContent = phScore != null ? phScore : '--';
            phScoreEl.className = 'multi-score-value ' + getScoreClass(phScore);
        }

        // NPK评分
        var npkScoreEl = document.getElementById('npkScore');
        if (npkScoreEl) {
            var npkScore = analysis.npk_score;
            npkScoreEl.textContent = npkScore != null ? npkScore : '--';
            npkScoreEl.className = 'multi-score-value ' + getScoreClass(npkScore);
        }

        // 水分评分
        var waterScoreEl = document.getElementById('waterScore');
        if (waterScoreEl) {
            var waterScore = analysis.water_score;
            waterScoreEl.textContent = waterScore != null ? waterScore : '--';
            waterScoreEl.className = 'multi-score-value ' + getScoreClass(waterScore);
        }

        // 温度评分
        var tempScoreEl = document.getElementById('tempScore');
        if (tempScoreEl) {
            var tempScore = analysis.temperature_score;
            tempScoreEl.textContent = tempScore != null ? tempScore : '--';
            tempScoreEl.className = 'multi-score-value ' + getScoreClass(tempScore);
        }

        // EC评分
        var ecScoreEl = document.getElementById('ecScore');
        if (ecScoreEl) {
            var ecScore = analysis.ec_score;
            ecScoreEl.textContent = ecScore != null ? ecScore : '--';
            ecScoreEl.className = 'multi-score-value ' + getScoreClass(ecScore);
        }

        // 有机质评分
        var organicScoreEl = document.getElementById('organicScore');
        if (organicScoreEl) {
            var organicScore = analysis.organic_score;
            organicScoreEl.textContent = organicScore != null ? organicScore : '--';
            organicScoreEl.className = 'multi-score-value ' + getScoreClass(organicScore);
        }

        // 异常指标计数
        var abnormalCountEl = document.getElementById('abnormalCount');
        if (abnormalCountEl) {
            var count = analysis.abnormal_count || 0;
            if (count > 0) {
                abnormalCountEl.innerHTML = '⚠️ 检测到 <strong>' + count + '</strong> 项异常指标需要关注';
                abnormalCountEl.className = 'abnormal-count has-abnormal';
            } else {
                abnormalCountEl.innerHTML = '✅ 各项指标均在正常范围内';
                abnormalCountEl.className = 'abnormal-count';
            }
        }
    }

    /** 获取评分对应的样式类 */
    function getScoreClass(score) {
        if (score == null) return '';
        if (score >= 80) return 'good';
        if (score >= 60) return 'warning';
        return 'danger';
    }

    /** 渲染专业诊断概览（新增） */
    function renderDiagnosticOverview(analysis) {
        // 百香果适配度
        var suitabilityEl = document.getElementById('suitabilityValue');
        if (suitabilityEl) {
            var suitability = analysis.suitability;
            if (suitability != null) {
                suitabilityEl.textContent = suitability + '%';
                suitabilityEl.className = 'overview-value ' + getScoreClass(suitability);
            } else {
                suitabilityEl.textContent = '--';
                suitabilityEl.className = 'overview-value';
            }
        }

        // 产量风险评估
        var yieldRiskEl = document.getElementById('yieldRiskValue');
        if (yieldRiskEl) {
            var yieldRisk = analysis.yield_risk;
            if (yieldRisk && yieldRisk.level) {
                yieldRiskEl.textContent = yieldRisk.level;
                yieldRiskEl.className = 'overview-value ' + (yieldRisk.level === '高风险' ? 'danger' : yieldRisk.level === '中风险' ? 'warning' : '');
            } else {
                yieldRiskEl.textContent = '--';
                yieldRiskEl.className = 'overview-value';
            }
        }

        // 主要限制因子
        var limitingFactorEl = document.getElementById('limitingFactorValue');
        if (limitingFactorEl) {
            var limitingFactor = analysis.limiting_factor;
            if (limitingFactor && limitingFactor.name) {
                limitingFactorEl.textContent = limitingFactor.name + '(' + limitingFactor.score + '分)';
                limitingFactorEl.className = 'overview-value ' + getScoreClass(limitingFactor.score);
            } else {
                limitingFactorEl.textContent = '无';
                limitingFactorEl.className = 'overview-value';
            }
        }

        // Warning Tags
        var tagsContainer = document.getElementById('warningTags');
        if (tagsContainer) {
            tagsContainer.innerHTML = '';
            var tags = analysis.warning_tags || [];
            if (tags.length > 0) {
                tags.forEach(function(tag) {
                    var tagInfo = getTagDisplayInfo(tag);
                    var tagEl = document.createElement('span');
                    tagEl.className = 'warning-tag ' + tagInfo.level;
                    tagEl.innerHTML = tagInfo.icon + ' ' + tagInfo.name;
                    tagEl.style.color = tagInfo.color;
                    tagEl.style.borderColor = tagInfo.color;
                    tagsContainer.appendChild(tagEl);
                });
            }
        }

        // Top Issues
        var issuesContainer = document.getElementById('topIssues');
        if (issuesContainer) {
            issuesContainer.innerHTML = '';
            var issues = analysis.top_issues || [];
            if (issues.length > 0) {
                var titleEl = document.createElement('div');
                titleEl.className = 'top-issues-title';
                titleEl.innerHTML = '🚨 优先处理的问题';
                issuesContainer.appendChild(titleEl);

                issues.forEach(function(issue, index) {
                    var issueEl = document.createElement('div');
                    issueEl.className = 'top-issue-item';
                    issueEl.innerHTML =
                        '<div class="top-issue-number">' + (index + 1) + '</div>' +
                        '<div class="top-issue-content">' +
                        '<div class="top-issue-name">' + issue.name + ' (' + issue.value + ')</div>' +
                        '<div class="top-issue-status">状态: ' + issue.status + '</div>' +
                        '<div class="top-issue-suggestion">' + issue.suggestion + '</div>' +
                        '</div>';
                    issuesContainer.appendChild(issueEl);
                });
            }
        }
    }

    /** 获取标签显示信息 */
    function getTagDisplayInfo(tag) {
        var tagMap = {
            'PH_LOW':        {name: 'pH偏低',       color: '#f59e0b', icon: '⚠️', level: 'warning'},
            'PH_HIGH':       {name: 'pH偏高',       color: '#f59e0b', icon: '⚠️', level: 'warning'},
            'N_LOW':         {name: '氮不足',       color: '#f59e0b', icon: '🌱', level: 'warning'},
            'P_LOW':         {name: '磷不足',       color: '#f59e0b', icon: '🌱', level: 'warning'},
            'K_LOW':         {name: '钾不足',       color: '#ef4444', icon: '🚨', level: 'danger'},
            'HUMIDITY_LOW':  {name: '湿度过低',     color: '#f59e0b', icon: '💧', level: 'warning'},
            'HUMIDITY_HIGH': {name: '湿度过高',     color: '#ef4444', icon: '🚨', level: 'danger'},
            'TEMP_LOW':      {name: '温度偏低',     color: '#3b82f6', icon: '❄️', level: 'info'},
            'TEMP_HIGH':     {name: '温度偏高',     color: '#f59e0b', icon: '🌡️', level: 'warning'},
            'EC_HIGH':       {name: '盐分过高',     color: '#ef4444', icon: '🚨', level: 'danger'},
            'ORGANIC_LOW':   {name: '有机质不足',   color: '#f59e0b', icon: '🌿', level: 'warning'},
        };
        return tagMap[tag] || {name: tag, color: '#6b7280', icon: '📌', level: 'info'};
    }

    function renderAnalysisCards(analysis) {
        var grid = document.getElementById('analysisGrid');
        if (!grid) return;
        grid.innerHTML = '';

        if (analysis.ph_analysis) grid.appendChild(createAnalysisCard('pH 值', analysis.ph_analysis, 'ph'));
        if (analysis.npk_analysis) grid.appendChild(createNPKCard(analysis.npk_analysis));
        if (analysis.humidity_analysis) grid.appendChild(createAnalysisCard('土壤湿度', analysis.humidity_analysis, 'humidity', '%'));
        if (analysis.temperature_analysis) grid.appendChild(createAnalysisCard('土壤温度', analysis.temperature_analysis, 'temperature', '°C'));
        if (analysis.ec_analysis) grid.appendChild(createAnalysisCard('电导率 (EC)', analysis.ec_analysis, 'ec', ' μS/cm'));
        if (analysis.organic_matter_analysis) grid.appendChild(createAnalysisCard('有机质', analysis.organic_matter_analysis, 'organic', '%'));
    }

    function createAnalysisCard(title, data, type, unit) {
        unit = unit || '';
        var status = data.status || '未检测';
        var isGood = status === '适宜';
        var isWarning = status.indexOf('偏低') >= 0 || status.indexOf('偏高') >= 0;
        var isDanger = status.indexOf('严重') >= 0;

        var card = document.createElement('div');
        card.className = 'analysis-card' + (isWarning || isDanger ? ' warning' : '');
        card.innerHTML =
            '<div class="analysis-card-header">' +
            '<span class="analysis-card-title">' + title + '</span>' +
            '<span class="analysis-card-status ' + (isGood ? 'good' : isDanger ? 'danger' : 'warning') + '">' + status + '</span>' +
            '</div>' +
            '<div class="analysis-card-value">' + (data.value !== null && data.value !== undefined ? data.value : '--') + unit + '</div>' +
            '<div class="analysis-card-desc">' + (data.detail || '') + '</div>';
        return card;
    }

    function createNPKCard(data) {
        var ns = data.nitrogen.status || '未检测';
        var ps = data.phosphorus.status || '未检测';
        var ks = data.potassium.status || '未检测';
        var allGood = ns === '适宜' && ps === '适宜' && ks === '适宜';
        var hasW = ns.indexOf('偏低') >= 0 || ns.indexOf('偏高') >= 0 || ps.indexOf('偏低') >= 0 || ps.indexOf('偏高') >= 0 || ks.indexOf('偏低') >= 0 || ks.indexOf('偏高') >= 0;

        var card = document.createElement('div');
        card.className = 'analysis-card' + (hasW ? ' warning' : '');
        card.innerHTML =
            '<div class="analysis-card-header">' +
            '<span class="analysis-card-title">氮磷钾 (NPK)</span>' +
            '<span class="analysis-card-status ' + (allGood ? 'good' : 'warning') + '">' + (allGood ? '均衡' : '需调整') + '</span>' +
            '</div>' +
            '<div class="analysis-card-value">N:' + (data.nitrogen.value !== null ? data.nitrogen.value : '--') +
            ' P:' + (data.phosphorus.value !== null ? data.phosphorus.value : '--') +
            ' K:' + (data.potassium.value !== null ? data.potassium.value : '--') + '</div>' +
            '<div class="analysis-card-desc">' + (data.overall || '') + '</div>';
        return card;
    }

    /** 渲染雷达图 */
    function renderRadarChart(analysis) {
        var canvas = document.getElementById('radarChart');
        if (!canvas) return;
        
        if (!isChartAvailable()) {
            showEmptyChart('radarChart', '图表库加载中...');
            return;
        }
        
        if (!analysis || (!analysis.ph_analysis && !analysis.npk_analysis)) {
            showEmptyChart('radarChart', '暂无评分数据');
            return;
        }
        
        clearEmptyChart('radarChart');

        var labels = ['pH', '氮', '磷', '钾', '湿度', '温度', 'EC', '有机质'];
        var scores = [
            analysis.ph_analysis && analysis.ph_analysis.score != null ? analysis.ph_analysis.score : 0,
            analysis.npk_analysis ? (analysis.npk_analysis.nitrogen.score || 0) : 0,
            analysis.npk_analysis ? (analysis.npk_analysis.phosphorus.score || 0) : 0,
            analysis.npk_analysis ? (analysis.npk_analysis.potassium.score || 0) : 0,
            analysis.humidity_analysis && analysis.humidity_analysis.score != null ? analysis.humidity_analysis.score : 0,
            analysis.temperature_analysis && analysis.temperature_analysis.score != null ? analysis.temperature_analysis.score : 0,
            analysis.ec_analysis && analysis.ec_analysis.score != null ? analysis.ec_analysis.score : 0,
            analysis.organic_matter_analysis && analysis.organic_matter_analysis.score != null ? analysis.organic_matter_analysis.score : 0
        ];

        // 根据分数设置颜色
        var avgScore = scores.reduce(function(a, b) { return a + b; }, 0) / scores.length;
        var mainColor = scoreColor(avgScore);

        new Chart(canvas, {
            type: 'radar',
            data: {
                labels: labels,
                datasets: [{
                    label: '评分',
                    data: scores,
                    backgroundColor: mainColor.replace(')', ',0.15)').replace('rgb', 'rgba'),
                    borderColor: mainColor,
                    borderWidth: 2,
                    pointBackgroundColor: mainColor,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 1,
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { stepSize: 25, font: { size: 10 }, backdropColor: 'transparent' },
                        grid: { color: 'rgba(0,0,0,0.06)' },
                        pointLabels: { font: { size: 12, weight: '500' }, color: '#374151' }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        cornerRadius: 8,
                        callbacks: {
                            label: function(ctx) { return ctx.label + ': ' + ctx.parsed.r + ' 分'; }
                        }
                    }
                }
            }
        });
    }

    function renderRecommendations(recommendations) {
        var section = document.getElementById('recommendationsSection');
        if (!section) return;

        // 如果没有建议，显示默认提示
        if (!recommendations || recommendations.length === 0) {
            section.innerHTML =
                '<div class="recommendations-title">💡 改良建议</div>' +
                '<div class="recommendation-item">' +
                '<div class="recommendation-content">' +
                '<p>当前土壤状况良好，继续保持现有管理措施即可。</p></div></div>';
            return;
        }

        section.innerHTML = '<div class="recommendations-title">💡 改良建议</div>';
        recommendations.forEach(function(rec, index) {
            var item = document.createElement('div');
            item.className = 'recommendation-item' + (rec.priority === 1 ? ' priority-high' : rec.priority === 2 ? ' priority-medium' : '');

            // 构建详情HTML
            var detailsHtml = '';
            if (rec.details && typeof rec.details === 'object') {
                detailsHtml = '<div class="recommendation-details">';
                for (var key in rec.details) {
                    if (rec.details.hasOwnProperty(key)) {
                        detailsHtml +=
                            '<div class="recommendation-details-row">' +
                            '<span class="recommendation-details-label">' + key + '：</span>' +
                            '<span class="recommendation-details-value">' + rec.details[key] + '</span>' +
                            '</div>';
                    }
                }
                detailsHtml += '</div>';
            }

            item.innerHTML =
                '<div class="recommendation-number">' + (index + 1) + '</div>' +
                '<div class="recommendation-content">' +
                '<h4>[' + rec.category + '] ' + rec.title + '</h4>' +
                '<p>' + rec.description + '</p>' +
                detailsHtml +
                '</div>';
            section.appendChild(item);
        });
    }

    // ================================================================
    // 初始化
    // ================================================================

    function init() {
        addAnimationStyles();
        var path = window.location.pathname;
        if (path === '/' || path === '/index') {
            initDashboard();
        } else if (path === '/input') {
            initInputForm();
        } else if (path === '/history') {
            initHistoryPage();
        } else if (path.indexOf('/result/') === 0) {
            initResultPage();
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // ================================================================
    // 导出功能
    // ================================================================

    /** 导出当前记录的 PDF */
    window.exportPDF = function() {
        var recordId = getCurrentRecordId();
        if (!recordId) {
            showMessage('无法获取记录ID', 'error');
            return;
        }
        showLoading('正在生成 PDF 报告...');
        window.location.href = '/api/export/pdf/' + recordId;
        setTimeout(hideLoading, 2000);
    };

    /** 导出当前记录的 Excel */
    window.exportExcel = function() {
        var recordId = getCurrentRecordId();
        if (!recordId) {
            showMessage('无法获取记录ID', 'error');
            return;
        }
        showLoading('正在生成 Excel 报告...');
        window.location.href = '/api/export/excel/' + recordId;
        setTimeout(hideLoading, 2000);
    };

    /** 导出全部历史记录 */
    window.exportAllHistory = function() {
        showLoading('正在生成历史记录 Excel...');
        window.location.href = '/api/export/history/excel';
        setTimeout(hideLoading, 3000);
    };

    /** 获取当前记录ID */
    function getCurrentRecordId() {
        var path = window.location.pathname;
        var match = path.match(/\/result\/(\d+)/);
        return match ? match[1] : null;
    }

    window.SoilApp = {
        showLoading: showLoading,
        hideLoading: hideLoading,
        showMessage: showMessage,
        formatDate: formatDate,
        getScoreBadgeClass: getScoreBadgeClass,
        getRiskBadgeClass: getRiskBadgeClass,
        exportPDF: window.exportPDF,
        exportExcel: window.exportExcel,
        exportAllHistory: window.exportAllHistory
    };

})();
