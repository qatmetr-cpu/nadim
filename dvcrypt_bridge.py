import datetime
import os
import requests
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)

login_reports = []

DVCrypt_MASTER_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DVCrypt Management & Reports</title>
    <style>
        * { box-sizing: border-box; font-family: Tahoma, sans-serif; }
        body { background-color: #262626; color: #000; margin: 0; padding: 10px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .win-box { background: #f0f0f0; border: 1px solid #7a7a7a; border-radius: 3px; width: 100%; max-width: 500px; padding: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.7); }
        .win-header { background: linear-gradient(to bottom, #10336b, #0c2347); color: white; padding: 6px 10px; font-weight: bold; font-size: 0.9rem; display: flex; justify-content: space-between; align-items: center; margin: -12px -12px 12px -12px; }
        .form-row { margin-bottom: 8px; display: flex; align-items: center; }
        .form-row label { width: 110px; font-size: 0.8rem; font-weight: bold; color: #000; }
        .form-row input, .form-row select { flex: 1; padding: 5px; border: 1px solid #7f9db9; background: #fff; font-size: 0.9rem; border-radius: 2px; }
        .section-box { border: 1px solid #ccc; padding: 10px; margin-top: 10px; background: #fafafa; }
        .status-group { font-size: 0.85rem; margin-top: 5px; }
        .status-group label { display: block; margin-bottom: 4px; font-weight: normal; }
        .btn-row { display: flex; justify-content: flex-end; gap: 6px; margin-top: 12px; }
        .win-btn { background: #e1e1e1; border: 1px solid #adadad; padding: 5px 15px; font-size: 0.85rem; cursor: pointer; border-radius: 2px; font-weight: bold; min-width: 75px; }
        .win-btn:hover { background: #e5f1fb; border-color: #0078d7; }
        .win-btn.ok { background: #10b981; color: white; border-color: #059669; }
        .win-btn.ok:hover { background: #059669; }
        .step { display: none; }
        .step.active { display: block; }
        .error-msg { color: #d9534f; font-size: 0.8rem; margin-top: 5px; text-align: center; font-weight: bold; }
        .msg { text-align: center; font-size: 0.85rem; margin-top: 5px; font-weight: bold; }
        .report-box { background: #1e293b; color: #38bdf8; padding: 8px; border-radius: 3px; font-size: 0.8rem; max-height: 150px; overflow-y: auto; margin-top: 10px; text-align: right; }
        .results-table { width: 100%; border-collapse: collapse; margin-top: 10px; background: #fff; font-size: 0.85rem; }
        .results-table th, .results-table td { border: 1px solid #ccc; padding: 6px; text-align: right; }
        .results-table th { background: #e9ecef; color: #333; }
        .results-table tr:hover { background: #e5f1fb; cursor: pointer; }
    </style>
</head>
<body>

<div class="win-box">

    <!-- 1. نافذة الاتصال (Connection) -->
    <div id="step-conn" class="step active">
        <div class="win-header"><span>Connection</span><span>✕</span></div>
        <div style="margin-bottom: 10px; font-size: 0.85rem;">
            <label><input type="radio" name="cType" checked> This computer</label><br>