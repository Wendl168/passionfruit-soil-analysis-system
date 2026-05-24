/**
 * input.js - 土壤数据录入页面交互逻辑
 * 负责表单提交、数据校验、调用后端 API、结果展示。
 */

(function () {
    "use strict";

    // 设置默认日期为今天
    var dateInput = document.getElementById("sample_date");
    if (dateInput) {
        dateInput.value = new Date().toISOString().split("T")[0];
    }

    // 表单提交
    var form = document.getElementById("soilForm");
    var submitBtn = document.getElementById("submitBtn");
    var loadingOverlay = document.getElementById("loadingOverlay");

    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            handleSubmit();
        });
    }

    function handleSubmit() {
        // 收集表单数据
        var formData = {
            sample_code: getInputValue("sample_code"),
            sample_date: getInputValue("sample_date"),
            location: getInputValue("location"),
            ph_value: getNumericValue("ph_value"),
            ec_value: getNumericValue("ec_value"),
            moisture: getNumericValue("moisture"),
            organic_matter: getNumericValue("organic_matter"),
            nitrogen: getNumericValue("nitrogen"),
            phosphorus: getNumericValue("phosphorus"),
            potassium: getNumericValue("potassium"),
            calcium: getNumericValue("calcium"),
            magnesium: getNumericValue("magnesium"),
            sulfur: getNumericValue("sulfur"),
            iron: getNumericValue("iron"),
            manganese: getNumericValue("manganese"),
            zinc: getNumericValue("zinc"),
            copper: getNumericValue("copper"),
            boron: getNumericValue("boron"),
        };

        // 显示加载状态
        showLoading(true);
        submitBtn.disabled = true;

        // 发送请求
        fetch("/api/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(formData),
        })
            .then(function (res) {
                return res.json();
            })
            .then(function (data) {
                showLoading(false);
                submitBtn.disabled = false;

                if (data.success) {
                    // 跳转到结果页
                    window.location.href = "/result/" + data.record_id;
                } else {
                    // 显示错误
                    var msg = data.message || "分析失败";
                    if (data.errors && data.errors.length > 0) {
                        msg += "\n" + data.errors.join("\n");
                    }
                    alert(msg);
                }
            })
            .catch(function (err) {
                showLoading(false);
                submitBtn.disabled = false;
                alert("网络错误，请检查后端服务是否启动。");
                console.error(err);
            });
    }

    function getInputValue(id) {
        var el = document.getElementById(id);
        return el ? el.value.trim() : "";
    }

    function getNumericValue(id) {
        var el = document.getElementById(id);
        if (!el || el.value.trim() === "") return null;
        return parseFloat(el.value);
    }

    function showLoading(show) {
        if (loadingOverlay) {
            loadingOverlay.style.display = show ? "flex" : "none";
        }
    }
})();
