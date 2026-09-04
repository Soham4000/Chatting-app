import streamlit as st
import streamlit.components.v1 as components
import json
import sqlite3
import hashlib
import base64
import smtplib
import ssl
import random
import os
import uuid
from email.message import EmailMessage
import html
from streamlit_mic_recorder import mic_recorder

# Optional: keeps "Online" / "last seen" presence live without
# requiring the person to click anything. If the package isn't
# installed, the app still works -- presence just only refreshes
# when the person interacts with the page (old behavior).
try:
    from streamlit_autorefresh import st_autorefresh
    _AUTOREFRESH_AVAILABLE = True
except ImportError:
    _AUTOREFRESH_AVAILABLE = False

# Optional: lets a login survive closing/reopening the app (a
# "remember me" cookie), instead of forcing a fresh login every
# time like it does today. If the package isn't installed, the
# app still works -- it just always shows the login screen.
try:
    from streamlit_cookies_manager import EncryptedCookieManager
    _COOKIES_AVAILABLE = True
except ImportError:
    _COOKIES_AVAILABLE = False

# =========================
# NOTIFICATION SOUND (WhatsApp-style "ding")
# =========================

NOTIFICATION_SOUND_B64 = (
    "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"
)


def play_notification_sound():
    """Plays a short notification sound using an invisible autoplay audio tag."""
    st.markdown(
        f"""
        <audio autoplay style="display:none;">
            <source src="data:audio/wav;base64,{NOTIFICATION_SOUND_B64}" type="audio/wav">
        </audio>
        """,
        unsafe_allow_html=True
    )


def request_desktop_notification_permission():
    """Asks the browser for permission to show desktop notifications.
    Must be triggered by a real user click (e.g. a Settings button) —
    browsers ignore/ auto-deny permission requests that aren't tied to
    a genuine user gesture."""
    components.html(
        """
        <script>
        if ("Notification" in window.parent) {
            window.parent.Notification.requestPermission();
        }
        </script>
        """,
        height=0
    )


def send_desktop_notification(title, body):
    """Fires a real OS-level browser notification (shows even if the tab
    is in the background/minimized), if the user has granted permission."""
    safe_title = title.replace('"', "'").replace("\\n", " ")
    safe_body = body.replace('"', "'").replace("\\n", " ")
    components.html(
        f"""
        <script>
        try {{
            if ("Notification" in window.parent &&
                window.parent.Notification.permission === "granted") {{
                new window.parent.Notification("{safe_title}", {{
                    body: "{safe_body}",
                    icon: "https://cdn-icons-png.flaticon.com/512/2462/2462719.png"
                }});
            }}
        }} catch (e) {{}}
        </script>
        """,
        height=0
    )


def show_popup_banner(title, body):
    """Shows a large, prominent in-app popup banner (bigger/louder than
    st.toast) that slides in from the top-right and auto-fades."""
    safe_title = html.escape(title)
    safe_body = html.escape(body)
    st.markdown(
        f'<div style="position:fixed;top:70px;right:24px;z-index:9999;'
        f'background:#075E54;color:#fff;padding:16px 20px;border-radius:12px;'
        f'box-shadow:0 6px 20px rgba(0,0,0,0.3);max-width:320px;'
        f'animation:mychat_popup_fade 5s ease forwards;">'
        f'<div style="font-weight:700;font-size:15px;margin-bottom:4px;">'
        f'💬 {safe_title}</div>'
        f'<div style="font-size:13px;opacity:0.9;">{safe_body}</div>'
        f'</div>'
        f'<style>'
        f'@keyframes mychat_popup_fade {{'
        f'0% {{ opacity:0; transform:translateY(-12px); }}'
        f'10% {{ opacity:1; transform:translateY(0); }}'
        f'85% {{ opacity:1; }}'
        f'100% {{ opacity:0; transform:translateY(-12px); }}'
        f'}}'
        f'</style>',
        unsafe_allow_html=True
    )

# =========================
# APP SETTINGS
# =========================

st.set_page_config(
    page_title="MyChat",
    page_icon="💬",
    layout="wide"
)

# ==========================================
# "REPLIED TO" PREVIEW STYLING
# (the small clickable snippet shown above a
# message that was sent as a reply -- style it
# like a proper quoted-reply card so it's
# unmistakable, in both 1-on-1 and group chats)
# ==========================================

st.markdown(
    """
    <style>
    div[class*="st-key-jump_to_"] button,
    div[class*="st-key-group_jump_to_"] button {
        background: #f0f2f5 !important;
        border: none !important;
        border-left: 4px solid #06d755 !important;
        border-radius: 6px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        color: #3b4a54 !important;
        font-size: 13px !important;
        font-weight: 400 !important;
        white-space: normal !important;
        height: auto !important;
        padding: 6px 10px !important;
        margin-bottom: 2px !important;
    }
    div[class*="st-key-jump_to_"] button:hover,
    div[class*="st-key-group_jump_to_"] button:hover {
        background: #e4e6ea !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# LOGIN SESSION
# ==========================================

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# ==========================================
# THEME SETTINGS
# ==========================================

themes = {

    "Light": {
        "bg": "#FFFFFF",
        "text": "#000000",
        "secondary": "#F5F5F5",
        "accent": "#2196F3"
    },

    "Dark": {
        "bg": "#121212",
        "text": "#FFFFFF",
        "secondary": "#1E1E1E",
        "accent": "#BB86FC"
    },

    "WhatsApp Green": {
        "bg": "#E5DDD5",
        "text": "#111111",
        "secondary": "#DCF8C6",
        "accent": "#25D366"
    },

    "Ocean Blue": {
        "bg": "#EAF6FF",
        "text": "#073B4C",
        "secondary": "#D6EEFF",
        "accent": "#0077B6"
    },

    "Midnight Purple": {
        "bg": "#160B26",
        "text": "#FFFFFF",
        "secondary": "#24133D",
        "accent": "#9B5DE5"
    },

    "Rose Pink": {
        "bg": "#FFF0F5",
        "text": "#4A102A",
        "secondary": "#FFD6E5",
        "accent": "#E91E63"
    },

    "Sunset Orange": {
        "bg": "#FFF3E0",
        "text": "#4E2600",
        "secondary": "#FFE0B2",
        "accent": "#FF6D00"
    },

    "Forest Green": {
        "bg": "#EAF4EA",
        "text": "#17351B",
        "secondary": "#D5E8D4",
        "accent": "#2E7D32"
    },

    "Coffee Brown": {
        "bg": "#F5EBDD",
        "text": "#3E2723",
        "secondary": "#E6D3B3",
        "accent": "#795548"
    }
}
# =========================================================
# CHAT WALLPAPERS
# =========================================================

chat_wallpapers = {

    "Floating Glow": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(0, 180, 255, 0.25),
                transparent 35%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(150, 50, 255, 0.15),
                transparent 35%
            ),
            #101827;
    """,

    "Dark Grid": """
        background-color: #111827;
        background-image:
            linear-gradient(#ffffff08 1px, transparent 1px),
            linear-gradient(90deg, #ffffff08 1px, transparent 1px);
        background-size: 30px 30px;
    """,

    "Neon Blue": """
        background:
            radial-gradient(
                circle at center,
                rgba(0, 120, 255, 0.25),
                #020617 70%
            );
    """,

    "Purple Galaxy": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(168, 85, 247, 0.35),
                transparent 30%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(236, 72, 153, 0.25),
                transparent 35%
            ),
            #0b0614;
    """,

    "Ocean Waves": """
        background:
            linear-gradient(
                135deg,
                #003b5c,
                #006994,
                #001f3f
            );
    """,

    "Sunset": """
        background:
            linear-gradient(
                135deg,
                #ff7e5f,
                #feb47b,
                #7b4397
            );
    """,

    "Minimal": """
        background: #f5f5f5;
    """,

    "WhatsApp Style": """
        background-color: #efeae2;
        background-image:
            radial-gradient(
                rgba(0,0,0,0.05) 1px,
                transparent 1px
            );
        background-size: 20px 20px;
    """,

    

    "🌌 Aurora Dream": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(139, 233, 255, 0.35),
                transparent 35%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(192, 132, 252, 0.25),
                transparent 35%
            ),
            linear-gradient(
                135deg,
                #eef7ff,
                #f5efff
            );
    """,

    "🫧 Crystal Bubble": """
        background:
            radial-gradient(
                circle at 25% 25%,
                rgba(255,255,255,0.75),
                transparent 18%
            ),
            radial-gradient(
                circle at 75% 75%,
                rgba(185,234,255,0.40),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #e8faff,
                #f2f7ff
            );
    """,

    "🌸 Sakura Glow": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(255,183,213,0.30),
                transparent 30%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(255,214,232,0.35),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #fff1f6,
                #fff8fb
            );
    """,

    "💎 Crystal Mist": """
        background:
            radial-gradient(
                circle at 30% 20%,
                rgba(185,234,255,0.40),
                transparent 30%
            ),
            radial-gradient(
                circle at 75% 75%,
                rgba(217,199,255,0.30),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #eefaff,
                #f4efff
            );
    """,

    "🌅 Golden Sunset": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(255,209,102,0.35),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #fff3d6,
                #ffe9dc,
                #f4e4ff
            );
    """,

    "🦋 Dreamy Sky": """
        background:
            radial-gradient(
                circle at 20% 30%,
                rgba(143,211,255,0.35),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #eaf8ff,
                #edf3ff
            );
    """,

    "🌊 Ocean Pearl": """
        background:
            radial-gradient(
                circle at 75% 25%,
                rgba(125,211,252,0.35),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #e7f9ff,
                #eaf4ff
            );
    """,

    "🌙 Moonlit Cloud": """
        background:
            radial-gradient(
                circle at 70% 20%,
                rgba(255,255,255,0.70),
                transparent 25%
            ),
            linear-gradient(
                135deg,
                #e8ecf8,
                #dfe8f5
            );
    """,

    "💜 Purple Silk": """
        background:
            radial-gradient(
                circle at 25% 25%,
                rgba(196,181,253,0.35),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #f3edff,
                #ebe5ff
            );
    """,

    "🩵 Arctic Pearl": """
        background:
            radial-gradient(
                circle at 30% 20%,
                rgba(255,255,255,0.80),
                transparent 25%
            ),
            linear-gradient(
                135deg,
                #e8fbff,
                #edf8ff
            );
    """,

    "🌷 Rose Silk": """
        background:
            radial-gradient(
                circle at 20% 30%,
                rgba(253,164,175,0.30),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #fff0f4,
                #ffe8ef
            );
    """,

    "🍑 Peach Silk": """
        background:
            radial-gradient(
                circle at 75% 25%,
                rgba(253,186,116,0.30),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #fff1e8,
                #ffebe3
            );
    """,

    "🌿 Emerald Mist": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(110,231,183,0.35),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #ecfff6,
                #e7f8f0
            );
    """,

    "✨ Champagne Glow": """
        background:
            radial-gradient(
                circle at 50% 20%,
                rgba(253,230,138,0.40),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #fff9e8,
                #fff3d8
            );
    """,

    "☁️ Cloud Velvet": """
        background:
            radial-gradient(
                circle at 30% 30%,
                rgba(255,255,255,0.80),
                transparent 25%
            ),
            radial-gradient(
                circle at 75% 70%,
                rgba(255,255,255,0.50),
                transparent 28%
            ),
            #f1f5f9;
    """,

    "🪻 Lavender Silk": """
        background:
            radial-gradient(
                circle at 75% 25%,
                rgba(196,181,253,0.35),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #f6f0ff,
                #eee7ff
            );
    """,

    "🩷 Blush Pearl": """
        background:
            radial-gradient(
                circle at 25% 25%,
                rgba(249,168,212,0.35),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #fff1f7,
                #ffeaf3
            );
    """,

    "🌈 Prism Glow": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(249,168,212,0.30),
                transparent 28%
            ),
            radial-gradient(
                circle at 80% 25%,
                rgba(147,197,253,0.30),
                transparent 28%
            ),
            radial-gradient(
                circle at 50% 90%,
                rgba(134,239,172,0.25),
                transparent 30%
            ),
            #f7f9ff;
    """,

    "💫 Stardust Mist": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(196,181,253,0.30),
                transparent 30%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(147,197,253,0.30),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #f3f0ff,
                #eef5ff
            );
    """,

    "🌤 Heavenly Sky": """
        background:
            radial-gradient(
                circle at 70% 20%,
                rgba(255,255,255,0.80),
                transparent 25%
            ),
            linear-gradient(
                135deg,
                #e8f7ff,
                #f5fbff
            );
    """,

    "🧊 Frozen Glass": """
        background:
            radial-gradient(
                circle at 25% 25%,
                rgba(255,255,255,0.70),
                transparent 25%
            ),
            linear-gradient(
                135deg,
                #e8faff,
                #e6f0ff
            );
    """,

    "🌺 Floral Haze": """
        background:
            radial-gradient(
                circle at 20% 25%,
                rgba(251,207,232,0.35),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #fff3f8,
                #fff0f5
            );
    """,

    "🍃 Jade Whisper": """
        background:
            radial-gradient(
                circle at 75% 25%,
                rgba(134,239,172,0.30),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #effff5,
                #e9f8f0
            );
    """,

    "🌙 Midnight Pearl": """
        background:
            radial-gradient(
                circle at 70% 25%,
                rgba(196,181,253,0.25),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #20253a,
                #171b2e
            );
    """,

    "💙 Sapphire Mist": """
        background:
            radial-gradient(
                circle at 25% 25%,
                rgba(96,165,250,0.35),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #eaf4ff,
                #e4efff
            );
    """,

    "🪞 Silver Glass": """
        background:
            radial-gradient(
                circle at 25% 25%,
                rgba(255,255,255,0.80),
                transparent 25%
            ),
            linear-gradient(
                135deg,
                #f3f5f7,
                #e8edf2
            );
    """,

    "🌅 Coral Horizon": """
        background:
            radial-gradient(
                circle at 80% 20%,
                rgba(251,113,133,0.30),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #fff0e8,
                #ffe7e0
            );
    """,

    "🫧 Aqua Pearl": """
        background:
            radial-gradient(
                circle at 25% 25%,
                rgba(103,232,249,0.35),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #e8fffd,
                #e8f8ff
            );
    """,

    "🌼 Vanilla Glow": """
        background:
            radial-gradient(
                circle at 70% 25%,
                rgba(253,230,138,0.35),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #fffbed,
                #fff6dc
            );
    """,

    "🔮 Mystic Glass": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(167,139,250,0.35),
                transparent 30%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(103,232,249,0.25),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #f2edff,
                #eafaff
            );
    """
}
# ==========================================
# SAVED THEME
# ==========================================

if "saved_theme" not in st.session_state:
    st.session_state["saved_theme"] = "Light"

saved_theme = st.session_state["saved_theme"]

if isinstance(saved_theme, dict) or saved_theme not in themes:
    saved_theme = "Light"
    st.session_state["saved_theme"] = "Light"

current_theme = themes[saved_theme]
       

# ==========================================
# SAVED THEME
# ==========================================

if "saved_theme" not in st.session_state:
    st.session_state["saved_theme"] = "Light"


# ==========================================
# LOAD SAVED THEME SAFELY
# ========================================== 

saved_theme = st.session_state.get("saved_theme", "Light")

# If saved_theme accidentally contains a dictionary,
# reset it to a theme name
if isinstance(saved_theme, dict):
    saved_theme = "Light"

# If the theme name doesn't exist, reset it
if saved_theme not in themes:
    saved_theme = "Light"

st.session_state["saved_theme"] = saved_theme

current_theme = themes[saved_theme]

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {current_theme["bg"]};
        color: {current_theme["text"]};
    }}

    .stApp p,
    .stApp span,
    .stApp label,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4 {{
        color: {current_theme["text"]};
    }}

    section[data-testid="stSidebar"] {{
        background-color: {current_theme["secondary"]};
    }}

    .stButton > button {{
        background-color: {current_theme["accent"]};
        color: white;
        border: none;
        border-radius: 8px;
    }}

    .stButton > button:hover {{
        opacity: 0.85;
    }}

    </style>
    """,
    unsafe_allow_html=True
)
# =========================
# DATABASE
# =========================
DB_PATH = "chat.db"

conn = sqlite3.connect(
    "chat.db",
    timeout=10,
    check_same_thread=False
)

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    username TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    password TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact TEXT,
    sender TEXT,
    message TEXT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")



cursor.execute("""
CREATE TABLE IF NOT EXISTS profiles(
    username TEXT PRIMARY KEY,
    image TEXT
)
""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS status(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    text TEXT,
    file BLOB,
    file_type TEXT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")


try:
    cursor.execute("ALTER TABLE status ADD COLUMN file BLOB")
except sqlite3.OperationalError:
    pass

try:
    cursor.execute("ALTER TABLE status ADD COLUMN file_type TEXT")
except sqlite3.OperationalError:
    pass
try:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN phone TEXT"
    )
    conn.commit()
except sqlite3.OperationalError:
    pass
try:
    cursor.execute(
        "ALTER TABLE messages ADD COLUMN receiver TEXT"
    )
    conn.commit()
except sqlite3.OperationalError as e:
    if "duplicate column name" not in str(e).lower():
        raise
# Add seen column
try:
    cursor.execute("""
        ALTER TABLE messages
        ADD COLUMN seen INTEGER DEFAULT 0
    """)
    conn.commit()
except sqlite3.OperationalError as e:
    if "duplicate column name" not in str(e).lower():
        raise    


conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact TEXT,
    sender TEXT,
    message TEXT,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    receiver TEXT,
    seen INTEGER DEFAULT 0,
    audio_path TEXT,
    reply_to INTEGER
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS deleted_chats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    friend TEXT NOT NULL,
    UNIQUE(username, friend)
)
""")

conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS blocked_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    blocked_user TEXT NOT NULL,
    UNIQUE(username, blocked_user)
)
""")

conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS blocked_users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    blocked_user TEXT NOT NULL,
    UNIQUE(username, blocked_user)
)
""")

conn.commit()
# ==================================================
# GROUP CHAT TABLES
# ==================================================

cursor.execute("""
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT ,
    creator TEXT ,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS group_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(group_id, username)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS group_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    sender TEXT NOT NULL,
    message TEXT NOT NULL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reply_to INTEGER,
    FOREIGN KEY(group_id) REFERENCES groups(id)
)
""")

conn.commit()

# ==========================================
# ADD REPLY_TO COLUMN IF NOT EXISTS
# ==========================================

try:
    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute(
        "ALTER TABLE messages ADD COLUMN reply_to INTEGER"
    )

    conn.commit()
    conn.close()

except sqlite3.OperationalError:
    # Column already exists
    pass

except sqlite3.OperationalError as e:

    if "duplicate column name" not in str(e).lower():
        raise
    
try:
    cursor.execute(
        "ALTER TABLE messages ADD COLUMN audio_path TEXT"
    )
except sqlite3.OperationalError:
    pass
try:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN profile_pic TEXT"
    )
except sqlite3.OperationalError:
    pass

# Add bio column if it doesn't exist
try:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN bio TEXT"
    )
except sqlite3.OperationalError:
    pass

# ==================================================
# ONLINE / LAST SEEN COLUMNS
# ==================================================

try:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN last_active TIMESTAMP"
    )
except sqlite3.OperationalError:
    pass

try:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN show_online_status INTEGER DEFAULT 1"
    )
except sqlite3.OperationalError:
    pass

try:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN show_last_seen INTEGER DEFAULT 1"
    )
except sqlite3.OperationalError:
    pass

# Saved theme, so it survives logout/login and app restarts
# instead of resetting to default every time.
try:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN theme TEXT"
    )
except sqlite3.OperationalError:
    pass

# "Keep me logged in" token, so re-opening the app doesn't
# force a fresh login every single time.
try:
    cursor.execute(
        "ALTER TABLE users ADD COLUMN remember_token TEXT"
    )
except sqlite3.OperationalError:
    pass

conn.commit()

# ================================================== 
# FIX / MIGRATE GROUPS TABLE
# ==================================================

cursor.execute("PRAGMA table_info(groups)")
group_columns = [
    row[1]
    for row in cursor.fetchall()
]

if "name" not in group_columns:
    cursor.execute(
        "ALTER TABLE groups ADD COLUMN name TEXT"
    )

if "creator" not in group_columns:
    cursor.execute(
        "ALTER TABLE groups ADD COLUMN creator TEXT"
    )

if "created_at" not in group_columns:
    cursor.execute(
        """
        ALTER TABLE groups
        ADD COLUMN created_at
        TIMESTAMP
        """
    )

if "group_pic" not in group_columns:
    cursor.execute(
        "ALTER TABLE groups ADD COLUMN group_pic TEXT"
    )

conn.commit()


# ========================= 
# FUNCTIONS
# =========================
def hash_password(password):
    return hashlib.sha256(
        password.encode("utf-8")
    ).hexdigest()


def register(username, email, phone, password):

    username = username.strip()
    email = email.strip().lower()
    phone = phone.strip()

    try:
        with sqlite3.connect(
            DB_PATH,
            timeout=30,
            check_same_thread=False
        ) as db:

            db.execute("PRAGMA busy_timeout = 30000")

            db.execute(
                """
                INSERT INTO users
                (username, email, phone, password)
                VALUES (?, ?, ?, ?)
                """,
                (
                    username,
                    email,
                    phone,
                    hash_password(password)
                )
            )

            db.commit()

        return True

    except sqlite3.IntegrityError:
        return False

    except sqlite3.OperationalError as e:

        if "database is locked" in str(e).lower():
            st.error("Database is busy. Please try again.")
            return False

        raise

# =========================
# GET PROFILE PICTURE
# =========================

def get_profile_pic(username):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute(
        "PRAGMA busy_timeout = 30000"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT profile_pic
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    result = cursor.fetchone()

    conn.close()

    if result and result[0]:
        return result[0]

    return None


def login(email, password):

    email = email.strip().lower()

    try:
        with sqlite3.connect(
            DB_PATH,
            timeout=30,
            check_same_thread=False
        ) as db:

            db.execute("PRAGMA busy_timeout = 30000")

            cursor = db.cursor()

            cursor.execute(
                """
                SELECT username, password
                FROM users
                WHERE LOWER(TRIM(email)) = ?
                LIMIT 1
                """,
                (email,)
            )

            result = cursor.fetchone()

            if result is None:
                return None

            username, stored_password = result

            # New accounts: hashed password
            if stored_password == hash_password(password):
                return username

            # Old accounts: plain-text password
            # Allows existing accounts to continue working
            if stored_password == password:

                # Upgrade old password to hashed password
                cursor.execute(
                    """
                    UPDATE users
                    SET password = ?
                    WHERE username = ?
                    """,
                    (
                        hash_password(password),
                        username
                    )
                )

                db.commit()

                return username

            return None

    except sqlite3.OperationalError as e:

        if "database is locked" in str(e).lower():
            st.error("Database is busy. Please try again.")
            return None

        raise


# ==========================================
# SAVED THEME (persisted per account, in the DB --
# not just in the browser session)
# ==========================================

def get_saved_theme(username):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )
    conn.execute("PRAGMA busy_timeout=30000")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT theme FROM users WHERE username = ?",
        (username,)
    )

    row = cursor.fetchone()
    conn.close()

    if row and row[0]:
        return row[0]

    return "Light"


def save_theme_for_user(username, theme_name):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )
    conn.execute("PRAGMA busy_timeout=30000")

    conn.execute(
        "UPDATE users SET theme = ? WHERE username = ?",
        (theme_name, username)
    )

    conn.commit()
    conn.close()


# ==========================================
# "KEEP ME LOGGED IN" TOKEN
# ==========================================

import secrets


def create_remember_token(username):
    """Generates a fresh random token, stores it against this
    account, and returns it so it can be saved in a browser
    cookie. Re-opening the app with that cookie logs the
    account back in automatically, like WhatsApp does."""

    token = secrets.token_hex(32)

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )
    conn.execute("PRAGMA busy_timeout=30000")

    conn.execute(
        "UPDATE users SET remember_token = ? WHERE username = ?",
        (token, username)
    )

    conn.commit()
    conn.close()

    return token


def get_user_by_remember_token(token):

    if not token:
        return None

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )
    conn.execute("PRAGMA busy_timeout=30000")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username FROM users WHERE remember_token = ?",
        (token,)
    )

    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None


def clear_remember_token(username):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )
    conn.execute("PRAGMA busy_timeout=30000")

    conn.execute(
        "UPDATE users SET remember_token = NULL WHERE username = ?",
        (username,)
    )

    conn.commit()
    conn.close()


def save_photo(username, image_data):

    # ==========================================
    # CREATE PROFILE FOLDER
    # ==========================================

    os.makedirs(
        "profiles",
        exist_ok=True
    )

    # ==========================================
    # SAVE IMAGE FILE
    # ==========================================

    filename = os.path.abspath(
        os.path.join(
            "profiles",
            f"{username}.png"
        )
    )

    with open(
        filename,
        "wb"
    ) as f:

        f.write(image_data)

    # ==========================================
    # UPDATE DATABASE
    # ==========================================

    try:

        with sqlite3.connect(
            DB_PATH,
            timeout=30,
            check_same_thread=False
        ) as db:

            db.execute(
                "PRAGMA busy_timeout = 30000"
            )

            cursor = db.cursor()

            cursor.execute(
                """
                UPDATE users
                SET profile_pic = ?
                WHERE username = ?
                """,
                (
                    filename,
                    username
                )
            )

            db.commit()

        return True

    except sqlite3.OperationalError as e:

        if "database is locked" in str(e).lower():

            st.error(
                "⚠️ Database is busy. Please try again."
            )

            return False

        raise

    # ==========================================
    # VOICE MESSAGE
    # ==========================================

    if audio_bytes is not None:

        os.makedirs("voice_messages", exist_ok=True)

        filename = f"voice_{uuid.uuid4().hex}.wav"

        audio_path = os.path.join(
            "voice_messages",
            filename
        )

        # Save audio file
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)

        # Save path inside message column
        message = "**VOICE**:" + audio_path

    # ==========================================
    # SAVE MESSAGE
    # ==========================================

    cursor.execute(
        """
        INSERT INTO messages
        (sender, receiver, message, time)
        VALUES (?, ?, ?, datetime('now'))
        """,
        (
            sender,
            receiver,
            message
        )
    )

    conn.commit()
    conn.close()
    

def send_message( 
    sender,
    receiver,
    message,
    audio_bytes=None,
    reply_to=None
):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute(
        "PRAGMA busy_timeout=30000"
    )

    cursor = conn.cursor()
    # ==========================================
    # CHECK IF USER IS BLOCKED
    # ==========================================

    if (
        is_user_blocked(sender, receiver)
        or
        is_user_blocked(receiver, sender)
    ):
        conn.close()
        return

    # ==========================================
    # VOICE MESSAGE
    # ==========================================

    if audio_bytes is not None:

        os.makedirs(
            "voice_messages",
            exist_ok=True
        )

        filename = f"voice_{uuid.uuid4().hex}.wav"

        audio_path = os.path.abspath(
            os.path.join(
                "voice_messages",
                filename
            )
        )

        with open(
            audio_path,
            "wb"
        ) as f:

            f.write(audio_bytes)

        message = "**VOICE**:" + audio_path

    # ==========================================
    # SAVE MESSAGE
    # ==========================================

    cursor.execute(
        """
        INSERT INTO messages
        (
            sender,
            receiver,
            message,
            time,
            reply_to
        )
        VALUES
        (
            ?,
            ?,
            ?,
            datetime('now'),  
            ?
        )
        """,
        (
            sender,
            receiver,
            message,
            reply_to
        )
    )

    # ==========================================
    # BRING DELETED CHAT BACK TO CHAT LIST
    # ==========================================

    cursor.execute(
        """
        DELETE FROM deleted_chats
        WHERE username = ?
        AND friend = ?
        """,
        (
            sender,
            receiver
         )
    )

    conn.commit()
    conn.close()

    



def get_messages(a, b): 

    

    cursor.execute(
        """
        SELECT
            id,
            sender,
            message,
            time,
            reply_to
        FROM messages
        WHERE
            (sender = ? AND receiver = ?)
            OR
            (sender = ? AND receiver = ?)
        ORDER BY id
        """,
        (
            a,
            b,
            b,
            a
        )
    )

    return cursor.fetchall()



def add_status(user,text,file_data,
            file_type):

    cursor.execute(
        """
        INSERT INTO status(username,text,file,file_type)
        VALUES(?,?,?,?)
        """,
        (
            user,
            text,
            file_data,
            file_type
        )
    )

    conn.commit()



def get_status():

    cursor.execute(
        """
        SELECT id, username, text, file, file_type, time
        FROM status
        ORDER BY id DESC
        """
    )

    return cursor.fetchall()

def delete_status(status_id):

    cursor.execute(
        """
        DELETE FROM status
        WHERE id = ?
        """,
        (status_id,)
    )

    conn.commit()
    


def get_profile_pic(username):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT profile_pic
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    result = cursor.fetchone()

    conn.close()

    if result and result[0]:
        return result[0]

    return None


def save_photo(username, image_data):

    # Create profile folder
    os.makedirs("profiles", exist_ok=True)

    # Save image file
    filename = f"profiles/{username}.png"

    with open(filename, "wb") as f:
        f.write(image_data)

    # Open database
    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE users
        SET profile_pic = ?
        WHERE username = ?
        """,
        (filename, username)
    )

    conn.commit()
     

def delete_message(message_id):

    cursor.execute(
        "DELETE FROM messages WHERE id = ?",
        (message_id,)
    )

    conn.commit()
# ==================================================
# BLOCK USER
# ==================================================

def block_user(username, blocked_user):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA busy_timeout=30000")

    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO blocked_users
        (username, blocked_user)
        VALUES (?, ?)
    """, (
        username,
        blocked_user
    ))

    conn.commit()
    conn.close()

# ==================================================
# UNBLOCK USER
# ==================================================

def unblock_user(username, blocked_user):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA busy_timeout=30000")

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM blocked_users
        WHERE username = ?
        AND blocked_user = ?
    """, (
        username,
        blocked_user
    ))

    conn.commit()
    conn.close()

# ==================================================
# CHECK BLOCK STATUS
# ==================================================

def is_user_blocked(username, other_user):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT 1
        FROM blocked_users
        WHERE username = ?
        AND blocked_user = ?
        LIMIT 1
    """, (
        username,
        other_user
    ))

    result = cursor.fetchone()

    conn.close()

    return result is not None
    
# ==================================================
# DELETE CHAT FOR CURRENT USER
# ==================================================

def delete_chat_for_user(username, friend):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute(
        "PRAGMA busy_timeout=30000"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO deleted_chats
        (username, friend)
        VALUES (?, ?)
        """,
        (
            username,
            friend
        )
    )

    conn.commit()
    conn.close()


# ==================================================
# RESTORE CHAT WHEN NEW MESSAGE IS SENT
# ==================================================

def restore_chat_for_user(username, friend):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA busy_timeout=30000")

    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM deleted_chats
        WHERE username = ?
        AND friend = ?
    """, (
        username,
        friend
    ))

    conn.commit()
    conn.close()
    


# ==================================================
# CHECK IF CHAT WAS DELETED
# ==================================================

def is_chat_deleted(username, friend):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute(
        "PRAGMA busy_timeout=30000"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM deleted_chats
        WHERE username = ?
        AND friend = ?
        LIMIT 1
        """,
        (
            username,
            friend
        )
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None
# ==================================================
# GROUP FUNCTIONS
# ==================================================

def create_group(group_name, creator, members):

    group_name = group_name.strip()

    if not group_name:
        return None

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA busy_timeout=30000")

    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(groups)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    insert_columns = ["creator"]
    insert_values = [creator]

    # Always populate "name" (the column the rest of the app reads from)
    if "name" in existing_columns:
        insert_columns.insert(0, "name")
        insert_values.insert(0, group_name)

    # Some older databases have a legacy NOT NULL "group_name" column too —
    # populate it as well so the insert doesn't violate that constraint.
    if "group_name" in existing_columns:
        insert_columns.insert(0, "group_name")
        insert_values.insert(0, group_name)

    placeholders = ", ".join("?" for _ in insert_columns)
    columns_sql = ", ".join(insert_columns)

    cursor.execute(
        f"""
        INSERT INTO groups
        ({columns_sql})
        VALUES ({placeholders})
        """,
        tuple(insert_values)
    )

    group_id = cursor.lastrowid

    # Creator automatically becomes a member
    all_members = set(members)
    all_members.add(creator)

    for member in all_members:

        cursor.execute(
            """
            INSERT OR IGNORE INTO group_members
            (group_id, username)
            VALUES (?, ?)
            """,
            (
                group_id,
                member
            )
        )

    conn.commit()
    conn.close()

    return group_id


def add_group_members(group_id, usernames):
    """Adds one or more usernames to an existing group (no-op for anyone
    already a member, thanks to INSERT OR IGNORE)."""

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA busy_timeout=30000")

    cursor = conn.cursor()

    for member in usernames:

        cursor.execute(
            """
            INSERT OR IGNORE INTO group_members
            (group_id, username)
            VALUES (?, ?)
            """,
            (
                group_id,
                member
            )
        )

    conn.commit()
    conn.close()


def remove_group_member(group_id, username):
    """Removes a single username from a group's member list."""

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA busy_timeout=30000")

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM group_members
        WHERE group_id = ?
          AND username = ?
        """,
        (
            group_id,
            username
        )
    )

    conn.commit()
    conn.close()


def get_group_pic(group_id):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT group_pic
        FROM groups
        WHERE id = ?
        """,
        (group_id,)
    )

    result = cursor.fetchone()

    conn.close()

    if result and result[0]:
        return result[0]

    return None


def save_group_pic(group_id, image_data):

    os.makedirs("group_pics", exist_ok=True)

    filename = f"group_pics/group_{group_id}.png"

    with open(filename, "wb") as f:
        f.write(image_data)

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA busy_timeout=30000")

    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE groups
        SET group_pic = ?
        WHERE id = ?
        """,
        (filename, group_id)
    )

    conn.commit()
    conn.close()


def rename_group(group_id, new_name, username):
    new_name = new_name.strip()

    if not new_name:
        return False

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA busy_timeout=30000")
    cursor = conn.cursor()

    # Only the group creator can rename the group
    cursor.execute(
        """
        SELECT creator
        FROM groups
        WHERE id = ?
        """,
        (group_id,)
    )

    result = cursor.fetchone()

    if not result:
        conn.close()
        return False

    creator = result[0]

    if creator != username:
        conn.close()
        return False

    cursor.execute("PRAGMA table_info(groups)")
    existing_columns = [row[1] for row in cursor.fetchall()]

    set_clauses = ["name = ?"]
    values = [new_name]

    if "group_name" in existing_columns:
        set_clauses.append("group_name = ?")
        values.append(new_name)

    values.append(group_id)

    cursor.execute(
        f"""
        UPDATE groups
        SET {", ".join(set_clauses)}
        WHERE id = ?
        """,
        tuple(values)
    )

    conn.commit()
    conn.close()

    return True


def get_user_groups(username):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA busy_timeout=30000")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            g.id,
            g.name,
            g.creator
        FROM groups g
        INNER JOIN group_members gm
            ON g.id = gm.group_id
        WHERE gm.username = ?
        ORDER BY g.id DESC
        """,
        (username,)
    )

    groups = cursor.fetchall()

    conn.close()

    return groups


def get_group_members(group_id):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT username
        FROM group_members
        WHERE group_id = ?
        ORDER BY username
        """,
        (group_id,)
    )

    members = [
        row[0]
        for row in cursor.fetchall() 
    ]

    conn.close()

    return members


def get_group_name(group_id):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )
    conn.execute("PRAGMA busy_timeout=30000")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT name
        FROM groups
        WHERE id = ?
        """,
        (group_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result[0] if result else "Group"


def send_group_message(
    group_id,
    sender,
    message,
    reply_to=None
):

    if not message:
        return

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA busy_timeout=30000")

    cursor = conn.cursor()

    # Make sure sender is actually a group member
    cursor.execute(
        """
        SELECT 1
        FROM group_members
        WHERE group_id = ?
        AND username = ?
        LIMIT 1
        """,
        (
            group_id,
            sender
        )
    )

    if cursor.fetchone() is None:
        conn.close()
        return

    cursor.execute(
        """
        INSERT INTO group_messages
        (
            group_id,
            sender,
            message,
            time,
            reply_to
        )
        VALUES (?, ?, ?, datetime('now'), ?)
        """,
        (
            group_id,
            sender,
            message,
            reply_to
        )
    )

    conn.commit()
    conn.close()


def get_group_messages(group_id):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT
            id,
            sender,
            message,
            time,
            reply_to
        FROM group_messages
        WHERE group_id = ?
        ORDER BY id
        """,
        (group_id,)
    )

    messages = cursor.fetchall()

    conn.close()

    return messages

def delete_group(group_id):
    try:
        # Delete group messages
        cursor.execute(
            "DELETE FROM group_messages WHERE group_id = ?",
            (group_id,)
        )

        # Delete group members
        cursor.execute(
            "DELETE FROM group_members WHERE group_id = ?",
            (group_id,)
        )

        # Delete the group
        cursor.execute(
            "DELETE FROM groups WHERE id = ?",
            (group_id,)
        )

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        print("Delete group error:", e)
        return False

# =========================
# "KEEP ME LOGGED IN" COOKIE
# =========================

# NOTE: change this password to your own secret value (e.g. load
# it from an environment variable) before putting this app in
# front of real users -- anyone who has this password can forge
# a login cookie.
_COOKIE_PASSWORD = "please-change-this-mychat-cookie-secret"

cookies = None

if _COOKIES_AVAILABLE:

    cookies = EncryptedCookieManager(
        prefix="mychat/",
        password=_COOKIE_PASSWORD
    )

    if not cookies.ready():
        st.stop()

# =========================
# SESSION
# =========================

if "user" not in st.session_state:
    st.session_state.user = None

# ==========================================
# AUTO-LOGIN FROM "KEEP ME LOGGED IN" COOKIE
# (only runs once, when there's no active session yet)
# ==========================================

if (
    st.session_state.user is None
    and cookies is not None
    and cookies.get("remember_token")
):
    _auto_user = get_user_by_remember_token(
        cookies.get("remember_token")
    )

    if _auto_user:
        st.session_state.user = _auto_user
        st.session_state["saved_theme"] = get_saved_theme(_auto_user)
        # Re-run once now that we know the theme, so the CSS
        # block (which runs earlier in the script) picks up the
        # correct theme immediately instead of flashing "Light"
        # first. Safe from looping: on the next run st.session_state.user
        # is already set, so this block won't fire again.
        st.rerun()


# =========================
# LOGIN / REGISTER
# =========================

if st.session_state.user is None:

    st.title("💬 MyChat")

    option = st.radio(
        "Choose",
        ["Login", "Register"]
    )

    # =========================
    # REGISTER
    # =========================

    if option == "Register":

        username = st.text_input("Username")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Register"):

            if not username:
                st.error("⚠️ Username is required.")

            elif not email:
                st.error("⚠️ Email is required.")

            elif not phone:
                st.error("⚠️ Phone number is required.")

            elif not password:
                st.error("⚠️ Password is required.")

            elif register(
                username,
                email,
                phone,
                password
            ):

                st.success(
                    "✅ Account created successfully!"
                )

            else:

                st.error(
                    "❌ Email or username already exists."
                )

    # =========================
    # LOGIN
    # =========================

    else:

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        keep_logged_in = st.checkbox(
            "Keep me logged in on this device",
            value=True,
            key="keep_logged_in_checkbox"
        )

        if st.button("Login"):

            user = login(
                email,
                password
            )

            if user is not None:

                st.session_state.user = user

                # Restore this account's saved theme instead of
                # showing the default one.
                st.session_state["saved_theme"] = get_saved_theme(user)

                # "Keep me logged in": save a token both in the
                # database and in a browser cookie, so re-opening
                # the app logs this account back in automatically.
                if keep_logged_in and cookies is not None:

                    token = create_remember_token(user)

                    cookies["remember_token"] = token
                    cookies.save()

                st.rerun()

            else:

                st.error(
                    "❌ Invalid email or password."
                )

    st.stop()
# =========================
# GET OTHER USERS
# =========================

def get_users(user):

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute(
        "PRAGMA busy_timeout=30000"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT username
        FROM users
        WHERE username != ?
        ORDER BY username
        """,
        (user,)
    )

    users = [
        row[0]
        for row in cursor.fetchall()
    ]

    conn.close()

    return users


def get_recent_chats(user):

    # Returns only the people this account has actually
    # exchanged at least one message with, most-recent first.
    # This is what the "Chat list" should show by default --
    # NOT the full user directory (that's what get_users() is
    # for, and it's only used when the person searches).

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute(
        "PRAGMA busy_timeout=30000"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT other_user
        FROM (
            SELECT id, receiver AS other_user
            FROM messages
            WHERE sender = ?
              AND receiver IS NOT NULL
              AND receiver != ''
              AND receiver != ?
            UNION ALL
            SELECT id, sender AS other_user
            FROM messages
            WHERE receiver = ?
              AND sender IS NOT NULL
              AND sender != ''
              AND sender != ?
        )
        GROUP BY other_user
        ORDER BY MAX(id) DESC
        """,
        (user, user, user, user)
    )

    people = [
        row[0]
        for row in cursor.fetchall()
        if row[0]
    ]

    conn.close()

    return people


# =========================
# ONLINE / LAST SEEN
# =========================

from datetime import datetime, timezone


def to_local_time_str(raw_time):
    """Messages/last_active are stored in UTC (SQLite's
    datetime('now') / CURRENT_TIMESTAMP). Convert to the local
    system timezone before showing it, otherwise timestamps look
    "wrong" by the UTC offset (e.g. a message sent right now shows
    an hour that isn't the current time)."""

    if not raw_time:
        return raw_time

    try:
        dt_utc = datetime.strptime(
            str(raw_time),
            "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=timezone.utc)

        return dt_utc.astimezone().strftime("%Y-%m-%d %H:%M:%S")

    except ValueError:
        return raw_time


def render_copy_button(key, text_to_copy, toast_text="📋 Copied"):
    """A small reusable '📋 Copy' button that copies text_to_copy to
    the clipboard via the browser's clipboard API. Used for both
    text messages and attachments (voice/image/video/file), in both
    the 1-on-1 and group chats."""

    if st.button(
        "📋",
        key=key,
        help="Copy"
    ):
        components.html(
            f"""
            <script>
            navigator.clipboard.writeText({json.dumps(str(text_to_copy))});
            </script>
            """,
            height=0
        )
        st.toast(toast_text)


def render_message_actions_menu(
    key_prefix,
    reply_state_key,
    reply_value,
    forward_id_key,
    forward_content_key,
    forward_content,
    copy_text,
    copy_toast,
    delete_action
):
    """A single '⋮' button per message that opens a small popover
    with Reply / Forward / Copy / Delete inside it -- used for every
    message type (text, voice, image, video, file) in both the
    1-on-1 and group chats, so the message row itself stays clean.

    delete_action must be a zero-argument callable that performs the
    actual deletion (DB row + any file on disk). This function calls
    st.rerun() itself after each action, so delete_action should not
    call st.rerun() on its own.
    """

    with st.popover(
        "⋮",
        key=f"{key_prefix}_menu"
    ):

        if st.button(
            "↩️ Reply",
            key=f"{key_prefix}_reply_btn",
            use_container_width=True
        ):
            st.session_state[reply_state_key] = reply_value
            st.rerun()

        if st.button(
            "↗️ Forward",
            key=f"{key_prefix}_forward_btn",
            use_container_width=True
        ):
            st.session_state[forward_id_key] = reply_value
            st.session_state[forward_content_key] = forward_content
            st.rerun()

        if st.button(
            "📋 Copy",
            key=f"{key_prefix}_copy_btn",
            use_container_width=True
        ):
            components.html(
                f"""
                <script>
                navigator.clipboard.writeText({json.dumps(str(copy_text))});
                </script>
                """,
                height=0
            )
            st.toast(copy_toast)

        if st.button(
            "🗑️ Delete",
            key=f"{key_prefix}_delete_btn",
            use_container_width=True
        ):
            delete_action()
            st.rerun()


def touch_last_active(username):
    """Marks a user as active right now. Call this once per script run
    while the user is logged in, so their presence stays up to date."""

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA busy_timeout=30000")

    conn.execute(
        """
        UPDATE users
        SET last_active = CURRENT_TIMESTAMP
        WHERE username = ?
        """,
        (username,)
    )

    conn.commit()
    conn.close()


def get_presence_status(username):
    """Returns a display string like '🟢 Online' or 'last seen 10:42 AM',
    respecting that user's own privacy toggles. Returns '' if both
    are turned off."""

    conn = sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )

    conn.execute("PRAGMA busy_timeout=30000")

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT last_active, show_online_status, show_last_seen
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    row = cursor.fetchone()
    conn.close()

    if not row:
        return ""

    last_active_raw, show_online, show_last_seen = row

    show_online = True if show_online is None else bool(show_online)
    show_last_seen = True if show_last_seen is None else bool(show_last_seen)

    if not last_active_raw:
        return ""

    try:
        last_active = datetime.strptime(
            str(last_active_raw),
            "%Y-%m-%d %H:%M:%S"
        ).replace(tzinfo=timezone.utc)
    except ValueError:
        return ""

    now_utc = datetime.now(timezone.utc)

    seconds_ago = (
        now_utc - last_active
    ).total_seconds()

    ONLINE_THRESHOLD_SECONDS = 60

    if show_online and seconds_ago <= ONLINE_THRESHOLD_SECONDS:
        return "🟢 Online"

    if show_last_seen:

        # last_active is stored in UTC (SQLite's CURRENT_TIMESTAMP).
        # Convert it to the local system timezone before formatting,
        # otherwise the displayed clock time is off by the UTC
        # offset (e.g. showing a UTC hour instead of the real one).
        last_active_local = last_active.astimezone()
        today_local = datetime.now().astimezone().date()

        if last_active_local.date() == today_local:
            time_str = last_active_local.strftime("%I:%M %p").lstrip("0")
            return f"last seen today at {time_str}"
        else:
            date_str = last_active_local.strftime("%d %b, %I:%M %p").lstrip("0")
            return f"last seen {date_str}"

    return ""



# =========================
# MAIN APP
# =========================

user = st.session_state.user

touch_last_active(user)

# Re-run the app periodically (while logged in) so your own
# "Online" status stays fresh for others, and so a friend's
# "last seen" text updates on your screen even if you're just
# sitting on the chat without clicking anything.
if _AUTOREFRESH_AVAILABLE:
    st_autorefresh(
        interval=20_000,
        key="presence_autorefresh"
    )

# =========================
# SIDEBAR
# =========================

st.sidebar.title("💬 MyChat")

st.sidebar.write(
    "Logged in:",
    user
)


# =========================
# PROFILE PICTURE + BIO
# =========================

conn = sqlite3.connect("chat.db")
cursor = conn.cursor()

cursor.execute(
    """
    SELECT profile_pic, bio
    FROM users
    WHERE username = ?
    """,
    (user,)
)

profile_data = cursor.fetchone()




# Profile picture
if profile_data and profile_data[0]:

    profile_pic = profile_data[0]

    if os.path.exists(profile_pic):

        st.sidebar.image(
            profile_pic,
            width=120
        )

    else:
        st.sidebar.write("👤")

else:
    st.sidebar.write("👤")


# Bio
if profile_data and profile_data[1]:

    st.sidebar.caption(
        profile_data[1]
    )

else:

    st.sidebar.caption(
        "No bio added"
    )


st.sidebar.divider()


# =========================
# MENU
# =========================

page = st.sidebar.selectbox(
    "Menu",
    [
        "Chats",
        "Status",
        "Groups",
        "Profile",
        "Settings"
    ]
)

# ==================================================
# AUTO-COLLAPSE THE SIDEBAR AFTER PICKING A MENU ITEM
# ==================================================

if "_prev_menu_page" not in st.session_state:
    st.session_state["_prev_menu_page"] = page

if page != st.session_state["_prev_menu_page"]:

    st.session_state["_prev_menu_page"] = page

    components.html(
        """
        <script>
        setTimeout(function() {
            const doc = window.parent.document;
            const collapseBtn =
                doc.querySelector('[data-testid="stSidebarCollapseButton"] button') ||
                doc.querySelector('[data-testid="stSidebarCollapseButton"]') ||
                doc.querySelector('[data-testid="stBaseButton-headerNoPadding"]') ||
                doc.querySelector('button[kind="header"]');
            if (collapseBtn) {
                collapseBtn.click();
            }
        }, 150);
        </script>
        """,
        height=0
    )


# =========================
# LOGOUT
# =========================

if st.sidebar.button("Logout"):

    # Invalidate the "keep me logged in" token, both in the
    # database and in the browser cookie, so logging out actually
    # logs out -- otherwise the cookie would just log this
    # account back in on the next visit.
    clear_remember_token(user)

    if cookies is not None:
        cookies["remember_token"] = ""
        cookies.save()

    # Clear EVERY piece of session state (selected chat/group,
    # reply/forward state, attachment toggles, highlight flags,
    # etc.) so the next account to log in on this same browser
    # tab starts completely fresh and never inherits the
    # previous account's open chat, group, or UI state.
    st.session_state.clear()

    st.session_state.user = None
    st.rerun()



# =========================
# PROFILE
# =========================

if page == "Profile":

    st.header("👤 Profile")

    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()

    # Get current profile data
    cursor.execute(
        "SELECT profile_pic, bio FROM users WHERE username = ?",
        (user,)
    )

    profile_data = cursor.fetchone()

    

    # =========================
    # PROFILE PICTURE
    # =========================

    st.subheader("Profile Picture")

    # Display saved profile picture
    if profile_data and profile_data[0]:

        st.image(
            profile_data[0],
            width=150
        )

    else:

        st.info("No profile picture")


    photo = st.file_uploader(
        "Change profile picture",
        type=["png", "jpg", "jpeg"],
        key="profile_photo"
    )


    # Save uploaded picture
    if photo:

        save_photo(
            user,
            photo.read()
        )

        st.success("Photo saved")
        st.rerun()


    # Remove profile picture
    if st.button(
        "🗑️ Remove Profile Picture",
        key="remove_profile_photo"
    ):

        conn = sqlite3.connect("chat.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users
            SET profile_pic = NULL
            WHERE username = ?
            """,
            (user,)
        )

        conn.commit()
        

        st.success("Profile picture removed")
        st.rerun()


    # =========================
    # BIO
    # =========================

    bio = st.text_area(
        "Bio",
        key="profile_bio"
     )

    conn = sqlite3.connect("chat.db")
    cursor = conn.cursor()

    cursor.execute(
             """
             UPDATE users
             SET bio = ?
             WHERE username = ?
             """,
             (bio, user)
       )

    conn.commit()
    

     
    


    # =========================
    # SAVE PROFILE
    # =========================
 
    if st.button(
        "💾 Save Bio",
        key="save_profile"
    ):

        conn = sqlite3.connect("chat.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users
            SET bio = ?
            WHERE username = ?
            """,
            (bio, user)
        )

        conn.commit()
        

        st.success("✅ Bio saved successfully")

    # =========================
    # REMOVE BIO
    # =========================

    if st.button(
        "🗑️ Remove Bio",
        key="remove_bio"
    ):

        conn = sqlite3.connect("chat.db")
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE users
            SET bio = NULL
            WHERE username = ?
            """,
            (user,)
        )

        conn.commit()
        

        st.success("Bio removed")
        st.rerun()


    st.stop()
    
# =========================
# STATUS
# =========================

if page == "Status":

    st.header("📸 Status")

    # -------------------------
    # CREATE STATUS
    # -------------------------

    text = st.text_area(
        "Write status"
    )

    media = st.file_uploader(
        "Upload Image or Video",
        type=[
            "png",
            "jpg",
            "jpeg",
            "mp4",
            "mov"
        ]
    )

    file_data = None
    file_type = None

    if media:

        file_data = media.read()

        if media.type.startswith("image"):

            file_type = "image"

            st.image(
                file_data,
                caption="Preview",
                width=300
            )

        elif media.type.startswith("video"):

            file_type = "video"

            st.video(
                file_data
            )

    # -------------------------
    # POST STATUS
    # -------------------------

    if st.button("📤 Post Status"):

        if not text and file_data is None:

            st.warning(
                "Write something or upload media"
            )

        else:

            add_status(
                user,
                text,
                file_data,
                file_type
            )

            st.success(
                "Status added"
            )

            st.rerun()

    st.divider()

    # -------------------------
    # RECENT STATUS
    # -------------------------

    st.subheader(
        "Recent Status"
    )

    statuses = get_status()

    for status in statuses:

            # IMPORTANT:
            # get_status() returns 6 values
            status_id, u, t, file, file_type, time = status

            st.write(
                "👤 " + str(u)
            )

            if t:

                st.write(t)

            if file:

                if file_type == "image":

                    st.image(
                        file,
                        width=300
                    )

                elif file_type == "video":

                    st.video(
                        file
                    )

            st.caption(
                time
            )

            # -------------------------
            # DELETE OWN STATUS
            # -------------------------

            if str(u).strip() == str(user).strip():

                if st.button(
                    "🗑️ Delete",
                    key=f"delete_status_{status_id}"
                ):

                    delete_status(
                        status_id
                    )

                    st.success(
                        "Status deleted"
                    )

                    st.rerun()

            st.divider()

    st.stop()



# =========================
# CALLS
# =========================

if page=="Calls":

    st.header("📞 Calls")


    people=get_users(user)


    if people:

        person=st.selectbox(
            "User",
            people
        )


        typ=st.radio(
            "Type",
            [
                "Voice",
                "Video"
            ]
        )


        if st.button("Call"):

            add_call(
                user,
                person,
                typ
            )


    st.subheader(
        "History"
    )


    for c in get_calls(user):

        st.write(c)


    st.stop()

# =========================================================
# CHAT WALLPAPERS
# =========================================================

chat_wallpapers = {

    "Floating Glow": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(0, 180, 255, 0.25),
                transparent 35%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(150, 50, 255, 0.15),
                transparent 35%
            ),
            #101827;
    """,

    "Neon Blue": """
        background:
            radial-gradient(
                circle at center,
                rgba(0, 120, 255, 0.25),
                #020617 70%
            );
    """,

    "Purple Galaxy": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(168, 85, 247, 0.85),
                transparent 30%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(236, 72, 53, 0.60),
                transparent 100%
            ),
            #0b0614;
    """,

    "Ocean Waves": """
        background:
            linear-gradient(
                135deg,
                #003b5c,
                #006994,
                #001f3f
            );
    """,

    "Sunset": """
        background:
            linear-gradient(
                135deg,
                #ff7e5f,
                #feb47b,
                #7b4397
            );
    """,

    "Minimal": """
        background: #f5f5f5;
    """,

    "WhatsApp Style": """
        background-color: #efeae2;
        background-image:
            radial-gradient(
                rgba(0,0,0,0.05) 1px,
                transparent 1px
            );
        background-size: 20px 20px;
    """,
    # =========================================================
    # NEW ATTRACTIVE LIGHT WALLPAPERS
    # =========================================================

    "🌌 Aurora Dream": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(139, 233, 255, 0.35),
                transparent 35%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(192, 132, 252, 0.25),
                transparent 35%
            ),
            linear-gradient(
                135deg,
                #eef7ff,
                #f5efff
            );
    """,

    "🫧 Crystal Bubble": """
        background:
            radial-gradient(
                circle at 25% 25%,
                rgba(255, 255, 255, 0.75),
                transparent 18%
            ),
            radial-gradient(
                circle at 75% 75%,
                rgba(185, 234, 255, 0.40),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #e8faff,
                #f2f7ff
            );
    """,

    "🌸 Sakura Glow": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(255, 183, 213, 0.30),
                transparent 30%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(255, 214, 232, 0.35),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #fff1f6,
                #fff8fb
            );
    """,

    "💎 Crystal Mist": """
        background:
            radial-gradient(
                circle at 30% 20%,
                rgba(185, 234, 255, 0.40),
                transparent 30%
            ),
            radial-gradient(
                circle at 75% 75%,
                rgba(217, 199, 255, 0.30),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #eefaff,
                #f4efff
            );
    """,

    "🌅 Golden Sunset": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(255, 209, 102, 0.35),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #fff3d6,
                #ffe9dc,
                #f4e4ff
            );
    """,

    "🦋 Dreamy Sky": """
        background:
            radial-gradient(
                circle at 20% 30%,
                rgba(143, 211, 255, 0.35),
                transparent 32%
            ),
            radial-gradient(
                circle at 80% 70%,
                rgba(190, 220, 255, 0.25),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #eaf8ff,
                #edf3ff
            );
    """,

    "🌊 Ocean Pearl": """
        background:
            radial-gradient(
                circle at 75% 25%,
                rgba(125, 211, 252, 0.35),
                transparent 32%
            ),
            radial-gradient(
                circle at 20% 80%,
                rgba(103, 232, 249, 0.20),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #e7f9ff,
                #eaf4ff
            );
    """,

    "🌙 Moonlit Cloud": """
        background:
            radial-gradient(
                circle at 70% 20%,
                rgba(255, 255, 255, 0.70),
                transparent 25%
            ),
            radial-gradient(
                circle at 20% 80%,
                rgba(180, 195, 220, 0.20),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #e8ecf8,
                #dfe8f5
            );
    """,

    "💜 Purple Silk": """
        background:
            radial-gradient(
                circle at 25% 25%,
                rgba(196, 181, 253, 0.35),
                transparent 32%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(221, 214, 254, 0.25),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #f3edff,
                #ebe5ff
            );
    """,

    "🩵 Arctic Pearl": """
        background:
            radial-gradient(
                circle at 30% 20%,
                rgba(255, 255, 255, 0.80),
                transparent 25%
            ),
            radial-gradient(
                circle at 75% 75%,
                rgba(165, 243, 252, 0.25),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #e8fbff,
                #edf8ff
            );
    """,

    "🌷 Rose Silk": """
        background:
            radial-gradient(
                circle at 20% 30%,
                rgba(253, 164, 175, 0.30),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #fff0f4,
                #ffe8ef
            );
    """,

    "🍑 Peach Silk": """
        background:
            radial-gradient(
                circle at 75% 25%,
                rgba(253, 186, 116, 0.30),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #fff1e8,
                #ffebe3
            );
    """,

    "🌿 Emerald Mist": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(110, 231, 183, 0.35),
                transparent 32%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(167, 243, 208, 0.20),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #ecfff6,
                #e7f8f0
            );
    """,

    "✨ Champagne Glow": """
        background:
            radial-gradient(
                circle at 50% 20%,
                rgba(253, 230, 138, 0.40),
                transparent 32%
            ),
            radial-gradient(
                circle at 20% 80%,
                rgba(255, 237, 180, 0.25),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #fff9e8,
                #fff3d8
            );
    """,

    "☁️ Cloud Velvet": """
        background:
            radial-gradient(
                circle at 30% 30%,
                rgba(255, 255, 255, 0.80),
                transparent 25%
            ),
            radial-gradient(
                circle at 75% 70%,
                rgba(255, 255, 255, 0.50),
                transparent 28%
            ),
            #f1f5f9;
    """,

    "🪻 Lavender Silk": """
        background:
            radial-gradient(
                circle at 75% 25%,
                rgba(196, 181, 253, 0.35),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #f6f0ff,
                #eee7ff
            );
    """,

    "🩷 Blush Pearl": """
        background:
            radial-gradient(
                circle at 25% 25%,
                rgba(249, 168, 212, 0.35),
                transparent 30%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(255, 210, 230, 0.25),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #fff1f7,
                #ffeaf3
            );
    """,

    "🌈 Prism Glow": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(249, 168, 212, 0.30),
                transparent 28%
            ),
            radial-gradient(
                circle at 80% 25%,
                rgba(147, 197, 253, 0.30),
                transparent 28%
            ),
            radial-gradient(
                circle at 50% 90%,
                rgba(134, 239, 172, 0.25),
                transparent 30%
            ),
            #f7f9ff;
    """,

    "💫 Stardust Mist": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(196, 181, 253, 0.30),
                transparent 30%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(147, 197, 253, 0.30),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #f3f0ff,
                #eef5ff
            );
    """,

    "🌤 Heavenly Sky": """
        background:
            radial-gradient(
                circle at 70% 20%,
                rgba(255, 255, 255, 0.80),
                transparent 25%
            ),
            linear-gradient(
                135deg,
                #e8f7ff,
                #f5fbff
            );
    """,

    "🧊 Frozen Glass": """
        background:
            radial-gradient(
                circle at 25% 25%,
                rgba(255, 255, 255, 0.70),
                transparent 25%
            ),
            radial-gradient(
                circle at 75% 75%,
                rgba(186, 230, 253, 0.25),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #e8faff,
                #e6f0ff
            );
    """,

    "🌺 Floral Haze": """
        background:
            radial-gradient(
                circle at 20% 25%,
                rgba(251, 207, 232, 0.35),
                transparent 30%
            ),
            radial-gradient(
                circle at 80% 75%,
                rgba(244, 191, 211, 0.20),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #fff3f8,
                #fff0f5
            );
    """,

    "🍃 Jade Whisper": """
        background:
            radial-gradient(
                circle at 75% 25%,
                rgba(134, 239, 172, 0.30),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #effff5,
                #e9f8f0
            );
    """,

    "🌙 Midnight Pearl": """
        background:
            radial-gradient(
                circle at 70% 25%,
                rgba(196, 181, 253, 0.25),
                transparent 32%
            ),
            radial-gradient(
                circle at 20% 80%,
                rgba(96, 165, 250, 0.15),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #20253a,
                #171b2e
            );
    """,

    "💙 Sapphire Mist": """
        background:
            radial-gradient(
                circle at 25% 25%,
                rgba(96, 165, 250, 0.35),
                transparent 32%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(147, 197, 253, 0.20),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #eaf4ff,
                #e4efff
            );
    """,

    "🪞 Silver Glass": """
        background:
            radial-gradient(
                circle at 25% 25%,
                rgba(255, 255, 255, 0.80),
                transparent 25%
            ),
            radial-gradient(
                circle at 75% 75%,
                rgba(203, 213, 225, 0.25),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #f3f5f7,
                #e8edf2
            );
    """,

    "🌅 Coral Horizon": """
        background:
            radial-gradient(
                circle at 80% 20%,
                rgba(251, 113, 133, 0.30),
                transparent 30%
            ),
            radial-gradient(
                circle at 20% 80%,
                rgba(253, 186, 116, 0.20),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #fff0e8,
                #ffe7e0
            );
    """,

    "🫧 Aqua Pearl": """
        background:
            radial-gradient(
                circle at 25% 25%,
                rgba(103, 232, 249, 0.35),
                transparent 32%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(125, 211, 252, 0.20),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #e8fffd,
                #e8f8ff
            );
    """,

    "🌼 Vanilla Glow": """
        background:
            radial-gradient(
                circle at 70% 25%,
                rgba(253, 230, 138, 0.35),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #fffbed,
                #fff6dc
            );
    """,

    "🔮 Mystic Glass": """
        background:
            radial-gradient(
                circle at 20% 20%,
                rgba(167, 139, 250, 0.35),
                transparent 30%
            ),
            radial-gradient(
                circle at 80% 80%,
                rgba(103, 232, 249, 0.25),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #f2edff,
                #eafaff
            );
    """,
}
# ========================= 

# SETTINGS

# =========================

if page == "Settings":


  st.header("⚙️ Settings")

  option = st.selectbox(
    "Settings",
    [
        "Appearance",
        "Chat Wallpaper",
        "Privacy",
        "Notifications",
        "Security",
        "About"
    ],
    key="settings_option"
)

  # =========================
  # APPEARANCE
  # =========================

  if option == "Appearance":

    st.header("🎨 Appearance")

    if "theme" not in st.session_state:
        st.session_state.theme = "Light"

    theme = st.selectbox(
        "Choose Theme",
        [
            "Light",
            "Dark",
            "WhatsApp Green",
            "Ocean Blue",
            "Midnight Purple",
            "Rose Pink",
            "Sunset Orange",
            "Forest Green",
            "Coffee Brown",
            
        ],
        key="theme"
    ) 

    colors = themes[theme]

    st.markdown(
        f"""
        <style>

        .stApp {{
            background-color: {colors["bg"]};
            color: {colors["text"]};
        }}

        .stApp p,
        .stApp span,
        .stApp label,
        .stApp h1,
        .stApp h2,
        .stApp h3,
        .stApp h4 {{
            color: {colors["text"]};
        }}

        section[data-testid="stSidebar"] {{
            background-color: {colors["secondary"]};
        }}

        .stButton > button {{
            background-color: {colors["accent"]};
            color: white;
            border: none;
            border-radius: 8px;
        }}

        .stButton > button:hover {{
            opacity: 0.85;
        }}

        .stTextInput input,
        .stTextArea textarea {{
            background-color: {colors["secondary"]};
            color: {colors["text"]};
        }}

        div[data-baseweb="select"] > div {{
            background-color: {colors["secondary"]};
            color: {colors["text"]};
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

    st.success(
        f"Current Theme: {theme}"
    )     
     
       # -------------------------
       # SAVE BUTTON
       # -------------------------

    if st.button(
       "💾 Save Theme",
       key="save_theme_button"
       ):

        # Save the selected theme for THIS session...
        st.session_state["saved_theme"] = theme

        # ...and permanently, in the database, so it's still
        # there the next time this account logs in (instead of
        # resetting to the default theme every time).
        save_theme_for_user(user, theme)

        st.success(
          f"✅ {theme} theme saved successfully!"
        )
  
  # =========================================================
  # CHAT WALLPAPER SETTING
  # =========================================================

  if option == "Chat Wallpaper":
      st.subheader("🖼️ Chat Wallpaper")

      wallpaper_options = [
        "Floating Glow",
        "Dark Grid",
        "Neon Blue",
        "Purple Galaxy",
        "Ocean Waves",
        "Sunset",
        "Minimal",
        "WhatsApp Style",
        "🌌 Aurora Dream",
        "🫧 Crystal Bubble",
        "🌸 Sakura Glow",
        "💎 Crystal Mist",
        "🌅 Golden Sunset",
        "🦋 Dreamy Sky",
        "🌊 Ocean Pearl",
        "🌙 Moonlit Cloud",
        "💜 Purple Silk",
        "🩵 Arctic Pearl",
        "🌷 Rose Silk",
        "🍑 Peach Silk",
        "🌿 Emerald Mist",
        "✨ Champagne Glow",
        "☁️ Cloud Velvet",
        "🪻 Lavender Silk",
        "🩷 Blush Pearl",
        "🌈 Prism Glow",
        "💫 Stardust Mist",
        "🌤 Heavenly Sky",
        "🧊 Frozen Glass",
        "🌺 Floral Haze",
        "🍃 Jade Whisper",
        "🌙 Midnight Pearl",
        "💙 Sapphire Mist",
        "🪞 Silver Glass",
        "🌅 Coral Horizon",
        "🫧 Aqua Pearl",
        "🌼 Vanilla Glow",
        "🔮 Mystic Glass"
      ]
      # Current saved wallpaper
      current_wallpaper = st.session_state.get(
        "chat_wallpaper",
        "Floating Glow"
      )
      if current_wallpaper not in wallpaper_options:
          current_wallpaper = "Floating Glow"
          st.session_state["chat_wallpaper"] = current_wallpaper

      selected_wallpaper = st.selectbox(
        "Choose your chat wallpaper",
        wallpaper_options,
        index=wallpaper_options.index(current_wallpaper),
        key="chat_wallpaper_select"
      )

      if st.button("💾 Save Chat Wallpaper", key="save_chat_wallpaper"):

        st.session_state["chat_wallpaper"] = selected_wallpaper

        st.success(
            f"Chat wallpaper changed to {selected_wallpaper}"
        )

        st.rerun()
  # =========================
  # PRIVACY
  # =========================

  elif option == "Privacy":

        st.header("🔒 Privacy")

        # ----------------------------------------------------
        # Load online/last-seen prefs from the DATABASE
        # (so other users can actually respect them), and keep
        # the rest of the settings in session_state as before.
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT show_online_status, show_last_seen
            FROM users
            WHERE username = ?
            """,
            (user,)
        )
        _row = cursor.fetchone()
        _db_online_default = bool(_row[0]) if _row and _row[0] is not None else True
        _db_last_seen_default = bool(_row[1]) if _row and _row[1] is not None else True

        if "privacy_settings" not in st.session_state:
          st.session_state["privacy_settings"] = {
            "online_status": _db_online_default,
            "last_seen": _db_last_seen_default,
            "profile_photo": True,
            "read_receipts": True
        }

        privacy = st.session_state["privacy_settings"]

        online = st.toggle(
            "Show Online Status",
            value=privacy["online_status"],
            key="privacy_online"
        )

        last_seen = st.toggle(
            "Show Last Seen",
            value=privacy["last_seen"],
            key="privacy_last_seen"
        )

        profile_photo = st.toggle(
            "Show Profile Picture",
            value=privacy["profile_photo"],
            key="privacy_profile_photo"
        )

        read_receipts = st.toggle(
            "Read Receipts",
            value=privacy["read_receipts"],
            key="privacy_read_receipts"
        )

        if st.button("Save Privacy",key="save_privacy"):
          st.session_state["privacy_settings"] = {
            "online_status": online,
            "last_seen": last_seen,
            "profile_photo": profile_photo,
            "read_receipts": read_receipts
        }

          cursor.execute(
              """
              UPDATE users
              SET show_online_status = ?, show_last_seen = ?
              WHERE username = ?
              """,
              (int(online), int(last_seen), user)
          )
          conn.commit()

          st.success(
                "Privacy settings saved."
              )
          st.rerun()

  # ------------------------
  # NOTIFICATIONS
  # ------------------------
  elif option == "Notifications":

        st.toggle("Message Notifications", value=True)

        st.toggle("Group Notifications", value=True)

        st.toggle("Call Notifications", value=True)

        st.toggle("Sound", value=True)

        st.toggle("Vibration", value=True)

        st.divider()

        st.caption(
            "Desktop notifications show a popup from your browser "
            "even when this tab isn't active. Your browser will ask "
            "you to allow this."
        )

        if st.button("🔔 Enable Desktop Notifications"):
            request_desktop_notification_permission()
            st.success(
                "If your browser didn't already ask, check the address "
                "bar for a notification permission prompt."
            )

  # ------------------------
  # SECURITY
  # ------------------------
  elif option == "Security":

          st.header("🔐 Security Settings")

    

  # ---------------------------------
  # Login Alerts
  # ---------------------------------
  login_alerts = st.checkbox(
        "Login Alerts",
        key="login_alerts"
    )

  if login_alerts:

        st.success(
            "🔔 Login Alerts Enabled"
        )

    

  # ------------------------
  # ABOUT
  # ------------------------
  if option == "About":

          st.subheader("About MyChat")

          st.write("Version : 1.0")

          st.write("Developed using Streamlit")


# =========================
# SELECTED CHAT
# =========================

if "selected_friend" not in st.session_state:
    st.session_state["selected_friend"] = None

# ==================================================
# SELECTED GROUP
# ==================================================

if "selected_group" not in st.session_state:
    st.session_state["selected_group"] = None    

# ==========================================
# REPLY STATE
# ==========================================

if "reply_to" not in st.session_state:
    st.session_state["reply_to"] = None

if "highlight_message_id" not in st.session_state:
    st.session_state["highlight_message_id"] = None

# ==========================================
# FORWARD STATE (1-on-1 chat)
# ==========================================

if "forward_message_id" not in st.session_state:
    st.session_state["forward_message_id"] = None

if "forward_message_content" not in st.session_state:
    st.session_state["forward_message_content"] = None




# =========================
# CHAT
# =========================

# Only show the generic page title on the chat LIST. Once a
# specific conversation is open, WhatsApp replaces the top bar
# with that contact's own header instead of showing both --
# so we do the same here, rather than showing this title and
# then having it scroll independently of the fixed contact
# header below it.
if page == "Chats" and not st.session_state.get("selected_friend"):
    st.header("💬 Chat")


# ==================================================
# WHATSAPP-STYLE NOTIFICATIONS
# ==================================================

def get_unread_counts(current_user):

    cursor.execute(
        """
        SELECT sender, COUNT(*)
        FROM messages
        WHERE receiver = ?
          AND seen = 0
        GROUP BY sender
        """,
        (current_user,)
    )

    return dict(cursor.fetchall())


unread_counts = get_unread_counts(user)

if "_prev_unread_counts" not in st.session_state:
    st.session_state["_prev_unread_counts"] = {}

prev_unread_counts = st.session_state["_prev_unread_counts"]

_has_new_message = False

for sender, count in unread_counts.items():

    if count > prev_unread_counts.get(sender, 0):

        # Grab a short preview of their latest message
        cursor.execute(
            """
            SELECT message
            FROM messages
            WHERE sender = ? AND receiver = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (sender, user)
        )
        _latest_row = cursor.fetchone()
        _preview = _latest_row[0] if _latest_row else "New message"

        if str(_preview).startswith("**VOICE**:"):
            _preview = "🎤 Voice message"
        elif str(_preview).startswith("__IMAGE__:"):
            _preview = "🖼️ Image"
        elif str(_preview).startswith("__VIDEO__:"):
            _preview = "🎥 Video"
        elif str(_preview).startswith("__FILE__:"):
            _preview = "📎 File"
        elif len(str(_preview)) > 80:
            _preview = str(_preview)[:80] + "..."

        st.toast(
            f"📩 New message from {sender}",
            icon="💬"
        )

        show_popup_banner(f"New message from {sender}", _preview)

        send_desktop_notification(f"{sender} sent you a message", _preview)

        _has_new_message = True

if _has_new_message:
    play_notification_sound()

st.session_state["_prev_unread_counts"] = unread_counts




# ==================================================
# CHATS
# ==================================================

if page == "Chats":
    

    

    # ==================================================
    # CHAT LIST PAGE
    # ==================================================

    if st.session_state["selected_friend"] is None:

        st.header("💬 Chat list")
        
        search_text = st.text_input(
            "🔍 Search",
            placeholder="Search people...",
            key="chat_search"
        )
        all_people = get_users(user)

        if search_text.strip():
            search_text = search_text.strip().lower()
            
            people = [
                person
                for person in all_people
                if search_text in person.lower()
                
            ]
        else:
             # Default view: only people you've actually exchanged
             # a message with, not the entire user directory.
             recent_chats = get_recent_chats(user)

             people = [
                 person
                 for person in recent_chats
                 if not is_chat_deleted(
                     user,
                     person
                  )
              ]
             

        if not people:
            if search_text.strip():
                st.info("No users found.")
            else:
                st.info("No chats available.")

        else:

            for index, person in enumerate(people):

                # Safety net: never try to render a chat row for a
                # missing/blank username (can happen with old rows
                # from before the "receiver" column existed).
                if not person:
                    continue

                profile_pic = get_profile_pic(person)

                col1, col2, col3, col4 = st.columns(
                    [1, 4, 1, 1]
                )

                with col1:

                    if (
                        profile_pic
                        and os.path.exists(profile_pic)
                    ):

                        st.image(
                            profile_pic,
                            width=50
                        )

                    else:

                        st.markdown(
                            "👤",
                        )

                with col2:

                    unread = unread_counts.get(person, 0)

                    _is_online = get_presence_status(person) == "🟢 Online"

                    label = person

                    if _is_online:
                        label = f"🟢 {label}"

                    if unread > 0:
                        label = f"{label}   🔴 {unread}"

                    if st.button(
                        label,
                        key=f"open_chat_{index}_{person}",
                        use_container_width=True
                    ):

                        st.session_state[
                            "selected_friend"
                        ] = person

                        st.rerun()
            # ==========================================
            # DELETE BUTTON
            # ========================================== 

                with col3:
                    if st.button(
                        "🗑️",
                        key=f"delete_chat_{index}_{person}",
                        help=f"Delete chat with {person}"
                    ):
                        
                        delete_chat_for_user(
                            user,
                            person
                        )
                        # Make sure no chat remains selected
                        st.session_state[
                            "selected_friend"
                        ] = None
                        st.rerun()

                # ================================================== 
                # BLOCK / UNBLOCK BUTTON
                # ==================================================

                with col4:
                    if is_user_blocked(user, person):
                        if st.button(
                            "🔓",
                            key=f"unblock_{index}_{person}",
                            help=f"Unblock {person}"
                        ):

                            unblock_user(
                                user,
                                person
                            )
                            st.rerun()

                    else:
                        if st.button(
                            "🚫",
                            key=f"block_{index}_{person}",
                            help=f"Block {person}"
                        ):

                            block_user(
                                user,
                                person
                            )
                            st.rerun()
                
                        

        st.stop()


if page == "Chats" and st.session_state.get("selected_friend"):
        # =========================================================
    # CHAT PAGE
    # =========================================================

    # =========================================================
    # GET SAVED CHAT WALLPAPER
    # =========================================================

    selected_wallpaper = st.session_state.get(
        "chat_wallpaper",
        "🌌 Aurora Dream"
    )

    if selected_wallpaper not in chat_wallpapers:
        selected_wallpaper = "🌌 Aurora Dream"
        st.session_state["chat_wallpaper"] = selected_wallpaper

    wallpaper_css = chat_wallpapers[selected_wallpaper]


    # =========================================================
    # CHAT WALLPAPER CSS
    # =========================================================

    st.markdown(
        f"""
        <style>

        /* =====================================================
           CHAT PAGE BACKGROUND
           ===================================================== */

        [data-testid="stMain"] {{
            {wallpaper_css}
            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;
            background-attachment: fixed !important;

            min-height: 100vh !important;
        }}


        /* =====================================================
           STREAMLIT MAIN BLOCK
           Make it transparent so wallpaper is visible
           ===================================================== */

        [data-testid="stAppViewBlockContainer"] {{
            background: transparent !important;
        }}


        /* =====================================================
           STREAMLIT APP CONTAINER
           ===================================================== */

        [data-testid="stAppViewContainer"] {{
            background: transparent !important;
        }}


        /* =====================================================
           APP
           ===================================================== */

        .stApp {{
            background: transparent !important;
        }}


        /* =====================================================
           CHAT CONTENT
           ===================================================== */

        .chat-container {{
            {wallpaper_css}

            background-size: cover !important;
            background-position: center !important;
            background-repeat: no-repeat !important;

            min-height: calc(100vh - 80px) !important;

            width: 100% !important;

            box-sizing: border-box !important;

            padding: 20px !important;

            border-radius: 18px !important;
        }}


        /* =====================================================
           FIXED CHAT HEADER
           Targets the container via its Streamlit-assigned
           "st-key-<key>" class (the officially supported way to
           style a specific st.container()), instead of guessing
           internal element/class names that differ across
           Streamlit versions.
           ===================================================== */

        div.st-key-chat_header_box {{

            position: fixed !important;

            top: 0 !important;
            left: 0 !important;
            right: 0 !important;

            width: 100% !important;

            z-index: 999999 !important;

            background: rgba(255,255,255,0.97) !important;

            border-bottom: 1px solid #d1d7db !important;

            padding: 8px 16px !important;

            box-sizing: border-box !important;
        }}


        /* =====================================================
           SPACE FOR FIXED HEADER
           ===================================================== */

        .chat-header-space {{
            height: 0px !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 0 !important;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


    # =========================================================
    # SELECTED FRIEND
    # =========================================================

    friend = st.session_state["selected_friend"]

        

    # =========================================================
    # WHATSAPP-STYLE CHAT HEADER
    # =========================================================

    friend = st.session_state["selected_friend"]

    profile_pic = get_profile_pic(friend)

    # =========================================================
    # HEADER CSS
    # =========================================================

    st.markdown(
        """
        <style>

        /* ================================================
           FIXED CHAT HEADER
           ================================================ */ 

        .chat-header-container {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;

            width: 100% !important;
            height: 70px !important;

            z-index: 999999 !important;

            background: rgba(255,255,255,0.97) !important;

            border-bottom: 1px solid #d1d7db !important;

            box-sizing: border-box !important;
        }


        /* ================================================
           MOVE STREAMLIT HEADER CONTENT INTO FIXED HEADER
           ================================================ */

        .chat-header-container + div {
            margin-top: 70px !important;
        }


        /* ================================================
           NAME
           ================================================ */

        .chat-header-name {
            font-size: 17px !important;
            font-weight: 600 !important;

            color: #111827 !important;

            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }


        /* ================================================
           STATUS
           ================================================ */

        .chat-header-status {
            font-size: 12px !important;

            color: #667781 !important;

            margin-top: 2px !important;
        }


        /* ================================================
           BUTTONS
           ================================================ */

        .chat-header-container button {
            border: none !important;

            background: transparent !important;

            box-shadow: none !important;

            font-size: 21px !important;

            padding: 4px !important;
        }


        .chat-header-container button:hover {
            background: #f0f2f5 !important;

            border-radius: 50% !important;
        }


        /* ================================================
           PROFILE IMAGE
           ================================================ */

        .chat-header-container img {
            border-radius: 50% !important;

            object-fit: cover !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    ) 

    # =========================================================
    # HEADER
    # (given a stable "key" so the CSS above can target this
    # exact container via its auto-generated "st-key-<key>"
    # class and pin it to the top of the page -- see
    # ".chat-header-space" below for why we still need a spacer
    # after it.)
    # =========================================================

    header_box = st.container(key="chat_header_box")

    with header_box:

        back_col, pic_col, info_col, video_col, call_col, menu_col = st.columns(
            [0.7, 0.9, 5.0, 0.8, 0.8, 0.7],
            vertical_alignment="center"
        )


        # =========================================================
        # BACK BUTTON
        # =========================================================

        with back_col:

            if st.button(
                "←",
                key="chat_header_back_button"
            ):
                st.session_state["selected_friend"] = None
                st.rerun()


        # =========================================================
        # PROFILE PICTURE
        # =========================================================

        with pic_col:

            if profile_pic and os.path.isfile(profile_pic):

                st.image(
                    profile_pic,
                    width=48
                )

            else:

                st.markdown(
                    "👤",
                    unsafe_allow_html=False
                )


        # =========================================================
        # NAME + STATUS
        # =========================================================

        with info_col:

            _presence_text = get_presence_status(friend)

            st.markdown(
                f'<div class="chat-header-info">'
                f'<div class="chat-header-name">{html.escape(friend)}</div>'
                f'<div class="chat-header-status">{html.escape(_presence_text)}</div>'
                f'</div>',
                unsafe_allow_html=True
            )




        # =========================================================
        # THREE DOT MENU
        # =========================================================

        with menu_col:

            if st.button(
                "⋮",
                key="chat_header_menu",
                
            ):

                st.session_state["show_chat_menu"] = not st.session_state.get(
                    "show_chat_menu",
                    False
                )

    # =========================================================
    # SPACER so the now-fixed header above doesn't cover the
    # first messages / the three-dot menu content below it.
    # =========================================================

    st.markdown(
        '<div class="chat-header-space"></div>',
        unsafe_allow_html=True
    )

    # =========================================================
    # THREE-DOT MENU CONTENT
    # =========================================================

    if st.session_state.get("show_chat_menu", False):

        st.divider()

        # -----------------------------------------------------
        # SEARCH
        # -----------------------------------------------------

        if st.button(
            "🔍 Search",
            key=f"chat_menu_search_{friend}"
        ):

            st.session_state["chat_search_open"] = not st.session_state.get(
                "chat_search_open",
                False
            )

            st.rerun()


        # =========================================================
        # SEARCH MESSAGES
        # =========================================================

        if st.session_state.get("chat_search_open", False):

          search_message = st.text_input(
            "🔍 Search messages",
            key=f"chat_message_search_{friend}",
            placeholder="Type a message to search..."
          )

          if search_message.strip():

            # Get messages using your existing function
            messages = get_messages(user, friend)

            found_messages = []

            for msg in messages:

                # -------------------------------------------------
                # get_messages() returns:
                # (id, sender, message, time, reply_to)
                # message text is at index 2
                # -------------------------------------------------

                if isinstance(msg, (tuple, list)):

                    if len(msg) > 2:

                        message_text = str(msg[2])

                    else:

                        message_text = str(msg)

                else:

                    message_text = str(msg)


                # -------------------------------------------------
                # Compare search text with actual message
                # -------------------------------------------------

                if search_message.strip().lower() in message_text.lower():

                    found_messages.append(msg)


            # ----------------------------------------------------- 
            # SHOW RESULTS
            # -----------------------------------------------------

            if found_messages:

                st.success(
                    f"Found {len(found_messages)} matching message(s)"
                )

                for msg in found_messages:

                    if isinstance(msg, (tuple, list)) and len(msg) > 2:

                        sender_name = msg[1]
                        message_text = str(msg[2])
                        msg_time = to_local_time_str(msg[3] if len(msg) > 3 else "")

                        if message_text.startswith("**VOICE**:"):
                            message_text = "🎤 Voice message"
                        elif message_text.startswith("__IMAGE__:"):
                            message_text = "🖼️ Image"
                        elif message_text.startswith("__VIDEO__:"):
                            message_text = "🎥 Video"
                        elif message_text.startswith("__FILE__:"):
                            message_text = "📎 File"

                        st.markdown(
                            f'<div style="background:#dcf8c6;padding:10px 14px;'
                            f'margin:6px 0;border-radius:10px;width:fit-content;">'
                            f'<b>{html.escape(str(sender_name))}:</b> '
                            f'{html.escape(message_text)}'
                            f'<br><small style="color:#667;">{html.escape(str(msg_time))}</small>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    else:

                        st.write(msg)

            else:

                st.info("No matching messages found.")


        # -----------------------------------------------------
        # MUTE
        # -----------------------------------------------------

        current_mute_state = st.session_state.get(
            f"muted_{friend}",
            False
        )

        mute_text = (
            "🔔 Unmute notifications"
            if current_mute_state
            else "🔕 Mute notifications"
        )

        if st.button(
            mute_text,
            key=f"chat_menu_mute_{friend}"
        ):

            st.session_state[f"muted_{friend}"] = not current_mute_state

            if st.session_state[f"muted_{friend}"]:

                st.toast(
                    f"🔕 {friend} notifications muted"
                )

            else:

                st.toast(
                    f"🔔 {friend} notifications unmuted"
                )

            st.rerun()


        # -----------------------------------------------------
        # DELETE CHAT
        # -----------------------------------------------------

        if st.button(
            "🗑️ Delete chat",
            key=f"chat_menu_delete_{friend}"
        ):

            st.session_state["delete_chat_confirm"] = True

            st.rerun()


        # -----------------------------------------------------
    # DELETE CONFIRMATION
    # -----------------------------------------------------

    if st.session_state.get(
        "delete_chat_confirm",
        False
    ):

        st.warning(
            f"Delete your chat with {friend}?"
        )

        delete_col1, delete_col2 = st.columns(2)

        with delete_col1:

            if st.button(
                "Delete",
                key=f"confirm_delete_{friend}"
            ):

                # Get the logged-in user
                current_user = (
                    st.session_state.get("logged_in_user")
                    or st.session_state.get("current_user")
                    or st.session_state.get("user")
                    or st.session_state.get("logged_user")
                )

                if current_user:

                    # IMPORTANT:
                    # delete_chat_for_user needs TWO arguments
                    delete_chat_for_user(
                        current_user,
                        friend
                    )

                    st.session_state["delete_chat_confirm"] = False
                    st.session_state["show_chat_menu"] = False
                    st.session_state["selected_friend"] = None

                    st.rerun()

                else:

                    st.error(
                        "Unable to identify the logged-in user."
                    )


        with delete_col2:

            if st.button(
                "Cancel",
                key=f"cancel_delete_{friend}"
            ): 

                st.session_state["delete_chat_confirm"] = False

                st.rerun()


    # =========================================================
    # CALL SCREEN
    # =========================================================

    if st.session_state.get("show_call_screen", False):

        calling_friend = st.session_state.get(
            "calling_friend",
            friend
        )

        call_type = st.session_state.get(
            "call_type",
            "audio"
        )

        st.markdown(
            f"""
            <div style="
                padding:25px;
                margin-top:15px;
                border-radius:15px;
                background:#f0f2f5;
                text-align:center;
            ">

                <div style="font-size:45px;">
                    {"📹" if call_type == "video" else "📞"}
                </div>

                <div style="
                    font-size:20px;
                    font-weight:600;
                    margin-top:10px;
                ">
                    {calling_friend}
                </div>

                <div style="
                    color:#667781;
                    margin-top:5px;
                ">
                    Calling...
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "❌ End Call",
            key="end_chat_call"
        ):

            st.session_state["show_call_screen"] = False
            st.session_state["calling_friend"] = None
            st.session_state["call_type"] = None

            st.rerun()


    # =========================================================
    # HEADER SEPARATOR
    # =========================================================

    st.divider()





if "selected_group" not in st.session_state:
    st.session_state["selected_group"] = None

if "creating_group" not in st.session_state:
    st.session_state["creating_group"] = False

if "group_reply_to" not in st.session_state:
    st.session_state["group_reply_to"] = None
    
if "selected_group" not in st.session_state:
    st.session_state["selected_group"] = None

if "group_forward_message_id" not in st.session_state:
    st.session_state["group_forward_message_id"] = None

if "group_forward_message_content" not in st.session_state:
    st.session_state["group_forward_message_content"] = None

if "group_info_id" not in st.session_state:
    st.session_state["group_info_id"] = None

if "group_highlight_message_id" not in st.session_state:
    st.session_state["group_highlight_message_id"] = None

if "show_group_chat_menu" not in st.session_state:
    st.session_state["show_group_chat_menu"] = False

if "group_search_open" not in st.session_state:
    st.session_state["group_search_open"] = False


# ==================================================
# GROUPS
# ==================================================

if page == "Groups":

    # ==================================================
    # GROUP LIST PAGE
    # ==================================================

    if st.session_state["selected_group"] is None:

        st.header("👥 Groups")

        # ----------------------------------------------
        # CREATE GROUP BUTTON
        # ----------------------------------------------

        if st.button(
            "➕ Create New Group",
            key="create_new_group"
        ):
            st.session_state["creating_group"] = True
            st.rerun()

        # ----------------------------------------------
        # CREATE GROUP FORM
        # ----------------------------------------------
  
        if st.session_state.get(
            "creating_group",
            False
         ):
            st.subheader("Create New Group")
            with st.form(

                "create_group_form"
            ):
                group_name = st.text_input(
                    "Group Name",
                    placeholder="Enter group name"
                )
                people = get_users(user)

                selected_members = st.multiselect(
                    "Select Members",
                    people
                )
                col1, col2 = st.columns(2)

                with col1:
                    create_clicked = st.form_submit_button(
                        "✅ Create Group",
                        use_container_width=True
                    
                     )

                with col2:
                    cancel_clicked = st.form_submit_button(
                        "❌ Cancel",
                        use_container_width=True
                    )

            # ==========================================
            # CANCEL
            # ==========================================

            if cancel_clicked:
                st.session_state[
                    "creating_group"
                ] = False

                st.rerun()

            # ==========================================
            # CREATE
            # ========================================== 

            if create_clicked:
                if not group_name.strip():
                    st.error(
                        "Please enter a group name."
                     )

                elif not selected_members:
                    st.error(
                        "Please select at least one member."
                    )

                else:
                    group_id = create_group(
                        group_name,
                        user,
                        selected_members
                     )
                    if group_id:
                         st.session_state[
                             "creating_group"
                         ] = False

                         # Open the newly created group
                         st.session_state[
                             "selected_group"
                         ] = group_id

                         st.success(
                             "✅ Group created successfully!"
                        )
                         st.rerun()
  
        

        # ----------------------------------------------
        # GROUP LIST
        # ----------------------------------------------

        groups = get_user_groups(user)

        if not groups:

            st.info(
                "You are not a member of any groups yet."
            )

        else:

            st.subheader("Your Groups")

            for group_id, group_name, creator in groups:

                members = get_group_members(
                    group_id
                )

                col1, col2, col3 = st.columns(
                    [1, 5, 1]
                )

                with col1:

                    _group_pic_path = get_group_pic(group_id)

                    if _group_pic_path and os.path.isfile(_group_pic_path):
                        st.image(_group_pic_path, width=48)
                    else:
                        st.markdown(
                            "👥",
                            unsafe_allow_html=True
                        )

                with col2:

                    if st.button(
                        f"{group_name}",
                        key=f"open_group_{group_id}",
                        use_container_width=True
                    ):

                        st.session_state[
                            "selected_group"
                        ] = group_id

                        st.session_state[
                            "selected_friend"
                        ] = None

                        st.rerun()

                    st.caption(
                        f"{len(members)} members"
                    )
            # ==========================================
            # DELETE BUTTON
            # ==========================================

                with col3:
                    if st.button(
                        "🗑️",
                        key=f"delete_group_{group_id}",
                        help=f"Delete group"
                    ):
                        # Delete messages
                        cursor.execute(
                            """
                            DELETE FROM group_messages
                            WHERE group_id = ?
                            """,
                            (group_id,)
                        )

                        # Delete members
                        cursor.execute(
                            """
                            DELETE FROM group_members 
                            WHERE group_id = ?
                            """,
                            (group_id,)
                        )
                        # Delete group
                        cursor.execute(
                            """
                            DELETE FROM groups
                            WHERE id = ?
                            """,
                            (group_id,)
                        )
                        conn.commit()
                        st.session_state[
                            "selected_group"
                        ] = None
                        st.session_state[
                            "selected_friend"
                        ] = None
                        st.rerun()
                        
                        # Make sure no chat remains selected
                        st.session_state[
                            "selected_friend"
                            ] = None
                        st.rerun()
                    
        # ----------------------------------------------
        # DELETE GROUP CONFIRMATION
        # ----------------------------------------------

        if st.session_state.get(
            "delete_group_id"
        ) is not None:

            delete_id = st.session_state[
                "delete_group_id"
            ]

            st.warning(
                "⚠️ Are you sure you want to delete this group?"
            )

            col1, col2 = st.columns(2)
        # ------------------------------------------
        # CONFIRM DELETE
        # ------------------------------------------

            with col1:

                if st.button(
                    "🗑️ Delete",
                    key="confirm_delete_group",
                    use_container_width=True
                ):

                    cursor.execute(
                        """
                        DELETE FROM group_messages
                        WHERE group_id = ?
                        """,
                        (delete_id,)
                    )
                    cursor.execute(
                        """
                        DELETE FROM group_members
                        WHERE group_id = ?
                        """,
                        (delete_id,)
                    )

                    cursor.execute(
                        """
                        DELETE FROM groups
                        WHERE id = ?
                        """,
                        (delete_id,)
                    )

                    conn.commit()

                    st.session_state[
                        "delete_group_id"
                    ] = None
                    if st.session_state.get(
                        "selected_group"
                    ) == delete_id:

                        st.session_state[
                            "selected_group"
                        ] = None

                    st.rerun()
            # ------------------------------------------
            # CANCEL DELETE
            # ------------------------------------------

            with col2:

                if st.button(
                    "❌ Cancel",
                    key="cancel_delete_group",
                    use_container_width=True
                ):

                    st.session_state[
                        "delete_group_id"
                    ] = None

                    st.rerun()

        st.stop()

    # ==================================================
    # GROUP CHAT PAGE
    # ==================================================

    group_id = st.session_state.get("selected_group")

    if not group_id:
        st.warning("No group selected.")
        st.stop() 

    # ==================================================
    # GET GROUP INFORMATION
    # ==================================================

    cursor.execute(
        """
        SELECT name, creator
        FROM groups
        WHERE id = ?
        """,
        (group_id,)
    )

    group_info = cursor.fetchone()
    if not group_info:
        st.error("Group not found.")
        st.stop()
    group_name, group_creator = group_info


    # ==================================================
    # GROUP INFO PAGE
    # ==================================================

    if st.session_state.get("group_info_id") == group_id:

        cursor.execute(
            """
            SELECT created_at
            FROM groups
            WHERE id = ?
            """,
            (group_id,)
        )

        created_row = cursor.fetchone()
        created_at = created_row[0] if created_row else "Unknown"

        members = get_group_members(group_id)

        # ----------------------------------------------
        # BACK TO GROUP CHAT
        # ----------------------------------------------

        if st.button(
            "← Back to Group",
            key="back_to_group_chat_from_info"
        ):
            st.session_state["group_info_id"] = None
            st.rerun()

        st.header("ℹ️ Group Info")

        _is_group_admin = (user == group_creator)

        # ----------------------------------------------
        # GROUP PHOTO
        # ----------------------------------------------

        group_pic_path = get_group_pic(group_id)

        pic_col, name_col = st.columns([1, 4])

        with pic_col:
            if group_pic_path and os.path.isfile(group_pic_path):
                st.image(group_pic_path, width=80)
            else:
                st.markdown(
                    "<div style='font-size:56px;'>👥</div>",
                    unsafe_allow_html=True
                )

        with name_col:
            st.markdown(f"## {group_name}")
            st.caption(f"Created by {group_creator} • {created_at}")
            st.caption(f"{len(members)} members")

        if _is_group_admin:

            with st.expander("📷 Change Group Photo"):

                new_group_photo = st.file_uploader(
                    "Upload a new group photo",
                    type=["jpg", "jpeg", "png"],
                    key=f"group_photo_upload_{group_id}"
                )

                if new_group_photo is not None:

                    if st.button(
                        "✅ Set as Group Photo",
                        key=f"confirm_group_photo_{group_id}"
                    ):
                        save_group_pic(
                            group_id,
                            new_group_photo.getvalue()
                        )
                        st.toast("📷 Group photo updated", icon="✅")
                        st.rerun()

            with st.expander("✏️ Rename Group"):

                renamed_group = st.text_input(
                    "New group name",
                    value=group_name,
                    key=f"rename_group_input_{group_id}"
                )

                if st.button(
                    "✅ Save New Name",
                    key=f"confirm_rename_group_{group_id}"
                ):
                    if rename_group(group_id, renamed_group, user):
                        st.toast("✏️ Group renamed", icon="✅")
                        st.rerun()
                    else:
                        st.error("Group name can't be empty.")

        st.divider()

        # ----------------------------------------------
        # MEMBERS LIST
        # ----------------------------------------------

        st.subheader("Members")

        _is_admin = (user == group_creator)

        for member in members:

            if _is_admin and member != group_creator:
                col1, col2, col3 = st.columns([0.5, 4, 1.2])
            else:
                col1, col2 = st.columns([0.5, 5])

            with col1:
                st.markdown("👤")

            with col2:
                if member == group_creator:
                    st.write(f"**{member}**  👑 Admin" + (
                        "  *(You)*" if member == user else ""
                    ))
                else:
                    st.write(
                        f"{member}" + (
                            "  *(You)*" if member == user else ""
                        )
                    )

            if _is_admin and member != group_creator:
                with col3:
                    if st.button(
                        "Remove",
                        key=f"remove_member_{group_id}_{member}",
                        use_container_width=True
                    ):
                        remove_group_member(group_id, member)
                        st.toast(f"Removed {member} from the group", icon="👋")
                        st.rerun()

        st.divider()

        # ----------------------------------------------
        # ADD MEMBERS
        # ----------------------------------------------

        all_users = get_users(user)

        addable_users = [
            u for u in all_users
            if u not in members
        ]

        if st.session_state.get("adding_group_members") != group_id:

            if st.button(
                "➕ Add Members",
                key=f"add_members_btn_{group_id}",
                use_container_width=True
            ):
                st.session_state["adding_group_members"] = group_id
                st.rerun()

        else:

            if not addable_users:

                st.info("Everyone is already in this group.")

                if st.button(
                    "❌ Cancel",
                    key=f"cancel_add_members_empty_{group_id}"
                ):
                    st.session_state["adding_group_members"] = None
                    st.rerun()

            else:

                new_members = st.multiselect(
                    "Select people to add",
                    addable_users,
                    key=f"new_members_select_{group_id}"
                )

                col1, col2 = st.columns(2)

                with col1:

                    if st.button(
                        "✅ Add Selected",
                        key=f"confirm_add_members_{group_id}",
                        use_container_width=True,
                        disabled=not new_members
                    ):
                        add_group_members(group_id, new_members)

                        st.session_state["adding_group_members"] = None

                        st.toast(
                            f"➕ Added {len(new_members)} member(s)",
                            icon="👥"
                        )
                        st.rerun()

                with col2:

                    if st.button(
                        "❌ Cancel",
                        key=f"cancel_add_members_{group_id}",
                        use_container_width=True
                    ):
                        st.session_state["adding_group_members"] = None
                        st.rerun()

        st.divider()

        # ----------------------------------------------
        # EXIT GROUP
        # ----------------------------------------------

        if st.session_state.get("confirm_exit_group") != group_id:

            if st.button(
                "🚪 Exit Group",
                key=f"exit_group_{group_id}",
                use_container_width=True
            ):
                st.session_state["confirm_exit_group"] = group_id
                st.rerun()

        else:

            st.warning("⚠️ Are you sure you want to exit this group?")

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "🚪 Confirm Exit",
                    key=f"confirm_exit_group_btn_{group_id}",
                    use_container_width=True
                ):

                    cursor.execute(
                        """
                        DELETE FROM group_members
                        WHERE group_id = ?
                          AND username = ?
                        """,
                        (group_id, user)
                    )
                    conn.commit()

                    # Clean up the group entirely if no members remain
                    cursor.execute(
                        """
                        SELECT COUNT(*)
                        FROM group_members
                        WHERE group_id = ?
                        """,
                        (group_id,)
                    )
                    remaining = cursor.fetchone()[0]

                    if remaining == 0:
                        cursor.execute(
                            "DELETE FROM group_messages WHERE group_id = ?",
                            (group_id,)
                        )
                        cursor.execute(
                            "DELETE FROM groups WHERE id = ?",
                            (group_id,)
                        )
                        conn.commit()

                    st.session_state["confirm_exit_group"] = None
                    st.session_state["group_info_id"] = None
                    st.session_state["selected_group"] = None
                    st.session_state["selected_friend"] = None

                    st.toast(f"🚪 You left {group_name}", icon="👋")
                    st.rerun()

            with col2:

                if st.button(
                    "❌ Cancel",
                    key=f"cancel_exit_group_{group_id}",
                    use_container_width=True
                ):
                    st.session_state["confirm_exit_group"] = None
                    st.rerun()

        st.stop()



    # ==================================================
    # GROUP HEADER CSS
    # (mirrors the fixed WhatsApp-style header used in the
    # 1-on-1 chat, so the group header looks/behaves the
    # same way.)
    # ==================================================

    st.markdown(
        """
        <style>

        /* ================================================
           FIXED GROUP HEADER
           ================================================ */

        div.st-key-group_header_box {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;

            width: 100% !important;
            height: 70px !important;

            z-index: 999999 !important;

            background: rgba(255,255,255,0.97) !important;

            border-bottom: 1px solid #d1d7db !important;

            box-sizing: border-box !important;
        }

        div.st-key-group_header_box + div {
            margin-top: 70px !important;
        }


        /* ================================================
           SPACE FOR FIXED HEADER
           ================================================ */

        .group-header-space {
            height: 0px !important;
            margin: 0 !important;
            padding: 0 !important;
            line-height: 0 !important;
        }


        /* ================================================
           NAME
           ================================================ */

        .chat-header-name {
            font-size: 17px !important;
            font-weight: 600 !important;

            color: #111827 !important;

            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }


        /* ================================================
           STATUS
           ================================================ */

        .chat-header-status {
            font-size: 12px !important;

            color: #667781 !important;

            margin-top: 2px !important;
        }


        /* ================================================
           BUTTONS
           ================================================ */

        div.st-key-group_header_box button {
            border: none !important;

            background: transparent !important;

            box-shadow: none !important;

            font-size: 21px !important;

            padding: 4px !important;
        }

        div.st-key-group_header_box button:hover {
            background: #f0f2f5 !important;

            border-radius: 50% !important;
        }


        /* ================================================
           BACK BUTTON (bigger + highlighted)
           ================================================ */

        div.st-key-group_header_back_button button {
            font-size: 26px !important;
            font-weight: 700 !important;

            color: #1a73e8 !important;

            background: #e8f0fe !important;

            border-radius: 50% !important;

            width: 40px !important;
            height: 40px !important;

            padding: 0 !important;
        }

        div.st-key-group_header_back_button button:hover {
            background: #d2e3fc !important;
        }


        /* ================================================
           GROUP IMAGE
           ================================================ */

        div.st-key-group_header_box img {
            border-radius: 50% !important;

            object-fit: cover !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # ==================================================
    # GROUP HEADER
    # (same fixed WhatsApp-style header as the 1-on-1 chat --
    # given a stable "key" so the CSS above can target this
    # exact container via its auto-generated "st-key-<key>"
    # class and pin it to the top of the page.)
    # ==================================================

    group_header_box = st.container(key="group_header_box")

    with group_header_box:

        back_col, pic_col, info_col, info_btn_col, menu_col = st.columns(
            [0.7, 0.9, 5.0, 0.8, 0.7],
            vertical_alignment="center"
        )

        # =========================================================
        # BACK BUTTON
        # =========================================================

        with back_col:

            if st.button(
                "←",
                key="group_header_back_button"
            ):
                st.session_state["selected_group"] = None
                st.session_state["selected_friend"] = None
                st.session_state["group_reply_to"] = None
                st.rerun()

        # =========================================================
        # GROUP PICTURE
        # =========================================================

        with pic_col:

            _group_pic_path = get_group_pic(group_id)

            if _group_pic_path and os.path.isfile(_group_pic_path):

                st.image(
                    _group_pic_path,
                    width=48
                )

            else:

                st.markdown(
                    "👥",
                    unsafe_allow_html=False
                )

        # =========================================================
        # NAME + STATUS
        # =========================================================

        with info_col:

            _group_member_count = len(get_group_members(group_id))

            st.markdown(
                f'<div class="chat-header-info">'
                f'<div class="chat-header-name">{html.escape(group_name)}</div>'
                f'<div class="chat-header-status">{_group_member_count} members</div>'
                f'</div>',
                unsafe_allow_html=True
            )

        # =========================================================
        # GROUP INFO BUTTON
        # =========================================================

        with info_btn_col:

            if st.button(
                "ℹ️",
                key=f"open_group_info_{group_id}",
                help="Tap to view group info"
            ):
                st.session_state["group_info_id"] = group_id
                st.rerun()

        # =========================================================
        # THREE DOT MENU
        # =========================================================

        with menu_col:

            if st.button(
                "⋮",
                key="group_header_menu"
            ):

                st.session_state["show_group_chat_menu"] = not st.session_state.get(
                    "show_group_chat_menu",
                    False
                )

    # =========================================================
    # SPACER so the now-fixed header above doesn't cover the
    # first messages / the three-dot menu content below it.
    # =========================================================

    st.markdown(
        '<div class="group-header-space"></div>',
        unsafe_allow_html=True
    )

    st.caption(
        f"Created by {group_creator}"
    )

    # =========================================================
    # THREE-DOT MENU CONTENT
    # =========================================================

    if st.session_state.get("show_group_chat_menu", False):

        st.divider()

        # -----------------------------------------------------
        # SEARCH
        # -----------------------------------------------------

        if st.button(
            "🔍 Search",
            key=f"group_menu_search_{group_id}"
        ):

            st.session_state["group_search_open"] = not st.session_state.get(
                "group_search_open",
                False
            )

            st.rerun()

        # =========================================================
        # SEARCH MESSAGES
        # =========================================================

        if st.session_state.get("group_search_open", False):

            search_message = st.text_input(
                "🔍 Search messages",
                key=f"group_message_search_{group_id}",
                placeholder="Type a message to search..."
            )

            if search_message.strip():

                _group_messages_for_search = get_group_messages(group_id)

                found_messages = []

                for gm in _group_messages_for_search:

                    if isinstance(gm, (tuple, list)) and len(gm) > 2:
                        message_text = str(gm[2])
                    else:
                        message_text = str(gm)

                    if search_message.strip().lower() in message_text.lower():
                        found_messages.append(gm)

                if found_messages:

                    st.success(
                        f"Found {len(found_messages)} matching message(s)"
                    )

                    for gm in found_messages:

                        if isinstance(gm, (tuple, list)) and len(gm) > 2:

                            sender_name = gm[1]
                            message_text = str(gm[2])
                            msg_time = to_local_time_str(gm[3] if len(gm) > 3 else "")

                            if message_text.startswith("**VOICE**:"):
                                message_text = "🎤 Voice message"
                            elif message_text.startswith("__IMAGE__:"):
                                message_text = "🖼️ Image"
                            elif message_text.startswith("__VIDEO__:"):
                                message_text = "🎥 Video"
                            elif message_text.startswith("__FILE__:"):
                                message_text = "📎 File"

                            st.markdown(
                                f'<div style="background:#dcf8c6;padding:10px 14px;'
                                f'margin:6px 0;border-radius:10px;width:fit-content;">'
                                f'<b>{html.escape(str(sender_name))}:</b> '
                                f'{html.escape(message_text)}'
                                f'<br><small style="color:#667;">{html.escape(str(msg_time))}</small>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                        else:
                            st.write(gm)

                else:
                    st.info("No matching messages found.")

        # -----------------------------------------------------
        # MUTE
        # -----------------------------------------------------

        current_group_mute_state = st.session_state.get(
            f"muted_group_{group_id}",
            False
        )

        group_mute_text = (
            "🔔 Unmute notifications"
            if current_group_mute_state
            else "🔕 Mute notifications"
        )

        if st.button(
            group_mute_text,
            key=f"group_menu_mute_{group_id}"
        ):

            st.session_state[f"muted_group_{group_id}"] = not current_group_mute_state

            if st.session_state[f"muted_group_{group_id}"]:

                st.toast(
                    f"🔕 {group_name} notifications muted"
                )

            else:

                st.toast(
                    f"🔔 {group_name} notifications unmuted"
                )

            st.rerun()

        # -----------------------------------------------------
        # GROUP INFO
        # -----------------------------------------------------

        if st.button(
            "ℹ️ Group Info",
            key=f"group_menu_info_{group_id}"
        ):
            st.session_state["group_info_id"] = group_id
            st.rerun()

        st.divider()


    # ==================================================
    # GROUP MESSAGES
    # ==================================================

    group_messages = get_group_messages(
        group_id
    )

    for (
        message_id,
        sender,
        msg,
        time,
        reply_to
    ) in group_messages:

        time = to_local_time_str(time)

        # ==========================================
        # REPLY INFORMATION
        # ==========================================

        reply_html = ""

        if reply_to is not None:

            cursor.execute(
                """
                SELECT sender, message
                FROM group_messages
                WHERE id = ?
                """,
                (reply_to,)
            )

            reply_data = cursor.fetchone()

            

            if reply_data: 

                reply_sender = reply_data[0]
                reply_text = reply_data[1]

                if str(reply_text).startswith(
                    "**VOICE**:"
                ):

                    reply_text = "🎤 Voice message"

                elif str(reply_text).startswith(
                    "__IMAGE__:"
                ):

                    reply_text = "🖼️ Image"

                elif str(reply_text).startswith(
                    "__VIDEO__:"
                ):

                    reply_text = "🎥 Video"

                elif str(reply_text).startswith(
                    "__FILE__:"
                ):

                    reply_text = "📎 " + os.path.basename(
                        str(reply_text).split("__FILE__:", 1)[1].strip()
                    )

                reply_html = f"↩️ {reply_sender}: {reply_text}"
        # ------------------------------------------
        # VOICE MESSAGE
        # ------------------------------------------

        if str(msg).startswith(
            "**VOICE**:"
        ):

            audio_path = str(msg).split(
                "**VOICE**:",
                1
            )[1].strip()

            col1, col2 = st.columns(
                [8, 2]
            )

            with col1:

                if reply_html:
                    if st.button(
                        reply_html,
                        key=f"group_jump_to_voice_{group_id}_{message_id}",
                        use_container_width=True
                    ):
                        st.session_state["group_highlight_message_id"] = reply_to
                        st.rerun()

                if st.session_state.get("group_highlight_message_id") == message_id:
                    st.markdown(
                        f'<div id="group_msg_{message_id}" style="border:2px solid #f5b301;'
                        'background:#fff3b0;border-radius:8px;'
                        'padding:6px 10px;margin-bottom:4px;font-size:13px;">'
                        '🔶 Replied-to message</div>',
                        unsafe_allow_html=True
                    )

                    components.html(
                        f"""
                        <script>
                        var el = window.parent.document.getElementById("group_msg_{message_id}");
                        if (el) {{
                            el.scrollIntoView({{behavior: "smooth", block: "center"}});
                        }}
                        </script>
                        """,
                        height=0
                    )

                if os.path.exists(
                    audio_path
                ):

                    st.audio(
                        audio_path,
                        format="audio/wav"
                    )
                else:

                    st.error(
                        "🎵 Audio file not found."
                    )

                st.caption(
                    f"{sender} • {time}"
                )

            with col2:

                def _delete_group_voice_message(_mid=message_id, _path=audio_path):
                    cursor.execute(
                        """
                        DELETE FROM group_messages
                        WHERE id = ?
                        """,
                        (_mid,)
                    )
                    conn.commit()

                    if os.path.exists(_path):
                        try:
                            os.remove(_path)
                        except:
                            pass

                    st.session_state.pop("group_reply_to", None)

                render_message_actions_menu(
                    key_prefix=f"group_voice_{group_id}_{message_id}",
                    reply_state_key="group_reply_to",
                    reply_value=message_id,
                    forward_id_key="group_forward_message_id",
                    forward_content_key="group_forward_message_content",
                    forward_content=str(msg),
                    copy_text=audio_path,
                    copy_toast="📋 Voice message path copied",
                    delete_action=_delete_group_voice_message
                )

            continue
        
        # ------------------------------------------
        # IMAGE MESSAGE
        # ------------------------------------------

        if str(msg).startswith(
            "__IMAGE__:"
        ):

            image_path = str(msg).split(
                "__IMAGE__:",
                1
            )[1].strip()

            col1, col2 = st.columns(
                [8, 2]
            )

            with col1:

                if reply_html:
                    if st.button(
                        reply_html,
                        key=f"group_jump_to_image_{group_id}_{message_id}",
                        use_container_width=True
                    ):
                        st.session_state["group_highlight_message_id"] = reply_to
                        st.rerun()

                if st.session_state.get("group_highlight_message_id") == message_id:
                    st.markdown(
                        f'<div id="group_msg_{message_id}" style="border:2px solid #f5b301;'
                        'background:#fff3b0;border-radius:8px;'
                        'padding:6px 10px;margin-bottom:4px;font-size:13px;">'
                        '🔶 Replied-to message</div>',
                        unsafe_allow_html=True
                    )

                    components.html(
                        f"""
                        <script>
                        var el = window.parent.document.getElementById("group_msg_{message_id}");
                        if (el) {{
                            el.scrollIntoView({{behavior: "smooth", block: "center"}});
                        }}
                        </script>
                        """,
                        height=0
                    )

                if os.path.exists(
                    image_path
                ):

                    st.image(
                        image_path,
                        width=300
                    )
                else:

                    st.error(
                        "🖼️ Image file not found."
                    )

                st.caption(
                    f"{sender} • {time}"
                    f"{'✓✓ Seen' if seen else '✓ Sent'}"
                )

            with col2:

                def _delete_group_image_message(_mid=message_id, _path=image_path):
                    cursor.execute(
                        """
                        DELETE FROM group_messages
                        WHERE id = ?
                        """,
                        (_mid,)
                    )
                    conn.commit()

                    if os.path.exists(_path):
                        try:
                            os.remove(_path)
                        except:
                            pass

                render_message_actions_menu(
                    key_prefix=f"group_image_{group_id}_{message_id}",
                    reply_state_key="group_reply_to",
                    reply_value=message_id,
                    forward_id_key="group_forward_message_id",
                    forward_content_key="group_forward_message_content",
                    forward_content=str(msg),
                    copy_text=image_path,
                    copy_toast="📋 Image path copied",
                    delete_action=_delete_group_image_message
                )

            continue
        # ------------------------------------------
        # VIDEO MESSAGE
        # ------------------------------------------

        if str(msg).startswith(
            "__VIDEO__:"
        ):

            video_path = str(msg).split(
                "__VIDEO__:",
                1
            )[1].strip()

            col1, col2 = st.columns(
                [8, 2]
            )

            with col1:

                if reply_html:
                    if st.button(
                        reply_html,
                        key=f"group_jump_to_video_{group_id}_{message_id}",
                        use_container_width=True
                    ):
                        st.session_state["group_highlight_message_id"] = reply_to
                        st.rerun()

                if st.session_state.get("group_highlight_message_id") == message_id:
                    st.markdown(
                        f'<div id="group_msg_{message_id}" style="border:2px solid #f5b301;'
                        'background:#fff3b0;border-radius:8px;'
                        'padding:6px 10px;margin-bottom:4px;font-size:13px;">'
                        '🔶 Replied-to message</div>',
                        unsafe_allow_html=True
                    )

                    components.html(
                        f"""
                        <script>
                        var el = window.parent.document.getElementById("group_msg_{message_id}");
                        if (el) {{
                            el.scrollIntoView({{behavior: "smooth", block: "center"}});
                        }}
                        </script>
                        """,
                        height=0
                    )

                if os.path.exists(
                    video_path
                ):

                    st.video(
                        video_path
                    )
                else:

                    st.error(
                        "🎥 Video file not found."
                    )

                st.caption(
                    f"{sender} • {time}"f"{'✓✓ Seen' if seen else '✓ Sent'}"
                )

            with col2:

                def _delete_group_video_message(_mid=message_id, _path=video_path):
                    cursor.execute(
                        """
                        DELETE FROM group_messages
                        WHERE id = ?
                        """,
                        (_mid,)
                    )
                    conn.commit()

                    if os.path.exists(_path):
                        try:
                            os.remove(_path)
                        except:
                            pass

                render_message_actions_menu(
                    key_prefix=f"group_video_{group_id}_{message_id}",
                    reply_state_key="group_reply_to",
                    reply_value=message_id,
                    forward_id_key="group_forward_message_id",
                    forward_content_key="group_forward_message_content",
                    forward_content=str(msg),
                    copy_text=video_path,
                    copy_toast="📋 Video path copied",
                    delete_action=_delete_group_video_message
                )

            continue
        # ------------------------------------------
        # FILE MESSAGE
        # ------------------------------------------

        if str(msg).startswith(
            "__FILE__:"
        ):

            file_path = str(msg).split(
                "__FILE__:",
                1
            )[1].strip()

            col1, col2 = st.columns(
                [8, 2]
            )

            with col1:

                if reply_html:
                    if st.button(
                        reply_html,
                        key=f"group_jump_to_file_{group_id}_{message_id}",
                        use_container_width=True
                    ):
                        st.session_state["group_highlight_message_id"] = reply_to
                        st.rerun()

                if st.session_state.get("group_highlight_message_id") == message_id:
                    st.markdown(
                        f'<div id="group_msg_{message_id}" style="border:2px solid #f5b301;'
                        'background:#fff3b0;border-radius:8px;'
                        'padding:6px 10px;margin-bottom:4px;font-size:13px;">'
                        '🔶 Replied-to message</div>',
                        unsafe_allow_html=True
                    )

                    components.html(
                        f"""
                        <script>
                        var el = window.parent.document.getElementById("group_msg_{message_id}");
                        if (el) {{
                            el.scrollIntoView({{behavior: "smooth", block: "center"}});
                        }}
                        </script>
                        """,
                        height=0
                    )

                if os.path.exists(
                    file_path
                ):

                    st.markdown(
                        f"📎 `{os.path.basename(file_path)}`"
                    )
                    with open(
                        file_path,
                        "rb"
                    ) as f:

                        st.download_button(
                            "⬇️ Download",
                            f,
                            file_name=os.path.basename(
                                file_path
                            ),
                            key=f"group_download_{group_id}_{message_id}"
                        )

                else:

                    st.error(
                        "📎 File not found."
                    )

                st.caption(
                    f"{sender} • {time}"f"{'✓✓ Seen' if seen else '✓ Sent'}"
                )
            with col2:

                def _delete_group_file_message(_mid=message_id, _path=file_path):
                    cursor.execute(
                        """
                        DELETE FROM group_messages
                        WHERE id = ?
                        """,
                        (_mid,)
                    )
                    conn.commit()

                    if os.path.exists(_path):
                        try:
                            os.remove(_path)
                        except:
                            pass

                render_message_actions_menu(
                    key_prefix=f"group_file_{group_id}_{message_id}",
                    reply_state_key="group_reply_to",
                    reply_value=message_id,
                    forward_id_key="group_forward_message_id",
                    forward_content_key="group_forward_message_content",
                    forward_content=str(msg),
                    copy_text=file_path,
                    copy_toast="📋 File path copied",
                    delete_action=_delete_group_file_message
                )

            continue

        # ==========================================
        # TEXT MESSAGE
        # ==========================================

        clean_msg = str(msg)

        clean_msg = clean_msg.replace(
            "<div>",
            ""
        )

        clean_msg = clean_msg.replace(
            "</div>",
            ""
        )

        clean_msg = clean_msg.replace(
            '<div style="',
            ""
        )

        if "font-size:10px" in clean_msg:

            clean_msg = clean_msg.split(
                "font-size:10px"
            )[0]        
    
        # ==========================================
        # MESSAGE
        # ==========================================

        cursor.execute(
        "SELECT seen FROM messages WHERE id = ?",
        (message_id,)
    )

        result = cursor.fetchone()
        seen = result[0] if result else 0

        clean_msg = str(msg)

        clean_msg = clean_msg.replace("<div>", "")
        clean_msg = clean_msg.replace("</div>", "")
        clean_msg = clean_msg.replace("<div style=\"", "")

        if "font-size:10px" in clean_msg:
            clean_msg = clean_msg.split(
                "font-size:10px"
             )[0]

        col1, col2 = st.columns([8, 2])

        with col1:

            if reply_html:
                if st.button(
                    reply_html,
                    key=f"group_jump_to_{group_id}_{message_id}",
                    use_container_width=True
                ):
                    st.session_state["group_highlight_message_id"] = reply_to
                    st.rerun()

            _group_is_highlighted = (
                st.session_state.get("group_highlight_message_id") == message_id
            )

            if sender == user:

                _group_bg_color = "#fff3b0" if _group_is_highlighted else "#d9fdd3"
                _group_border = "border:2px solid #f5b301;" if _group_is_highlighted else ""

                st.markdown(
                    f'<div id="group_msg_{message_id}" style="text-align:right;margin:6px 0;">'
                    f'<span style="display:inline-block;background:{_group_bg_color};'
                    f'padding:8px 12px;border-radius:10px 10px 2px 10px;'
                    f'color:#111;text-align:left;{_group_border}">'
                    f'{html.escape(clean_msg)}'
                    f'<small style="display:block;text-align:right;'
                    f'margin-top:4px;color:#667;">'
                    f'{time} {"✓✓" if seen else "✓"}</small>'
                    f'</span></div>',
                    unsafe_allow_html=True
                )
            else:

                _group_bg_color = "#fff3b0" if _group_is_highlighted else "#ffffff"
                _group_border = "border:2px solid #f5b301;" if _group_is_highlighted else ""

                st.markdown(
                    f'<div id="group_msg_{message_id}" style="text-align:left;margin:6px 0;">'
                    f'<span style="display:inline-block;background:{_group_bg_color};'
                    f'padding:8px 12px;border-radius:10px 10px 10px 2px;'
                    f'color:#111;{_group_border}">'
                    f'{html.escape(clean_msg)}'
                    f'<small style="display:block;margin-top:4px;color:#667;">'
                    f'{time}</small>'
                    f'</span></div>',
                    unsafe_allow_html=True
                )

            if _group_is_highlighted:
                components.html(
                    f"""
                    <script>
                    var el = window.parent.document.getElementById("group_msg_{message_id}");
                    if (el) {{
                        el.scrollIntoView({{behavior: "smooth", block: "center"}});
                    }}
                    </script>
                    """,
                    height=0
                )

        # ==========================================
        # GROUP MESSAGE ACTIONS
        # ==========================================

        with col2:

            def _delete_group_text_message(_mid=message_id):
                cursor.execute(
                    """
                    DELETE FROM group_messages
                    WHERE id = ?
                    """,
                    (_mid,)
                )
                conn.commit()

                if st.session_state.get("group_reply_to") == _mid:
                    st.session_state.pop("group_reply_to", None)

            render_message_actions_menu(
                key_prefix=f"group_text_{group_id}_{message_id}",
                reply_state_key="group_reply_to",
                reply_value=message_id,
                forward_id_key="group_forward_message_id",
                forward_content_key="group_forward_message_content",
                forward_content=str(msg),
                copy_text=clean_msg,
                copy_toast="📋 Message copied",
                delete_action=_delete_group_text_message
            )

    # Clear the "jump to" highlight after this render pass, so it
    # behaves like a one-time flash rather than a permanent marker.
    st.session_state["group_highlight_message_id"] = None

    # ==================================================
    # GROUP MESSAGE INPUT
    # ==================================================

    st.divider()

    # ==============================================
    # REPLY PREVIEW
    # ==============================================

    if st.session_state.get(
        "group_reply_to"
    ):

        reply_id = st.session_state[
            "group_reply_to"
        ]

        cursor.execute(
            """
            SELECT sender, message
            FROM group_messages
            WHERE id = ?
            """,
            (reply_id,)
        )
        reply_data = cursor.fetchone()

        if reply_data:

            reply_sender = reply_data[0]
            reply_message = reply_data[1]

            if str(reply_message).startswith(
                "**VOICE**:"
            ):

                reply_message = "🎤 Voice message"

            elif str(reply_message).startswith(
                "__IMAGE__:"
            ):

                reply_message = "🖼️ Image" 

            elif str(reply_message).startswith(
                "__VIDEO__:"
            ):
                reply_message = "🎥 Video"

            elif str(reply_message).startswith(
                "__FILE__:"
            ):

                reply_message = "📎 File"

            st.info(
                f"↩️ Replying to "
                f"{reply_sender}: "
                f"{reply_message}"
            )

        if st.button(
            "❌ Cancel Reply",
            key=f"cancel_group_reply_{group_id}"
        ):

            st.session_state.pop(
                "group_reply_to",
                None
            )

            st.rerun()

    # ==================================================
    # GROUP FORWARD PANEL
    # ==================================================

    if st.session_state.get("group_forward_message_id"):

        _gf_content = st.session_state.get(
            "group_forward_message_content"
        )

        if str(_gf_content).startswith("**VOICE**:"):
            _gf_preview = "🎤 Voice message"

        elif str(_gf_content).startswith("__IMAGE__:"):
            _gf_preview = "🖼️ Image"

        elif str(_gf_content).startswith("__VIDEO__:"):
            _gf_preview = "🎥 Video"

        elif str(_gf_content).startswith("__FILE__:"):
            _gf_preview = "📎 " + os.path.basename(
                str(_gf_content).split("__FILE__:", 1)[1].strip()
            )

        else:
            _gf_preview = str(_gf_content)

        st.info(f"↗️ Forward: {_gf_preview}")

        _gf_options = []
        _gf_map = {}

        for _gf_gid, _gf_gname, _gf_creator in get_user_groups(user):
            if _gf_gid != group_id:
                _gf_label = f"👥 {_gf_gname}"
                _gf_options.append(_gf_label)
                _gf_map[_gf_label] = ("group", _gf_gid)

        for _gf_friend in get_users(user):
            _gf_label = f"👤 {_gf_friend}"
            _gf_options.append(_gf_label)
            _gf_map[_gf_label] = ("friend", _gf_friend)

        if _gf_options:

            gfcol1, gfcol2, gfcol3 = st.columns([3, 1, 1])

            with gfcol1:

                _gf_target = st.selectbox(
                    "Forward to",
                    _gf_options,
                    key="group_forward_target_select",
                    label_visibility="collapsed"
                )

            with gfcol2:

                if st.button(
                    "Send",
                    key="confirm_group_forward"
                ):

                    _gf_target_type, _gf_target_id = _gf_map[_gf_target]

                    if _gf_target_type == "group":
                        send_group_message(
                            _gf_target_id,
                            user,
                            _gf_content
                        )
                    else:
                        send_message(
                            user,
                            _gf_target_id,
                            _gf_content
                        )

                    st.session_state["group_forward_message_id"] = None
                    st.session_state["group_forward_message_content"] = None

                    st.success(f"Forwarded to {_gf_target.split(' ', 1)[1]}")

                    st.rerun()

            with gfcol3:

                if st.button(
                    "✕ Cancel",
                    key="cancel_group_forward"
                ):

                    st.session_state["group_forward_message_id"] = None
                    st.session_state["group_forward_message_content"] = None

                    st.rerun()

        else:

            st.warning("No other groups or friends to forward to.")

            if st.button(
                "✕ Cancel",
                key="cancel_group_forward_empty"
            ):

                st.session_state["group_forward_message_id"] = None
                st.session_state["group_forward_message_content"] = None

                st.rerun()

    # ==================================================
    # GROUP FOOTER CSS
    # (mirrors the fixed WhatsApp-style header -- pins the
    # message composer to the bottom of the screen so it
    # doesn't move while scrolling through messages.)
    # ==================================================

    st.markdown(
        """
        <style>

        /* ================================================
           FIXED GROUP FOOTER
           ================================================ */

        div.st-key-group_footer_box {
            position: fixed !important;
            bottom: 0 !important;
            left: 0 !important;
            right: 0 !important;

            width: 100% !important;

            z-index: 999999 !important;

            background: rgba(255,255,255,0.97) !important;

            border-top: 1px solid #d1d7db !important;

            padding: 10px 16px 14px 16px !important;

            box-sizing: border-box !important;
        }

        /* ================================================
           SPACE SO THE FIXED FOOTER DOESN'T COVER THE
           LAST MESSAGES
           ================================================ */

        .group-footer-space {
            height: 90px !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* ================================================
           COMPACT FILE UPLOADER (icon-sized, not a big
           drag-and-drop box)
           ================================================ */

        div.st-key-group_footer_box [data-testid="stFileUploaderDropzoneInstructions"] {
            display: none !important;
        }

        div.st-key-group_footer_box [data-testid="stFileUploaderDropzone"] {
            min-height: unset !important;
            height: 38px !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            background: #f0f2f5 !important;
            border-style: solid !important;
        }

        div.st-key-group_footer_box [data-testid="stFileUploaderDropzone"] button {
            font-size: 0 !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            width: 100% !important;
            height: 100% !important;
        }

        div.st-key-group_footer_box [data-testid="stFileUploaderDropzone"] button::before {
            content: "📎";
            font-size: 20px !important;
        }

        div.st-key-group_footer_box [data-testid="stFileUploader"] section {
            padding: 0 !important;
        }

        /* ================================================
           HIDE THE "Press Enter to apply" HINT AND THE
           RED BORDER ON THE UNCOMMITTED TEXT INPUT
           ================================================ */

        div.st-key-group_footer_box [data-testid="InputInstructions"] {
            display: none !important;
        }

        div.st-key-group_footer_box input {
            border-color: #d1d7db !important;
            box-shadow: none !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # Reserve space above the fixed footer so the last
    # message(s) aren't hidden underneath it.
    st.markdown(
        '<div class="group-footer-space"></div>',
        unsafe_allow_html=True
    )

    # ==================================================
    # GROUP CHAT BAR
    # (fixed footer, same pattern as the fixed header --
    # order: message box, voice, attachment, then send)
    # ==================================================

    group_footer_box = st.container(key="group_footer_box")

    with group_footer_box:

        col1, col_emoji, col2, col3, col4 = st.columns(
            [6.3, 0.7, 0.7, 0.7, 0.7],
            vertical_alignment="center"
        )

        # ==============================================
        # TEXT MESSAGE
        # ==============================================

        with col1:

            message = st.text_input(
                "",
                placeholder="Message group...",
                label_visibility="collapsed",
                key=f"group_message_{group_id}"
            )

        # ==============================================
        # EMOJI PICKER
        # ==============================================

        with col_emoji:

            with st.popover("😊"):

                _group_message_key = f"group_message_{group_id}"

                _emoji_options = [
                    "😀", "😂", "😍", "👍", "🙏", "🎉",
                    "❤️", "😢", "😮", "🔥", "👏", "😅",
                    "🤔", "😎", "🙌", "😴"
                ]

                _emoji_cols = st.columns(4)

                for _i, _emoji in enumerate(_emoji_options):

                    with _emoji_cols[_i % 4]:

                        if st.button(
                            _emoji,
                            key=f"group_emoji_{group_id}_{_i}"
                        ):
                            st.session_state[_group_message_key] = (
                                st.session_state.get(_group_message_key, "") + _emoji
                            )
                            st.rerun()

        # ==============================================
        # VOICE MESSAGE (toggle recorder, like 1-on-1 chat)
        # ==============================================

        with col2:

            group_voice_button = st.button(
                "🎤",
                key=f"group_voice_button_{group_id}",
                use_container_width=True
            )

        # ==============================================
        # ATTACHMENT
        # ==============================================

        with col3:

            _group_attachment_version_key = f"group_attachment_version_{group_id}"

            if _group_attachment_version_key not in st.session_state:
                st.session_state[_group_attachment_version_key] = 0

            attachment = st.file_uploader(
                "📎",
                type=[
                    "jpg",
                    "jpeg",
                    "png",
                    "gif",
                    "mp4",
                    "mov",
                    "avi",
                    "pdf",
                    "doc",
                    "docx"
                ],
                key=f"group_attachment_{group_id}_{st.session_state[_group_attachment_version_key]}",
                label_visibility="collapsed"
            )

        # ==============================================
        # SEND BUTTON (after voice + attachment)
        # ==============================================

        with col4:

            send_button = st.button(
                "↑",
                key=f"group_send_{group_id}",
                use_container_width=True
            )
    # ==================================================
    # SEND GROUP MESSAGE
    # ==================================================

    if send_button:

        # ----------------------------------------------
        # TEXT
        # ----------------------------------------------

        if message.strip():

            reply_to = st.session_state.get(
                "group_reply_to"
            )

            send_group_message(
                group_id,
                user,
                message.strip(),
                reply_to=reply_to
            )
            st.session_state.pop(
                "group_reply_to",
                None
            )

            st.rerun()

        # ----------------------------------------------
        # ATTACHMENT
        # ----------------------------------------------

        elif attachment is not None:

            os.makedirs(
                "group_media",
                exist_ok=True
            )

            file_name = (
                f"{group_id}_"
                f"{random.randint(100000,999999)}_"
                f"{attachment.name}"
            )

            file_path = os.path.join(
                "group_media",
                file_name
            )

            with open(
                file_path,
                "wb"
            ) as f:

                f.write(
                    attachment.getbuffer()
                )

            file_ext = (
                attachment.name
                .split(".")[-1]
                .lower()
            )

            # IMAGE

            if file_ext in [
                "jpg",
                "jpeg",
                "png",
                "gif"
            ]:
                group_message = (
                    "__IMAGE__:"
                    + file_path
                )

            # VIDEO

            elif file_ext in [
                "mp4",
                "mov",
                "avi"
            ]:

                group_message = (
                    "__VIDEO__:"
                    + file_path
                )
            # OTHER FILE

            else:

                group_message = (
                    "__FILE__:"
                    + file_path
                )

            reply_to = st.session_state.get( 
                "group_reply_to"
            )

            send_group_message(
                group_id,
                user,
                group_message,
                reply_to=reply_to
            )

            st.session_state.pop(
                "group_reply_to",
                None
            )

            st.session_state[_group_attachment_version_key] += 1

            st.rerun()

    # ==================================================
    # GROUP VOICE RECORDER (same pattern as 1-on-1 chat)
    # ==================================================

    _g_recording_key = f"group_recording_active_{group_id}"
    _g_recorder_version_key = f"group_voice_recorder_version_{group_id}"
    _g_saved_audio_key = f"group_saved_voice_audio_{group_id}"

    if _g_recording_key not in st.session_state:
        st.session_state[_g_recording_key] = False

    if _g_recorder_version_key not in st.session_state:
        st.session_state[_g_recorder_version_key] = 0

    if _g_saved_audio_key not in st.session_state:
        st.session_state[_g_saved_audio_key] = None

    if group_voice_button:
        st.session_state[_g_recording_key] = True
        st.rerun()

    if st.session_state[_g_recording_key]:

        group_voice_audio = st.audio_input(
            "🎤 Record voice",
            key=f"group_voice_recorder_{group_id}_{st.session_state[_g_recorder_version_key]}"
        )

        if group_voice_audio:

            st.audio(
                group_voice_audio,
                format="audio/wav"
            )

            st.session_state[_g_saved_audio_key] = group_voice_audio

            st.success("🎤 Voice recording ready!")

            # ------------------------------------------
            # SEND VOICE
            # ------------------------------------------

            if st.button(
                "↑ Send Voice",
                key=f"group_send_voice_{group_id}"
            ):

                _g_audio_file = st.session_state.get(_g_saved_audio_key)

                if _g_audio_file:

                    audio_bytes = _g_audio_file.getvalue()

                    os.makedirs("group_voice", exist_ok=True)

                    voice_path = os.path.join(
                        "group_voice",
                        f"{group_id}_{random.randint(100000, 999999)}.wav"
                    )

                    with open(voice_path, "wb") as f:
                        f.write(audio_bytes)

                    group_message = "**VOICE**:" + voice_path

                    reply_to = st.session_state.get("group_reply_to")

                    send_group_message(
                        group_id,
                        user,
                        group_message,
                        reply_to=reply_to
                    )

                    st.session_state.pop("group_reply_to", None)
                    st.session_state[_g_saved_audio_key] = None
                    st.session_state[_g_recording_key] = False
                    st.session_state[_g_recorder_version_key] += 1

                    st.rerun()

            # ------------------------------------------
            # DELETE RECORDING
            # ------------------------------------------

            if st.button(
                "🗑️ Delete Recording",
                key=f"group_delete_voice_recording_{group_id}"
            ):

                st.session_state[_g_saved_audio_key] = None
                st.session_state[_g_recording_key] = False
                st.session_state[_g_recorder_version_key] += 1

                st.rerun()

    st.stop()
# ==========================================
# MARK MESSAGES AS SEEN
# ==========================================

friend = st.session_state.get("selected_friend")

if friend:

    cursor.execute(
        """
        UPDATE messages
        SET seen = 1
        WHERE sender = ?
          AND receiver = ?
          AND seen = 0
        """,
        (
            friend,
            user
        )
    )

    conn.commit()


# ========================================== 
# GET MESSAGES
# ==========================================

messages = get_messages(
    user,
    friend
)

    
# =========================
# DISPLAY MESSAGES
# =========================

for message_id, sender, msg, time, reply_to in get_messages(
    user,
    friend
):
    time = to_local_time_str(time)

    # ==========================================
    # GET SEEN STATUS
    # ==========================================

    cursor.execute(
        """
        SELECT seen
        FROM messages
        WHERE id = ?
        """,
        (message_id,)
    )

    result = cursor.fetchone()

    seen = result[0] if result else 0

    # ==========================================
    # SHOW REPLIED MESSAGE (computed once per
    # message, used by every message type below)
    # ==========================================

    reply_html = ""
    if reply_to is not None:
        cursor.execute(
            """
            SELECT sender, message
            FROM messages
            WHERE id = ?
            """,
            (reply_to,)
        )
        reply_data = cursor.fetchone()
        if reply_data:
            reply_sender = reply_data[0]
            reply_text = reply_data[1]
            # Voice message
            if str(reply_text).startswith("**VOICE**:"):
                reply_text = "🎤 Voice message"
            # Image message
            elif str(reply_text).startswith("__IMAGE__:"):
                reply_text = "🖼️ Image"
            elif str(reply_text).startswith("__VIDEO__:"):
                reply_text = "🎥 Video"
            elif str(reply_text).startswith("__FILE__:"):
                reply_text = "📎 " + os.path.basename(
                    str(reply_text).split("__FILE__:", 1)[1].strip()
                )
            reply_html = f"↩️ {reply_sender}: {reply_text}"

    # ==========================================
    # VOICE MESSAGE
    # ==========================================

    if str(msg).startswith("**VOICE**:"):

            audio_path = str(msg).split(
                "**VOICE**:",
                1
            )[1].strip()
            
            
            # GET SEEN STATUS
            
            cursor.execute(
            "SELECT seen FROM messages WHERE id = ?",
            (message_id,)
            )
            result = cursor.fetchone()
            seen = result[0] if result else 0

            col1, col2 = st.columns([8, 1])

            with col1:

                if reply_html:
                    if st.button(
                        reply_html,
                        key=f"jump_to_voice_{message_id}",
                        use_container_width=True
                    ):
                        st.session_state["highlight_message_id"] = reply_to
                        st.rerun()

                if st.session_state.get("highlight_message_id") == message_id:
                    st.markdown(
                        f'<div id="msg_{message_id}" style="border:2px solid #f5b301;'
                        'background:#fff3b0;border-radius:8px;'
                        'padding:6px 10px;margin-bottom:4px;font-size:13px;">'
                        '🔶 Replied-to message</div>',
                        unsafe_allow_html=True
                    )

                    components.html(
                        f"""
                        <script>
                        var el = window.parent.document.getElementById("msg_{message_id}");
                        if (el) {{
                            el.scrollIntoView({{behavior: "smooth", block: "center"}});
                        }}
                        </script>
                        """,
                        height=0
                    )

                if os.path.exists(audio_path):

                    st.audio(
                        audio_path,
                        format="audio/wav"
                    )
                else:
                        st.error(
                    "🎵 Audio file not found."
                )   
                    # SENT / SEEN STATUS
                if sender == user:

                    if seen == 1:

                        st.caption(
                            f"{time}  ✓✓ Seen"
                        )

                    else:

                        st.caption(
                            f"{time}  ✓ Sent"
                        )
                else:
                    st.caption(time)

            with col2:

                def _delete_voice_message(_mid=message_id, _path=audio_path):
                    delete_message(_mid)
                    if os.path.exists(_path):
                        try:
                            os.remove(_path)
                        except:
                            pass

                render_message_actions_menu(
                    key_prefix=f"voice_{message_id}",
                    reply_state_key="reply_to",
                    reply_value=int(message_id),
                    forward_id_key="forward_message_id",
                    forward_content_key="forward_message_content",
                    forward_content=str(msg),
                    copy_text=audio_path,
                    copy_toast="📋 Voice message path copied",
                    delete_action=_delete_voice_message
                )

            continue
        
            


    # ==========================================
    # IMAGE MESSAGE
    # ADD THIS BLOCK HERE
    # ==========================================

    if str(msg).startswith("__IMAGE__:"):

        image_path = str(msg).split(
            "__IMAGE__:",
            1
        )[1].strip()

        col1, col2 = st.columns([8, 1])

        with col1:

            if reply_html:
                if st.button(
                    reply_html,
                    key=f"jump_to_image_{message_id}",
                    use_container_width=True
                ):
                    st.session_state["highlight_message_id"] = reply_to
                    st.rerun()

            if os.path.exists(image_path):

                if sender == user:

                    left, right = st.columns([3, 5])

                    with right:

                        st.image(
                            image_path,
                            width=300
                        )

                        st.caption(
                            f"{time}"
                            f"{'✓✓ Seen' if seen else '✓ Sent'}"
                        )

                else:

                    left, right = st.columns([5, 3])

                    with left:

                        st.image(
                            image_path,
                            width=300
                        )

                        if sender == user:
                            st.caption(
                                f"{time}  "
                                 
                                )
                        else:
                             st.caption(time)

            else:

                st.error("🖼️ Image file not found.")

        with col2:

            def _delete_image_message(_mid=message_id, _path=image_path):
                delete_message(_mid)
                if os.path.exists(_path):
                    try:
                        os.remove(_path)
                    except:
                        pass

            render_message_actions_menu(
                key_prefix=f"image_{message_id}",
                reply_state_key="reply_to",
                reply_value=int(message_id),
                forward_id_key="forward_message_id",
                forward_content_key="forward_message_content",
                forward_content=str(msg),
                copy_text=image_path,
                copy_toast="📋 Image path copied",
                delete_action=_delete_image_message
            )

        # IMPORTANT
        # Prevent image path from appearing as text
        continue


    # ==========================================
    # VIDEO MESSAGE
    # ADD THIS BLOCK HERE
    # ==========================================

    if str(msg).startswith("__VIDEO__:"):

        video_path = str(msg).split(
            "__VIDEO__:",
            1
        )[1].strip()

        col1, col2 = st.columns([8, 1])

        with col1:

            if reply_html:
                if st.button(
                    reply_html,
                    key=f"jump_to_video_{message_id}",
                    use_container_width=True
                ):
                    st.session_state["highlight_message_id"] = reply_to
                    st.rerun()

            if os.path.exists(video_path):

                if sender == user:
                    left, right = st.columns([3, 5])

                    with right:

                        st.video(
                            video_path
                        )

                        st.caption(
                            f"{time}  "
                            f"{'✓✓ Seen' if seen else '✓ Sent'}"
                        )

                else:

                    left, right = st.columns([5, 3])

                    with left:

                        st.video(
                            video_path
                        )

                        st.caption(time)

            else:

                st.error("🎥 Video file not found.")

        with col2:

            def _delete_video_message(_mid=message_id, _path=video_path):
                delete_message(_mid)
                if os.path.exists(_path):
                    try:
                        os.remove(_path)
                    except:
                        pass

            render_message_actions_menu(
                key_prefix=f"video_{message_id}",
                reply_state_key="reply_to",
                reply_value=int(message_id),
                forward_id_key="forward_message_id",
                forward_content_key="forward_message_content",
                forward_content=str(msg),
                copy_text=video_path,
                copy_toast="📋 Video path copied",
                delete_action=_delete_video_message
            )

        # IMPORTANT
        # Prevent video path from appearing as text
        continue

    # ==========================================
    # FILE MESSAGE (PDF / DOC / OTHER DOCUMENTS)
    # ==========================================

    if str(msg).startswith("__FILE__:"):

        file_path = str(msg).split(
            "__FILE__:",
            1
        )[1].strip()

        col1, col2 = st.columns([8, 1])

        with col1:

            if reply_html:
                if st.button(
                    reply_html,
                    key=f"jump_to_file_{message_id}",
                    use_container_width=True
                ):
                    st.session_state["highlight_message_id"] = reply_to
                    st.rerun()

            if os.path.exists(file_path):

                file_display_name = os.path.basename(file_path)

                icon = (
                    "📕"
                    if file_display_name.lower().endswith(".pdf")
                    else "📎"
                )

                st.markdown(
                    f"{icon} `{file_display_name}`"
                )

                with open(file_path, "rb") as f:

                    st.download_button(
                        "⬇️ Download",
                        f,
                        file_name=file_display_name,
                        key=f"download_file_{message_id}"
                    )

                if sender == user:

                    if seen == 1:
                        st.caption(f"{time}  ✓✓ Seen")
                    else:
                        st.caption(f"{time}  ✓ Sent")

                else:
                    st.caption(time)

            else:

                st.error("📎 File not found.")

        with col2:

            def _delete_file_message(_mid=message_id, _path=file_path):
                delete_message(_mid)
                if os.path.exists(_path):
                    try:
                        os.remove(_path)
                    except:
                        pass

            render_message_actions_menu(
                key_prefix=f"file_{message_id}",
                reply_state_key="reply_to",
                reply_value=int(message_id),
                forward_id_key="forward_message_id",
                forward_content_key="forward_message_content",
                forward_content=str(msg),
                copy_text=file_path,
                copy_toast="📋 File path copied",
                delete_action=_delete_file_message
            )

        # IMPORTANT
        # Prevent file path from appearing as text
        continue

     

    # =========================
    # TEXT MESSAGE
    # =========================

    cursor.execute(
        "SELECT seen FROM messages WHERE id = ?",
        (message_id,)
    )

    result = cursor.fetchone()
    seen = result[0] if result else 0

    clean_msg = str(msg)

    clean_msg = clean_msg.replace("<div>", "")
    clean_msg = clean_msg.replace("</div>", "")
    clean_msg = clean_msg.replace("<div style=\"", "")

    if "font-size:10px" in clean_msg:
        clean_msg = clean_msg.split(
            "font-size:10px"
        )[0]

    col1, col2 = st.columns([8, 1]) 
    


    

    with col1:

        if reply_html:
            if st.button(
                reply_html,
                key=f"jump_to_{message_id}",
                use_container_width=True
            ):
                st.session_state["highlight_message_id"] = reply_to
                st.rerun()

        _is_highlighted = (
            st.session_state.get("highlight_message_id") == message_id
        )

        if sender == user:

            _bg_color = "#fff3b0" if _is_highlighted else "#d9fdd3"
            _border = "border:2px solid #f5b301;" if _is_highlighted else ""

            st.markdown(
                f'<div id="msg_{message_id}" style="text-align:right;margin:6px 0;">'
                f'<span style="display:inline-block;background:{_bg_color};'
                f'padding:8px 12px;border-radius:10px 10px 2px 10px;'
                f'color:#111;text-align:left;{_border}">'
                f'{html.escape(clean_msg)}'
                f'<small style="display:block;text-align:right;'
                f'margin-top:4px;color:#667;">'
                f'{time} {"✓✓" if seen else "✓"}</small>'
                f'</span></div>',
                unsafe_allow_html=True
            )

        else:

            _bg_color = "#fff3b0" if _is_highlighted else "#ffffff"
            _border = "border:2px solid #f5b301;" if _is_highlighted else ""

            st.markdown(
                f'<div id="msg_{message_id}" style="text-align:left;margin:6px 0;">'
                f'<span style="display:inline-block;background:{_bg_color};'
                f'padding:8px 12px;border-radius:10px 10px 10px 2px;'
                f'color:#111;{_border}">'
                f'{html.escape(clean_msg)}'
                f'<small style="display:block;margin-top:4px;color:#667;">'
                f'{time}</small>'
                f'</span></div>',
                unsafe_allow_html=True
            )

        if _is_highlighted:
            components.html(
                f"""
                <script>
                var el = window.parent.document.getElementById("msg_{message_id}");
                if (el) {{
                    el.scrollIntoView({{behavior: "smooth", block: "center"}});
                }}
                </script>
                """,
                height=0
            )
            
    
        
    

    

        
   


        # ================= TIME / SEEN =================

        if sender == user:

            if seen == 1:

                st.caption(
                    f"{time}  ✓✓ Seen"
                )

            else:

                st.caption(
                    f"{time}  ✓ Sent"
                )

        else:

            st.caption(time)

    # ================= ACTIONS =================

    with col2:

        render_message_actions_menu(
            key_prefix=f"text_{message_id}",
            reply_state_key="reply_to",
            reply_value=int(message_id),
            forward_id_key="forward_message_id",
            forward_content_key="forward_message_content",
            forward_content=str(msg),
            copy_text=clean_msg,
            copy_toast="📋 Message copied",
            delete_action=lambda: delete_message(message_id)
        )


# Clear the "jump to" highlight after this render pass, so it
# behaves like a one-time flash rather than a permanent marker.
st.session_state["highlight_message_id"] = None


# ==================================================
# CHAT INPUT
# ==================================================

def send_chat_message(message):

    message = message.strip()

    if not message:
        return

    # Get selected message ID
    reply_id = st.session_state.get(
        "reply_to",
        None
    )

    # Send message with reply ID
    send_message(
        user,
        friend,
        message,
        reply_to=reply_id
    )

    # Clear reply selection
    st.session_state["reply_to"] = None

    # Refresh chat
    st.rerun()

# ==================================================
# REPLY PREVIEW
# ==================================================

reply_id = st.session_state.get("reply_to")

if reply_id:

    cursor.execute(
        """
        SELECT sender, message
        FROM messages
        WHERE id = ?
        """,
        (reply_id,)
    )

    reply_data = cursor.fetchone()

    if reply_data:

        reply_sender, reply_message = reply_data

        # Don't show the full voice path
        if str(reply_message).startswith("**VOICE**:"):

            reply_message = "🎤 Voice message"

        elif str(reply_message).startswith("__IMAGE__:"):

            reply_message = "🖼️ Image"

        elif str(reply_message).startswith("__VIDEO__:"):

            reply_message = "🎥 Video"

        elif str(reply_message).startswith("__FILE__:"):

            reply_message = "📎 " + os.path.basename(
                str(reply_message).split("__FILE__:", 1)[1].strip()
            )

        st.info(f"↩️ Replying to {reply_sender}: {reply_message}")
    else:
            st.session_state["reply_to"] = None

    if st.button(
        "✕ Cancel Reply",
        key="cancel_reply"
    ):

        st.session_state["reply_to"] = None

        st.rerun()

# ==================================================
# FORWARD MESSAGE PANEL
# ==================================================

if st.session_state.get("forward_message_id"):

    forward_content = st.session_state.get(
        "forward_message_content"
    )

    # Preview label for what's being forwarded

    if str(forward_content).startswith("**VOICE**:"):
        forward_preview = "🎤 Voice message"

    elif str(forward_content).startswith("__IMAGE__:"):
        forward_preview = "🖼️ Image"

    elif str(forward_content).startswith("__VIDEO__:"):
        forward_preview = "🎥 Video"

    elif str(forward_content).startswith("__FILE__:"):
        forward_preview = "📎 " + os.path.basename(
            str(forward_content).split("__FILE__:", 1)[1].strip()
        )

    else:
        forward_preview = str(forward_content)

    st.info(f"↗️ Forward: {forward_preview}")

    forward_targets = [
        u for u in get_users(user) if u != friend
    ]

    if forward_targets:

        fcol1, fcol2, fcol3 = st.columns([3, 1, 1])

        with fcol1:

            forward_to = st.selectbox(
                "Forward to",
                forward_targets,
                key="forward_target_select",
                label_visibility="collapsed"
            )

        with fcol2:

            if st.button(
                "Send",
                key="confirm_forward"
            ):

                send_message(
                    user,
                    forward_to,
                    forward_content
                )

                st.session_state["forward_message_id"] = None
                st.session_state["forward_message_content"] = None

                st.success(f"Forwarded to {forward_to}")

                st.rerun()

        with fcol3:

            if st.button(
                "✕ Cancel",
                key="cancel_forward"
            ):

                st.session_state["forward_message_id"] = None
                st.session_state["forward_message_content"] = None

                st.rerun()

    else:

        st.warning("No other users to forward to.")

        if st.button(
            "✕ Cancel",
            key="cancel_forward_empty"
        ):

            st.session_state["forward_message_id"] = None
            st.session_state["forward_message_content"] = None

            st.rerun()

# ==================================================
# CHAT FOOTER CSS
# (identical to the group chat's fixed footer -- pins
# the message composer to the bottom of the screen so
# it doesn't move while scrolling through messages.)
# ==================================================

st.markdown(
    """
    <style>

    /* ================================================
       FIXED CHAT FOOTER
       ================================================ */

    div.st-key-chat_footer_box {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;

        width: 100% !important;

        z-index: 999999 !important;

        background: rgba(255,255,255,0.97) !important;

        border-top: 1px solid #d1d7db !important;

        padding: 10px 16px 14px 16px !important;

        box-sizing: border-box !important;
    }

    /* ================================================
       SPACE SO THE FIXED FOOTER DOESN'T COVER THE
       LAST MESSAGES
       ================================================ */

    .chat-footer-space {
        height: 90px !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    /* ================================================
       COMPACT FILE UPLOADER (icon-sized, not a big
       drag-and-drop box)
       ================================================ */

    div.st-key-chat_footer_box [data-testid="stFileUploaderDropzoneInstructions"] {
        display: none !important;
    }

    div.st-key-chat_footer_box [data-testid="stFileUploaderDropzone"] {
        min-height: unset !important;
        height: 38px !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        background: #f0f2f5 !important;
        border-style: solid !important;
    }

    div.st-key-chat_footer_box [data-testid="stFileUploaderDropzone"] button {
        font-size: 0 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        width: 100% !important;
        height: 100% !important;
    }

    div.st-key-chat_footer_box [data-testid="stFileUploaderDropzone"] button::before {
        content: "📎";
        font-size: 20px !important;
    }

    div.st-key-chat_footer_box [data-testid="stFileUploader"] section {
        padding: 0 !important;
    }

    /* ================================================
       HIDE THE "Press Enter to apply" HINT AND THE
       RED BORDER ON THE UNCOMMITTED TEXT INPUT
       ================================================ */

    div.st-key-chat_footer_box [data-testid="InputInstructions"] {
        display: none !important;
    }

    div.st-key-chat_footer_box input {
        border-color: #d1d7db !important;
        box-shadow: none !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# Reserve space above the fixed footer so the last
# message(s) aren't hidden underneath it.
st.markdown(
    '<div class="chat-footer-space"></div>',
    unsafe_allow_html=True
)

# ==================================================
# CHAT BAR
# (fixed footer, same pattern as the group chat --
# order: message box, voice, attachment, then send)
# ==================================================

chat_footer_box = st.container(key="chat_footer_box")

with chat_footer_box:

    col1, col_emoji, col2, col3, col4 = st.columns(
        [6.3, 0.7, 0.7, 0.7, 0.7],
        vertical_alignment="center"
    )

    # ==============================================
    # TEXT MESSAGE
    # ==============================================

    with col1:

        message = st.text_input(
            "",
            placeholder="Message...",
            label_visibility="collapsed",
            key=f"chat_message_{friend}"
        )

    # ==============================================
    # EMOJI PICKER
    # ==============================================

    with col_emoji:

        with st.popover("😊"):

            _chat_message_key = f"chat_message_{friend}"

            _emoji_options = [
                "😀", "😂", "😍", "👍", "🙏", "🎉",
                "❤️", "😢", "😮", "🔥", "👏", "😅",
                "🤔", "😎", "🙌", "😴"
            ]

            _emoji_cols = st.columns(4)

            for _i, _emoji in enumerate(_emoji_options):

                with _emoji_cols[_i % 4]:

                    if st.button(
                        _emoji,
                        key=f"chat_emoji_{friend}_{_i}"
                    ):
                        st.session_state[_chat_message_key] = (
                            st.session_state.get(_chat_message_key, "") + _emoji
                        )
                        st.rerun()

    # ==============================================
    # VOICE MESSAGE
    # ==============================================

    with col2:

        voice_button = st.button(
            "🎤",
            key=f"voice_button_{friend}",
            use_container_width=True
        )

    # ==============================================
    # ATTACHMENT (inline, compact -- like group chat)
    # ==============================================

    with col3:

        _media_upload_version_key = f"media_upload_version_{friend}"

        if _media_upload_version_key not in st.session_state:
            st.session_state[_media_upload_version_key] = 0

        media_file = st.file_uploader(
            "📎",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp",
                "mp4",
                "mov",
                "webm",
                "pdf",
                "doc",
                "docx",
                "txt",
                "xlsx",
                "ppt",
                "pptx"
            ],
            key=f"media_upload_{friend}_{st.session_state[_media_upload_version_key]}",
            label_visibility="collapsed"
        )

    # ==============================================
    # SEND BUTTON (after voice + attachment)
    # ==============================================

    with col4:

        send_button = st.button(
            "↑",
            key=f"chat_send_{friend}",
            use_container_width=True
        )

# ==================================================
# SEND TEXT MESSAGE / MEDIA
# (only on an explicit Send click -- not on every
# rerun -- so an attachment doesn't get re-sent
# repeatedly while it's still sitting in the uploader)
# ==================================================

if send_button:

    if message.strip():

        send_chat_message(message)

        st.rerun()

    elif media_file is not None:

        os.makedirs(
            "chat_media",
            exist_ok=True
        )

        extension = os.path.splitext(
            media_file.name
        )[1].lower()

        filename = (
            f"{uuid.uuid4().hex}{extension}"
        )

        filepath = os.path.abspath(
            os.path.join(
                "chat_media",
                filename
            )
        )


        # SAVE FILE

        with open(
            filepath,
            "wb"
        ) as f:

            f.write(
                media_file.getbuffer()
            )


        # ==================================================
        # IMAGE
        # ==================================================

        if extension in [
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        ]:

            media_message = (
                "__IMAGE__:" + filepath
            )


        # ==================================================
        # VIDEO
        # ==================================================

        elif extension in [
            ".mp4",
            ".mov",
            ".webm"
        ]:

            media_message = (
                "__VIDEO__:" + filepath
            )

        # ==================================================
        # FILE (PDF / DOC / OTHER DOCUMENTS)
        # ==================================================

        else:

            media_message = (
                "__FILE__:" + filepath
            )


        # ==========================================
        # SEND MESSAGE (supports replying to media too)
        # ==========================================

        send_message(
            user,
            friend,
            media_message,
            reply_to=st.session_state.get("reply_to")
        )

        st.session_state["reply_to"] = None

        st.session_state[_media_upload_version_key] += 1

        st.rerun()

# ==================================================
# INITIALIZE VOICE SESSION STATE
# ==================================================

recording_key = f"recording_active_{friend}"
recorder_version_key = f"voice_recorder_version_{friend}"
saved_audio_key = f"saved_voice_audio_{friend}"


if recording_key not in st.session_state:
    st.session_state[recording_key] = False

if recorder_version_key not in st.session_state:
    st.session_state[recorder_version_key] = 0

if saved_audio_key not in st.session_state:
    st.session_state[saved_audio_key] = None


# ==================================================
# OPEN RECORDER
# ==================================================

if voice_button:

    st.session_state[recording_key] = True

    st.rerun()


# ==================================================
# RECORDING ACTIVE
# ==================================================

if st.session_state[recording_key]:

    voice_audio = st.audio_input(
        "🎤 Record voice",
        key=f"voice_recorder_{friend}_{st.session_state[recorder_version_key]}"
    )


    # ==============================================
    # RECORDING AVAILABLE
    # ==============================================

    if voice_audio:

        st.audio(
            voice_audio,
            format="audio/wav"
        )

        st.session_state[saved_audio_key] = voice_audio 

        st.success(
            "🎤 Voice recording ready!"
        )


        # ==========================================
        # SEND VOICE
        # ==========================================

        if st.button(
            "↑ Send Voice",
            key=f"send_voice_{friend}"
        ):

            audio_file = st.session_state.get(
                saved_audio_key
            )

            if audio_file:
                # ==================================
                # GET ACTUAL AUDIO BYTES
                # ==================================

                audio_bytes = audio_file.getvalue()

                # ==================================
                # SAVE AUDIO TO DATABASE
                # (carries along any pending reply)
                # ==================================

                voice_reply_id = st.session_state.get("reply_to")

                send_message(
                    user,
                    friend,
                    "",
                    audio_bytes,
                    reply_to=voice_reply_id
                )

                st.session_state["reply_to"] = None

                # ==================================
                # CLEAR AUDIO PREVIEW
                # ==================================

                st.session_state[saved_audio_key] = None

                # ==================================
                # CLOSE RECORDER
                # ==================================

                st.session_state[recording_key] = False

                # ==================================
                # CREATE NEW RECORDER
                # ==================================

                st.session_state[
                    recorder_version_key
                ] += 1

                # ==================================
                # REFRESH
                # ==================================

                st.rerun()


        # ==========================================
        # DELETE RECORDING
        # ==========================================

        if st.button(
            "🗑️ Delete Recording",
            key=f"delete_voice_recording_{friend}"
        ):

            st.session_state[saved_audio_key] = None

            st.session_state[recording_key] = False

            st.session_state[
                recorder_version_key
            ] += 1

            st.rerun()


# ==================================================
# RECORDER NOT ACTIVE
# ==================================================

else:

    st.info(
        "🎤 Tap the voice button to start recording."
    )
