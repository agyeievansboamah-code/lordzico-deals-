# Query: lordzicos store.p
# ContextLines: 1

from flask import Flask, redirect, render_template_string, request, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import random

app = Flask(__name__)
app.secret_key = "lordzico_deals_final_secure_2026"

# --- Database Configuration (SQLite) ---
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'lordzico_deals.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Business Configuration ---
BUSINESS_WHATSAPP = "233509482808"
BUSINESS_MOMO = "0553141283"
ADMIN_USERNAME = "lordzico"

# --- Database Models ---

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    pin = db.Column(db.String(10), nullable=False)
    registration_ref = db.Column(db.String(100), nullable=False)
    wallet = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    markups = db.relationship('Markup', backref='agent', lazy=True)
    orders = db.relationship('Order', backref='agent', lazy=True)
    withdrawals = db.relationship('Withdrawal', backref='agent', lazy=True)

class Markup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    bundle_id = db.Column(db.Integer, nullable=False)
    selling_price = db.Column(db.Float, nullable=False)

class Customer(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    first_order_date = db.Column(db.DateTime, default=datetime.utcnow)
    orders = db.relationship('Order', backref='customer', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(15), db.ForeignKey('customer.id'), nullable=False)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    bundle_name = db.Column(db.String(100), nullable=False)
    selling_price = db.Column(db.Float, nullable=False)
    recipient_phone = db.Column(db.String(20), nullable=False)
    momo_payer_phone = db.Column(db.String(20), nullable=False)
    
    # Granular Status Fields
    order_status = db.Column(db.String(30), default="Pending")     # Pending, Processing, Complete
    payment_status = db.Column(db.String(30), default="Pending")   # Pending, Settled
    
    order_date = db.Column(db.DateTime, default=datetime.utcnow)

class Withdrawal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('agent.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="PENDING")
    request_date = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# --- Exact Bundle Catalogue ---
BASE_CATALOG = [
    {"id": 1, "network": "MTN", "size": "1 GB", "base_price": 4.00},
    {"id": 2, "network": "MTN", "size": "2 GB", "base_price": 8.00},
    {"id": 3, "network": "MTN", "size": "3 GB", "base_price": 12.30},
    {"id": 4, "network": "MTN", "size": "4 GB", "base_price": 16.40},
    {"id": 5, "network": "MTN", "size": "5 GB (Std)", "base_price": 20.50},
    {"id": 6, "network": "MTN", "size": "5 GB (Lrg)", "base_price": 24.60},
    {"id": 7, "network": "MTN", "size": "8 GB", "base_price": 32.00},
    {"id": 8, "network": "MTN", "size": "10 GB", "base_price": 39.50},
    {"id": 9, "network": "MTN", "size": "15 GB", "base_price": 57.50},
    {"id": 10, "network": "MTN", "size": "20 GB", "base_price": 77.00},
    {"id": 11, "network": "MTN", "size": "25 GB", "base_price": 97.00},
    {"id": 12, "network": "MTN", "size": "30 GB", "base_price": 116.00},
    {"id": 13, "network": "MTN", "size": "40 GB", "base_price": 152.50},
    {"id": 14, "network": "MTN", "size": "50 GB", "base_price": 191.00},
    {"id": 15, "network": "AT Share", "size": "1 GB", "base_price": 3.80},
    {"id": 16, "network": "AT Share", "size": "2 GB", "base_price": 7.60},
    {"id": 17, "network": "AT Share", "size": "3 GB", "base_price": 11.40},
    {"id": 18, "network": "AT Share", "size": "4 GB", "base_price": 15.20},
    {"id": 19, "network": "AT Share", "size": "5 GB", "base_price": 19.00},
    {"id": 20, "network": "AT Share", "size": "6 GB", "base_price": 22.80},
    {"id": 21, "network": "AT Share", "size": "7 GB", "base_price": 26.60},
    {"id": 22, "network": "AT Share", "size": "8 GB", "base_price": 30.40},
    {"id": 23, "network": "AT Share", "size": "9 GB", "base_price": 34.20},
    {"id": 24, "network": "AT Share", "size": "10 GB", "base_price": 37.00},
    {"id": 25, "network": "AT Share", "size": "11 GB", "base_price": 41.80},
    {"id": 26, "network": "AT Share", "size": "12 GB", "base_price": 45.60},
    {"id": 27, "network": "AT Share", "size": "13 GB", "base_price": 49.40},
    {"id": 28, "network": "AT Share", "size": "14 GB", "base_price": 53.20},
    {"id": 29, "network": "AT Share", "size": "15 GB", "base_price": 57.00},
    {"id": 30, "network": "AT Share", "size": "16 GB", "base_price": 60.80},
    {"id": 31, "network": "AT Share", "size": "17 GB", "base_price": 64.60},
    {"id": 32, "network": "AT Share", "size": "18 GB", "base_price": 68.40},
    {"id": 33, "network": "AT Share", "size": "19 GB", "base_price": 72.20},
    {"id": 34, "network": "Telecel", "size": "5 GB", "base_price": 19.50},
    {"id": 35, "network": "Telecel", "size": "10 GB", "base_price": 35.50},
    {"id": 36, "network": "Telecel", "size": "15 GB", "base_price": 52.50},
    {"id": 37, "network": "Telecel", "size": "20 GB", "base_price": 70.00},
    {"id": 38, "network": "Telecel", "size": "30 GB", "base_price": 104.00},
    {"id": 39, "network": "Telecel", "size": "40 GB", "base_price": 138.00},
    {"id": 40, "network": "Telecel", "size": "50 GB", "base_price": 173.00},
    {"id": 41, "network": "Telecel", "size": "55 GB", "base_price": 190.00},
    {"id": 42, "network": "Telecel", "size": "100 GB", "base_price": 343.00},
    {"id": 43, "network": "AT BigTime", "size": "20 GB", "base_price": 60.00},
    {"id": 44, "network": "AT BigTime", "size": "30 GB", "base_price": 70.00},
    {"id": 45, "network": "AT BigTime", "size": "40 GB", "base_price": 80.00},
    {"id": 46, "network": "AT BigTime", "size": "50 GB", "base_price": 90.00},
    {"id": 47, "network": "AT BigTime", "size": "60 GB", "base_price": 125.00},
    {"id": 48, "network": "AT BigTime", "size": "80 GB", "base_price": 155.00},
    {"id": 49, "network": "AT BigTime", "size": "100 GB", "base_price": 175.00},
    {"id": 50, "network": "AT BigTime", "size": "200 GB", "base_price": 330.00},
]

def generate_customer_id():
    while True:
        random_str = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
        new_id = f"LZ-{random_str}"
        if not Customer.query.get(new_id):
            return new_id

def get_agent_data(username):
    return Agent.query.filter_by(username=username).first()

def get_agent_markups(agent):
    markups = Markup.query.filter_by(agent_id=agent.id).all()
    return {m.bundle_id: m.selling_price for m in markups}

def get_catalog_with_prices(agent):
    agent_prices = get_agent_markups(agent)
    full_data = []
    for b in BASE_CATALOG:
        current_price = agent_prices.get(b['id'], b['base_price'])
        full_data.append({**b, 'selling_price': current_price})
    return full_data

# --- HTML Template ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lordzico'Deals - App Portal</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; margin: 0; padding: 15px; color: #333; }
        .container { max-width: 700px; margin: 0 auto; background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h2 { color: #2c3e50; text-align: center; margin-bottom: 5px; }
        .subtitle { color: #7f8c8d; font-size: 13px; text-align: center; margin-bottom: 20px; font-weight: bold; }
        .form-group { margin-bottom: 15px; text-align: left; }
        label { display: block; margin-bottom: 5px; font-weight: 600; font-size: 13px; }
        input, select { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; }
        button { width: 100%; background: #27ae60; color: white; border: none; padding: 12px; border-radius: 6px; font-size: 15px; cursor: pointer; font-weight: bold; }
        button:hover { background: #219653; }
        .link-box { background: #e8f8f5; border: 1px dashed #27ae60; padding: 10px; border-radius: 6px; word-break: break-all; margin-top: 5px; font-family: monospace; font-size: 12px; }
        .wallet-card { background: linear-gradient(135deg, #2c3e50, #4ca1af); color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; text-align: center; }
        .wallet-amount { font-size: 24px; font-weight: bold; margin: 5px 0; }
        .table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 11px; }
        .table th, .table td { border: 1px solid #ddd; padding: 6px; text-align: left; }
        .table th { background-color: #f2f2f2; }
        .alert { background: #fdedec; border: 1px solid #e74c3c; color: #c0392b; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 12px; }
        .nav-tabs { display: flex; gap: 5px; margin-bottom: 15px; border-bottom: 2px solid #eee; padding-bottom: 10px; flex-wrap: wrap; }
        .nav-tabs a { text-decoration: none; padding: 6px 10px; background: #eee; border-radius: 4px; font-size: 11px; font-weight: bold; color: #333; }
        .nav-tabs a.active { background: #3498db; color: white; }
        .logout-btn { background: #e74c3c; margin-top: 20px; text-decoration: none; display: block; text-align: center; color: white; padding: 10px; border-radius: 6px; font-weight: bold; font-size: 13px; }
        .install-banner { background: #e3f2fd; border: 1px solid #90caf9; padding: 12px; border-radius: 8px; margin-bottom: 15px; display: flex; justify-content: space-between; align-items: center; }
        .badge-complete { background: #d4edda; color: #155724; padding: 3px 6px; border-radius: 4px; font-weight: bold; }
        .badge-processing { background: #fff3cd; color: #856404; padding: 3px 6px; border-radius: 4px; font-weight: bold; }
        .badge-pending { background: #f8d7da; color: #721c24; padding: 3px 6px; border-radius: 4px; font-weight: bold; }
        .ref-box { background: #fff3cd; border: 2px dashed #ffb300; padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 15px; }
        .ref-code { font-size: 22px; font-weight: bold; color: #d35400; font-family: monospace; margin: 5px 0; }
    </style>
</head>
<body>
    <div class="container">
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="alert">{{ messages[0] }}</div>
          {% endif %}
        {% endwith %>

        {% if mode == 'auth' %}
            <h2>Lordzico'Deals</h2>
            <div class="subtitle">Agent Access Portal & Order Tracking</div>
            
            <div class="install-banner" id="installContainer" style="display:none;">
                <div>📱 <b>Install App:</b> Add to screen for instant access!</div>
                <button id="installAppBtn" style="width: auto; padding: 6px 12px; background: #1976d2; font-size: 12px;">Install</button>
            </div>

            <div style="display:flex; gap:10px; margin-bottom:15px;">
                <button type="button" onclick="showTab('login')" id="btnLogin" style="background:#3498db;">Agent Login</button>
                <button type="button" onclick="showTab('reg')" id="btnReg" style="background:#bdc3c7;">Register</button>
                <button type="button" onclick="showTab('track')" id="btnTrack" style="background:#9b59b6;">Track Order & Payment</button>
            </div>

            <div id="loginSection">
                <form method="POST" action="/login">
                    <div class="form-group">
                        <label>Agent Username:</label>
                        <input type="text" name="username" placeholder="Username" required>
                    </div>
                    <div class="form-group">
                        <label>Secret PIN:</label>
                        <input type="password" name="pin" placeholder="PIN" required>
                    </div>
                    <button type="submit" style="background: #2980b9;">Login</button>
                </form>
            </div>

            <div id="regSection" style="display:none;">
                <div style="background: #e8f4f8; padding: 10px; border-radius: 6px; margin-bottom: 10px; font-size: 12px;">
                    Pay GHS 14.00 registration fee to MoMo: <b>{{ momo }}</b>, then register below.
                </div>
                <form method="POST" action="/register">
                    <div class="form-group">
                        <label>Choose Username:</label>
                        <input type="text" name="username" required>
                    </div>
                    <div class="form-group">
                        <label>Create Secret PIN:</label>
                        <input type="password" name="pin" required>
                    </div>
                    <div class="form-group">
                        <label>MoMo Number Used for Payment:</label>
                        <input type="text" name="reg_ref" required>
                    </div>
                    <button type="submit">Complete Registration</button>
                </form>
            </div>

            <div id="trackSection" style="display:none;">
                <form method="POST" action="/track_order">
                    <div class="form-group">
                        <label>Enter Your Customer Reference ID:</label>
                        <input type="text" name="customer_id" placeholder="e.g. LZ-7A9B2X" required>
                    </div>
                    <button type="submit" style="background: #9b59b6;">Verify Payment & Track Status</button>
                </form>
            </div>

            <script>
                let deferredPrompt;
                window.addEventListener('beforeinstallprompt', (e) => {
                    e.preventDefault();
                    deferredPrompt = e;
                    document.getElementById('installContainer').style.display = 'flex';
                });
                document.getElementById('installAppBtn').addEventListener('click', () => {
                    if (deferredPrompt) {
                        deferredPrompt.prompt();
                        deferredPrompt.userChoice.then((choice) => {
                            if (choice.outcome === 'accepted') document.getElementById('installContainer').style.display = 'none';
                            deferredPrompt = null;
                        });
                    }
                });
                function showTab(tab) {
                    document.getElementById('loginSection').style.display = tab=='login' ? 'block' : 'none';
                    document.getElementById('regSection').style.display = tab=='reg' ? 'block' : 'none';
                    document.getElementById('trackSection').style.display = tab=='track' ? 'block' : 'none';
                    document.getElementById('btnLogin').style.background = tab=='login' ? '#3498db' : '#bdc3c7';
                    document.getElementById('btnReg').style.background = tab=='reg' ? '#3498db' : '#bdc3c7';
                    document.getElementById('btnTrack').style.background = tab=='track' ? '#3498db' : '#bdc3c7';
                }
            </script>

        {% elif mode == 'order_success' %}
            <h2>Order Placed Successfully!</h2>
            <div class="subtitle">Save your reference code to track payment & data fulfillment.</div>

            <div class="ref-box">
                <div>Your Unique Customer Reference ID:</div>
                <div class="ref-code">{{ order.customer_id }}</div>
                <small style="color: #555;">Use this reference anytime to check if your payment has been settled and your order is complete.</small>
            </div>

            <div style="background: #f8f9fa; border: 1px solid #ddd; padding: 12px; border-radius: 8px; font-size: 13px; margin-bottom: 15px;">
                <p><b>Package:</b> {{ order.bundle_name }}</p>
                <p><b>Amount:</b> GHS {{ "%.2f"|format(order.selling_price) }}</p>
                <p><b>Recipient:</b> {{ order.recipient_phone }}</p>
                <p><b>Payment Status:</b> <span class="badge-pending">Pending Settlement</span></p>
                <p><b>Order Status:</b> <span class="badge-pending">Pending</span></p>
            </div>

            <a href="https://wa.me/{{ whatsapp }}?text={{ wa_msg }}" target="_blank" style="text-decoration:none; display:block; text-align:center; background:#27ae60; color:white; padding:12px; border-radius:6px; font-weight:bold; margin-bottom: 10px;">📲 Send Order & Reference to WhatsApp</a>
            <a href="/" style="text-decoration:none; display:block; text-align:center; background:#3498db; color:white; padding:10px; border-radius:6px; font-weight:bold;">Return to Portal Home</a>

        {% elif mode == 'tracking_result' %}
            <h2>Order & Payment Tracking</h2>
            <div class="subtitle">Reference ID: {{ order.customer_id }}</div>
            
            <div style="background: #f8f9fa; border: 1px solid #ddd; padding: 15px; border-radius: 8px; font-size: 13px; margin-bottom: 15px;">
                <p><b>Package:</b> {{ order.bundle_name }}</p>
                <p><b>Price:</b> GHS {{ "%.2f"|format(order.selling_price) }}</p>
                <p><b>Recipient Phone:</b> {{ order.recipient_phone }}</p>
                <p><b>Payer MoMo:</b> {{ order.momo_payer_phone }}</p>
                <hr>
                <p><b>Payment Verification:</b> 
                    {% if order.payment_status == 'Settled' %}
                        <span style="color: #27ae60; font-weight: bold;">SETTLED & VERIFIED ✅</span>
                    {% else %}
                        <span style="color: #c0392b; font-weight: bold;">PENDING SETTLEMENT ⏳ (Not Verified Yet)</span>
                    {% endif %}
                </p>
                <p><b>Order Progress:</b> 
                    {% if order.order_status == 'Complete' %}
                        <span class="badge-complete">Complete ✅</span>
                    {% elif order.order_status == 'Processing' %}
                        <span class="badge-processing">Processing ⏳</span>
                    {% else %}
                        <span class="badge-pending">Pending ⚠️</span>
                    {% endif %}
                </p>
            </div>
            <a href="/" style="text-decoration:none; display:block; text-align:center; background:#3498db; color:white; padding:10px; border-radius:6px; font-weight:bold;">Back to Home</a>

        {% elif mode == 'dashboard' %}
            <h2>Lordzico'Deals</h2>
            <div class="subtitle">
                {% if is_admin %}👑 MASTER ADMIN VIEW (All Orders){% else %}Agent Dashboard: {{ agent.username | upper }}{% endif %}
            </div>

            <div class="install-banner" id="dashboardInstall" style="display:none;">
                <div>📱 <b>App Installed Access:</b> Launch portal without link hassle.</div>
                <button id="dashInstallBtn" style="width: auto; padding: 6px 12px; background: #1976d2; font-size: 12px;">Install</button>
            </div>
            
            {% if not is_admin %}
            <div class="wallet-card">
                <div>Wallet Balance (Profits)</div>
                <div class="wallet-amount">GHS {{ "%.2f"|format(agent.wallet) }}</div>
                <form method="POST" action="/withdraw" style="margin-top: 10px; display: flex; gap: 5px;">
                    <input type="number" step="0.1" name="withdraw_amount" placeholder="Min 5" required style="padding:6px; border-radius:4px; border:none;">
                    <button type="submit" style="background: #f1c40f; color: #333; width: auto; padding: 6px 12px;">Withdraw</button>
                </form>
            </div>
            <div class="form-group">
                <label>Your Storefront Link:</label>
                <div class="link-box">{{ storefront_link }}</div>
            </div>
            {% endif %}

            <div class="nav-tabs">
                {% if not is_admin %}
                <a href="/dashboard?tab=prices" class="{% if active_tab == 'prices' %}active{% endif %}">Prices</a>
                {% endif %}
                <a href="/dashboard?{% if is_admin %}admin=lordzico&{% endif %}tab=orders" class="{% if active_tab == 'orders' %}active{% endif %}">Orders ({{ orders|length }})</a>
                {% if not is_admin %}
                <a href="/dashboard?tab=verify" class="{% if active_tab == 'verify' %}active{% endif %}">Verify Number</a>
                <a href="/dashboard?tab=withdrawals" class="{% if active_tab == 'withdrawals' %}active{% endif %}">Payouts</a>
                {% endif %}
            </div>

            {% if active_tab == 'prices' and not is_admin %}
                <form method="POST" action="/update_prices">
                    <div style="max-height: 220px; overflow-y: auto; border: 1px solid #ddd; border-radius: 6px;">
                        <table class="table">
                            <tr><th>Bundle</th><th>Base</th><th>Your Price</th></tr>
                            {% for b in catalog %}
                            <tr>
                                <td><b>{{ b.network }}</b> {{ b.size }}</td>
                                <td>{{ "%.2f"|format(b.base_price) }}</td>
                                <td><input type="number" step="0.1" name="p_{{ b.id }}" value="{{ "%.2f"|format(b.selling_price) }}" style="width:60px; text-align:center;"></td>
                            </tr>
                            {% endfor %}
                        </table>
                    </div>
                    <button type="submit" style="margin-top: 10px;">Save Custom Prices</button>
                </form>

            {% elif active_tab == 'orders' %}
                <div style="max-height: 260px; overflow-y: auto;">
                    <table class="table">
                        <tr><th>Ref / Agent</th><th>Package</th><th>Status Control</th></tr>
                        {% for o in orders %}
                        <tr>
                            <td><b>{{ o.customer_id }}</b><br><small>{% if is_admin %}Agent: {{ o.agent.username }}{% else %}{{ o.order_date.strftime('%m-%d %H:%M') }}{% endif %}</small></td>
                            <td>{{ o.bundle_name }}<br><small>{{ o.recipient_phone }} (GHS {{ "%.2f"|format(o.selling_price) }})</small></td>
                            <td>
                                {% if is_admin %}
                                <form method="POST" action="/admin_update_order" style="display:flex; flex-direction:column; gap:3px;">
                                    <input type="hidden" name="order_id" value="{{ o.id }}">
                                    <select name="order_status" style="font-size:10px; padding:2px;">
                                        <option value="Pending" {% if o.order_status == 'Pending' %}selected{% endif %}>Order: Pending</option>
                                        <option value="Processing" {% if o.order_status == 'Processing' %}selected{% endif %}>Order: Processing</option>
                                        <option value="Complete" {% if o.order_status == 'Complete' %}selected{% endif %}>Order: Complete</option>
                                    </select>
                                    <select name="payment_status" style="font-size:10px; padding:2px;">
                                        <option value="Pending" {% if o.payment_status == 'Pending' %}selected{% endif %}>Payment: Pending</option>
                                        <option value="Settled" {% if o.payment_status == 'Settled' %}selected{% endif %}>Payment: Settled</option>
                                    </select>
                                    <button type="submit" style="padding:2px; font-size:10px; background:#2980b9;">Update</button>
                                </form>
                                {% else %}
                                <div>
                                    Order: 
                                    {% if o.order_status == 'Complete' %}<span class="badge-complete">Complete</span>
                                    {% elif o.order_status == 'Processing' %}<span class="badge-processing">Processing</span>
                                    {% else %}<span class="badge-pending">Pending</span>{% endif %}
                                </div>
                                <div style="margin-top:2px;">
                                    Payment: 
                                    {% if o.payment_status == 'Settled' %}<span style="color:green; font-weight:bold;">Settled ✅</span>
                                    {% else %}<span style="color:red; font-weight:bold;">Pending ⏳</span>{% endif %}
                                </div>
                                {% endif %}
                            </td>
                        </tr>
                        {% else %}
                        <tr><td colspan="3" style="text-align:center;">No orders found.</td></tr>
                        {% endfor %}
                    </table>
                </div>

            {% elif active_tab == 'verify' and not is_admin %}
                <div style="background: #eef9f5; padding: 12px; border-radius: 6px; font-size: 13px;">
                    <strong>🔍 Phone Number Network Validator:</strong>
                    <form method="POST" action="/verify_number" style="margin-top:8px;">
                        <input type="text" name="check_phone" placeholder="e.g. 0241234567" required>
                        <button type="submit" style="background: #16a085; margin-top:8px;">Verify</button>
                    </form>
                    {% if verified_result %}
                    <div style="margin-top: 10px; padding: 8px; background: white; border: 1px solid #16a085; border-radius: 4px;">
                        {{ verified_result | safe }}
                    </div>
                    {% endif %}
                </div>

            {% elif active_tab == 'withdrawals' and not is_admin %}
                <div style="max-height: 220px; overflow-y: auto;">
                    <table class="table">
                        <tr><th>Date</th><th>Amount</th><th>Status</th></tr>
                        {% for w in agent.withdrawals %}
                        <tr><td>{{ w.request_date.strftime('%m-%d %H:%M') }}</td><td>GHS {{ "%.2f"|format(w.amount) }}</td><td>{{ w.status }}</td></tr>
                        {% else %}
                        <tr><td colspan="3" style="text-align:center;">No requests.</td></tr>
                        {% endfor %}
                    </table>
                </div>
            {% endif %}

            <a href="/logout" class="logout-btn">Log Out</a>
            
            <script>
                let dashPrompt;
                window.addEventListener('beforeinstallprompt', (e) => {
                    e.preventDefault();
                    dashPrompt = e;
                    document.getElementById('dashboardInstall').style.display = 'flex';
                });
                document.getElementById('dashInstallBtn').addEventListener('click', () => {
                    if (dashPrompt) {
                        dashPrompt.prompt();
                        dashPrompt.userChoice.then((choice) => {
                            if(choice.outcome === 'accepted') document.getElementById('dashboardInstall').style.display = 'none';
                            dashPrompt = null;
                        });
                    }
                });
            </script>

        {% elif mode == 'store' %}
            <h2>Lordzico'Deals Storefront</h2>
            <div class="subtitle">Agent Partner: {{ agent.username | upper }}</div>
            
            <div style="background: #fff8e1; border: 1px solid #ffb300; padding: 10px; border-radius: 6px; margin-bottom: 15px; font-size: 12px;">
                <strong>Instructions:</strong> Send exact payment via MoMo to <b>{{ momo }}</b> and submit details to receive your tracking reference.
            </div>

            <form method="POST" action="/place_order">
                <input type="hidden" name="agent_username" value="{{ agent.username }}">
                <div class="form-group">
                    <label>Select Bundle Package:</label>
                    <select name="bundle_id" required>
                        <option value="">-- Choose Data Package --</option>
                        {% for b in catalog %}
                        <option value="{{ b.id }}">{{ b.network }} | {{ b.size }} - GHS {{ "%.2f"|format(b.selling_price) }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="form-group">
                    <label>Recipient Phone Number:</label>
                    <input type="tel" name="recipient_phone" placeholder="e.g. 0241234567" required>
                </div>
                <div class="form-group">
                    <label>Your MoMo Payer Number:</label>
                    <input type="tel" name="momo_payer" placeholder="e.g. 0553141283" required>
                </div>
                <button type="submit">Generate Reference & Submit Order</button>
            </form>
            <div style="text-align: center; margin-top: 15px;">
                <a href="/" style="font-size: 12px; color: #3498db; text-decoration: none;">🔍 Track order status with reference ID</a>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

# --- Flask Routes ---

@app.route('/')
def index():
    agent_name = request.args.get('agent')
    if agent_name:
        agent = get_agent_data(agent_name.strip().lower())
        if not agent:
            flash("Storefront not found.")
            return redirect(url_for('index'))
        catalog = get_catalog_with_prices(agent)
        return render_template_string(HTML_TEMPLATE, mode='store', agent=agent, catalog=catalog, momo=BUSINESS_MOMO)
    
    if 'agent_id' in session:
        return redirect(url_for('dashboard'))
    
    return render_template_string(HTML_TEMPLATE, mode='auth', momo=BUSINESS_MOMO)

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username', '').strip().lower()
    pin = request.form.get('pin', '').strip()
    reg_ref = request.form.get('reg_ref', '').strip()

    if not username or not pin:
        flash("Username and PIN required.")
        return redirect(url_for('index'))

    if get_agent_data(username):
        flash("Username already taken.")
        return redirect(url_for('index'))

    new_agent = Agent(username=username, pin=pin, registration_ref=reg_ref, wallet=0.0)
    db.session.add(new_agent)
    db.session.commit()

    for b in BASE_CATALOG:
        db.session.add(Markup(agent_id=new_agent.id, bundle_id=b['id'], selling_price=b['base_price']))
    db.session.commit()

    session['agent_id'] = new_agent.id
    flash("Registration successful!")
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip().lower()
    pin = request.form.get('pin', '').strip()
    agent = get_agent_data(username)
    if agent and agent.pin == pin:
        session['agent_id'] = agent.id
        return redirect(url_for('dashboard'))
    
    flash("Invalid credentials.")
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    is_admin_flag = (request.args.get('admin') == ADMIN_USERNAME)
    agent_id = session.get('agent_id')
    if not agent_id and not is_admin_flag:
        return redirect(url_for('index'))
    
    agent = Agent.query.get(agent_id) if agent_id else None
    catalog = get_catalog_with_prices(agent) if agent else []
    active_tab = request.args.get('tab', 'orders' if is_admin_flag else 'prices')
    
    if is_admin_flag:
        orders = Order.query.order_by(Order.order_date.desc()).all()
    else:
        orders = Order.query.filter_by(agent_id=agent.id).order_by(Order.order_date.desc()).all()
        
    storefront_link = f"{request.host_url.rstrip('/')}/?agent={agent.username}" if agent else ""
    verified_result = session.pop('verify_res', None)

    return render_template_string(HTML_TEMPLATE, mode='dashboard', agent=agent, catalog=catalog, 
                                  active_tab=active_tab, orders=orders, storefront_link=storefront_link,
                                  verified_result=verified_result, is_admin=is_admin_flag)

@app.route('/admin_update_order', methods=['POST'])
def admin_update_order():
    order_id = request.form.get('order_id')
    order_status = request.form.get('order_status')
    payment_status = request.form.get('payment_status')
    
    order = Order.query.get(order_id)
    if order:
        order.order_status = order_status
        order.payment_status = payment_status
        db.session.commit()
        flash(f"Order reference {order.customer_id} updated successfully!")
        
    return redirect(url_for('dashboard', admin=ADMIN_USERNAME, tab='orders'))

@app.route('/update_prices', methods=['POST'])
def update_prices():
    agent_id = session.get('agent_id')
    if not agent_id:
        return redirect(url_for('index'))
    agent = Agent.query.get(agent_id)
    for b in BASE_CATALOG:
        key = f"p_{b['id']}"
        if key in request.form:
            try:
                new_price = float(request.form[key])
                if new_price >= b['base_price']:
                    m = Markup.query.filter_by(agent_id=agent.id, bundle_id=b['id']).first()
                    if m: m.selling_price = new_price
                    else: db.session.add(Markup(agent_id=agent.id, bundle_id=b['id'], selling_price=new_price))
            except ValueError:
                pass
    db.session.commit()
    flash("Prices updated.")
    return redirect(url_for('dashboard', tab='prices'))

@app.route('/verify_number', methods=['POST'])
def verify_number():
    agent_id = session.get('agent_id')
    if not agent_id:
        return redirect(url_for('index'))
    phone = request.form.get('check_phone', '').strip()
    
    mtn_p = ['024', '054', '053', '059', '025']
    tel_p = ['020', '050']
    at_p = ['027', '057', '026', '056']

    res = f"Number: <b>{phone}</b><br>"
    if len(phone) == 10 and phone.isdigit():
        pref = phone[:3]
        if pref in mtn_p: res += "✅ Valid <b>MTN</b> Number."
        elif pref in tel_p: res += "✅ Valid <b>Telecel</b> Number."
        elif pref in at_p: res += "✅ Valid <b>AirtelTigo</b> Number."
        else: res += "⚠️ Unsupported prefix format."
    else:
        res += "❌ Invalid format. Must be 10 digits."

    session['verify_res'] = res
    return redirect(url_for('dashboard', tab='verify'))

@app.route('/place_order', methods=['POST'])
def place_order():
    agent_username = request.form.get('agent_username')
    bundle_id = int(request.form.get('bundle_id'))
    recipient = request.form.get('recipient_phone')
    payer = request.form.get('momo_payer')

    agent = get_agent_data(agent_username)
    if not agent:
        flash("Invalid agent.")
        return redirect(url_for('index'))

    base_item = next((b for b in BASE_CATALOG if b['id'] == bundle_id), None)
    markup_item = Markup.query.filter_by(agent_id=agent.id, bundle_id=bundle_id).first()
    selling_price = markup_item.selling_price if markup_item else base_item['base_price']
    profit = selling_price - base_item['base_price']

    if profit > 0:
        agent.wallet += profit

    cust_id = generate_customer_id()
    db.session.add(Customer(id=cust_id))

    bundle_name_str = f"{base_item['network']} | {base_item['size']}"
    new_order = Order(
        customer_id=cust_id,
        agent_id=agent.id,
        bundle_name=bundle_name_str,
        selling_price=selling_price,
        recipient_phone=recipient,
        momo_payer_phone=payer,
        order_status="Pending",
        payment_status="Pending"
    )
    db.session.add(new_order)
    db.session.commit()

    wa_msg = (f"🚨 *NEW STORE ORDER (REF: {cust_id})* 🚨%0A"
              f"-----------------------------------%0A"
              f"🌐 *Agent:* {agent.username}%0A"
              f"📦 *Package:* {bundle_name_str}%0A"
              f"💰 *Price:* GHS {selling_price:.2f}%0A"
              f"📱 *Recipient:* {recipient}%0A"
              f"💳 *Payer MoMo:* {payer}%0A"
              f"-----------------------------------%0A"
              f"✅ Reference Generated: {cust_id}. Please verify payment and settle order!")

    return render_template_string(HTML_TEMPLATE, mode='order_success', order=new_order, whatsapp=BUSINESS_WHATSAPP, wa_msg=wa_msg)

@app.route('/track_order', methods=['POST'])
def track_order():
    cust_id = request.form.get('customer_id', '').strip().upper()
    order = Order.query.filter_by(customer_id=cust_id).first()
    if not order:
        flash("Reference ID not found. Please check your code.")
        return redirect(url_for('index'))
    return render_template_string(HTML_TEMPLATE, mode='tracking_result', order=order)

@app.route('/withdraw', methods=['POST'])
def withdraw():
    agent_id = session.get('agent_id')
    if not agent_id:
        return redirect(url_for('index'))
    agent = Agent.query.get(agent_id)
    try:
        amount = float(request.form.get('withdraw_amount', 0))
        if amount >= 5.0 and agent.wallet >= amount:
            agent.wallet -= amount
            db.session.add(Withdrawal(agent_id=agent.id, amount=amount, status="PENDING"))
            db.session.commit()
            flash("Withdrawal request sent!")
        else:
            flash("Invalid amount or low balance.")
    except ValueError:
        flash("Invalid input.")
    return redirect(url_for('dashboard', tab='withdrawals'))

@app.route('/logout')
def logout():
    session.pop('agent_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)