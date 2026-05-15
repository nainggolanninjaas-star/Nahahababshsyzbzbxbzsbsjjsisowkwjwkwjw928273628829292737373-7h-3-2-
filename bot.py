#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ╔══════════════════════════════════════════════════════════╗
# ║     FELICIA AI V3.0 — ULTIMATE CODING ASSISTANT        ║
# ║     ©Felicia | Auto-Learn • Auto-Fix • Auto-Code       ║
# ║     Railway Ready • Beautiful UI • Super Fast           ║
# ╚══════════════════════════════════════════════════════════╝

import asyncio, os, re, json, time, zipfile, shutil, signal, subprocess
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode
from groq import Groq

# ╔══════════════════════════════════════════════════════════╗
# ║                    🔧 CONFIG                             ║
# ╚══════════════════════════════════════════════════════════╝

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8582250210:AAHZWkAW0OmMtRa3ut-cQ3gUUYvmPhkmlR8")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
ADMIN_ID = int(os.getenv("ADMIN_ID", "8491120925"))
BOTS_DIR = os.getenv("BOTS_DIR", "/data/user_bots")  # Railway persistent storage
VERSION = "3.0.0"

# ╔══════════════════════════════════════════════════════════╗
# ║                    END CONFIG                            ║
# ╚══════════════════════════════════════════════════════════╝

# Buat folder bots kalo belum ada
Path(BOTS_DIR).mkdir(parents=True, exist_ok=True)

client = Groq(api_key=GROQ_API_KEY)

# ╔══════════════════════════════════════════════════════════╗
# ║              FELICIA SYSTEM PROMPT                       ║
# ╚══════════════════════════════════════════════════════════╝

FELICIA_PROMPT = """
[ANDA ADALAH FELICIA — AI CODING ASSISTANT PALING CANGGIH]

Anda adalah Felicia V3, AI super cerdas yang menguasai semua bahasa pemrograman.

KEPRIBADIAN:
- Ramah, sabar, profesional, humoris
- Selalu semangat membantu
- Menjelaskan dengan detail & mudah dipahami
- Menggunakan bahasa Indonesia santai + emoji
- Kode menggunakan bahasa Inggris (standar industri)

KEAHLIAN UTAMA:
1. 📖 MEMBACA FILE — Analisis isi file dengan statistik lengkap
2. 🔧 MEMPERBAIKI KODE — Deteksi error → Fix otomatis
3. 📝 MEMBUAT KODE — Dari deskripsi jadi kode siap pakai
4. ➕ MENAMBAH FITUR — Tambah fitur tanpa rusak yang lama
5. 🔍 MENGANALISIS KODE — Cari bug, warning, best practice
6. 🔄 MEROMBAK KODE — Refactor total / rewrite / convert bahasa
7. 🌐 MENCARI REFERENSI — Dokumentasi, tutorial, contoh kode
8. 💬 BERDISKUSI — Ngobrol santai tentang koding

ATURAN WAJIB:
1. SELALU tanyakan keluhan sebelum memperbaiki
2. SELALU tanyakan "Ada lagi?" sebelum mulai
3. SELALU tambahkan WATERMARK ©Felicia di setiap file output
4. Kirim ZIP jika lebih dari 1 file
5. Rekomendasikan bahasa pemrograman terbaik
6. Beritahu user config yang harus diisi (API key, token, dll)

WATERMARK FORMAT (letakkan di baris paling bawah setiap file):
# ┌──────────────────────────────────────────┐
# │  © Felicia AI V3.0 — Auto-Generated     │
# │  Generated: {timestamp}          │
# │  "Making coding beautiful & easy"        │
# └──────────────────────────────────────────┘
"""

# ╔══════════════════════════════════════════════════════════╗
# ║              LANGUAGE DETECTION                          ║
# ╚══════════════════════════════════════════════════════════╝

LANG_MAP = {
    '.py': ('Python', 'python', '🐍'),
    '.js': ('JavaScript', 'javascript', '💛'),
    '.ts': ('TypeScript', 'typescript', '💙'),
    '.html': ('HTML', 'html', '🌐'),
    '.css': ('CSS', 'css', '🎨'),
    '.json': ('JSON', 'json', '📋'),
    '.md': ('Markdown', 'markdown', '📝'),
    '.xml': ('XML', 'xml', '📄'),
    '.yml': ('YAML', 'yaml', '⚙️'),
    '.yaml': ('YAML', 'yaml', '⚙️'),
    '.env': ('Environment', 'env', '🔒'),
    '.log': ('Log File', 'log', '📊'),
    '.txt': ('Text', 'text', '📃'),
    '.ini': ('INI Config', 'ini', '🔧'),
    '.cfg': ('Config', 'cfg', '🔧'),
    '.sh': ('Bash', 'bash', '💻'),
    '.bash': ('Bash', 'bash', '💻'),
    '.php': ('PHP', 'php', '🐘'),
    '.java': ('Java', 'java', '☕'),
    '.cpp': ('C++', 'cpp', '⚡'),
    '.c': ('C', 'c', '⚙️'),
    '.go': ('Go', 'go', '🔵'),
    '.rs': ('Rust', 'rust', '🦀'),
    '.swift': ('Swift', 'swift', '🍎'),
    '.sql': ('SQL', 'sql', '🗄️'),
    '.r': ('R', 'r', '📈'),
    '.rb': ('Ruby', 'ruby', '💎'),
    '.dart': ('Dart', 'dart', '🎯'),
    '.kt': ('Kotlin', 'kotlin', '💜'),
}

SUPPORTED_READ = ['.py', '.js', '.ts', '.html', '.css', '.json', '.md', '.xml', '.yml', '.yaml', 
                  '.env', '.log', '.txt', '.ini', '.cfg', '.sh', '.php', '.java', '.cpp', '.c',
                  '.go', '.rs', '.swift', '.sql', '.r', '.rb']

SUPPORTED_FIX = ['.py', '.js', '.ts', '.html', '.css', '.php', '.java', '.cpp', '.go', '.rs', '.swift', '.rb']

# ╔══════════════════════════════════════════════════════════╗
# ║              STORAGE                                     ║
# ╚══════════════════════════════════════════════════════════╝

user_state = {}   # {user_id: {state, files, complaints, features, lang, ref}}
user_memory = {}  # {user_id: [{role, content}]}

# ╔══════════════════════════════════════════════════════════╗
# ║              HELPER FUNCTIONS                            ║
# ╚══════════════════════════════════════════════════════════╝

def add_watermark(code, lang="python"):
    """Tambahkan watermark ©Felicia"""
    wm = f"""
# ┌──────────────────────────────────────────┐
# │  © Felicia AI V3.0 — Auto-Generated     │
# │  Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}              │
# │  "Making coding beautiful & easy"        │
# └──────────────────────────────────────────┘"""
    return code.rstrip() + "\n" + wm

def get_file_info(filename, content):
    """Dapetin info file lengkap"""
    lang_info = LANG_MAP.get(Path(filename).suffix.lower(), ('Unknown', 'text', '❓'))
    lines = content.split('\n')
    return {
        'name': filename,
        'language': lang_info[0],
        'lang_code': lang_info[1],
        'emoji': lang_info[2],
        'lines': len(lines),
        'words': len(content.split()),
        'chars': len(content),
        'size_kb': round(len(content.encode('utf-8')) / 1024, 2),
        'ext': Path(filename).suffix.lower()
    }

def create_zip(files_dict):
    """Bikin ZIP"""
    buf = BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, content in files_dict.items():
            zf.writestr(name, content)
    buf.seek(0)
    return buf

def split_long_message(text, max_len=3800):
    """Pecah pesan panjang"""
    return [text[i:i+max_len] for i in range(0, len(text), max_len)]

# ╔══════════════════════════════════════════════════════════╗
# ║              AI CORE (Felicia Brain)                     ║
# ╚══════════════════════════════════════════════════════════╝

def felicia_think(user_id, message, system_extra="", temperature=0.7):
    """Core AI Felicia dengan memory"""
    
    if user_id not in user_memory:
        user_memory[user_id] = []
    
    user_memory[user_id].append({"role": "user", "content": message})
    
    if len(user_memory[user_id]) > 25:
        user_memory[user_id] = user_memory[user_id][-25:]
    
    messages = [{"role": "system", "content": FELICIA_PROMPT + system_extra}] + user_memory[user_id]
    
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=temperature,
            max_tokens=4000,
            top_p=0.95
        )
        reply = resp.choices[0].message.content
        user_memory[user_id].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"❌ Error: {str(e)[:200]}"

def clean_code(response):
    """Bersihin kode dari markdown"""
    c = re.sub(r'```\w*\n?', '', response).strip()
    c = re.sub(r'```$', '', c).strip()
    return c

# ╔══════════════════════════════════════════════════════════╗
# ║              BOT HANDLERS                                ║
# ╚══════════════════════════════════════════════════════════╝

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu Utama Felicia AI V3 — BEAUTIFUL UI"""
    user = update.effective_user
    user_id = user.id
    name = user.first_name or "Kawan"
    
    # Reset state
    user_state[user_id] = {
        "state": "idle",
        "files": [],
        "complaints": [],
        "features": [],
        "refs": [],
        "lang": "python"
    }
    
    # Beautiful UI
    text = f"""
╔═══════════════════════════════╗
║   ✨ *FELICIA AI V{VERSION}* ✨    ║
║   © Felicia Coding Assistant ║
╚═══════════════════════════════╝

👋 *Halo, {name}!*

Aku Felicia, AI asisten koding tercanggih! 🚀
Siap bantu kamu dalam segala hal tentang koding.

╭─────────────────────────────╮
│  🔥 *FITUR SUPER LENGKAP*  │
╰─────────────────────────────╯

📖 *Baca File*
  └ Analisis isi + statistik lengkap

🔧 *Perbaiki Kode*
  └ Deteksi error → Fix otomatis

📝 *Buat Kode Baru*
  └ Dari deskripsi jadi kode

➕ *Tambah Fitur*
  └ Tambah tanpa rusak yang lama

🔄 *Rombak Kode*
  └ Refactor / rewrite / convert

🔍 *Analisis Kode*
  └ Cari bug, warning, saran

🌐 *Cari Referensi*
  └ Dokumentasi & contoh kode

💬 *Diskusi Koding*
  └ Ngobrol santai + auto-learn

╭─────────────────────────────╮
│  📊 *STATUS*                │
╰─────────────────────────────╯

🟢 AI Model: Groq Llama 3 70B
💾 Memory: Aktif (25 pesan)
📦 Output: ZIP untuk multi-file
🏷️ Watermark: ©Felicia

━━━━━━━━━━━━━━━━━━━━━━━━━━━

👇 *Pilih menu di bawah atau kirim file langsung!*
"""
    
    keyboard = [
        [InlineKeyboardButton("📖 Baca File", callback_data="mode_read"),
         InlineKeyboardButton("🔧 Perbaiki", callback_data="mode_fix")],
        [InlineKeyboardButton("📝 Buat Baru", callback_data="mode_create"),
         InlineKeyboardButton("➕ Tambah Fitur", callback_data="mode_add")],
        [InlineKeyboardButton("🔄 Rombak Kode", callback_data="mode_refactor"),
         InlineKeyboardButton("🔍 Analisis", callback_data="mode_analyze")],
        [InlineKeyboardButton("🌐 Cari Referensi", callback_data="mode_search"),
         InlineKeyboardButton("💬 Diskusi AI", callback_data="mode_chat")],
        [InlineKeyboardButton("ℹ️ Bantuan Lengkap", callback_data="help")],
    ]
    
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle tombol menu"""
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    
    modes = {
        "mode_read": ("📖 MODE BACA FILE", "📤 Kirim file untuk dibaca.\n\n✅ Format didukung:\n" + ", ".join(SUPPORTED_READ), "waiting_read"),
        "mode_fix": ("🔧 MODE PERBAIKI", "📤 Kirim file kode.\n📝 Jelaskan error/keluhan.\n\nAku akan tanya dulu, lalu perbaiki otomatis!", "waiting_file_fix"),
        "mode_create": ("📝 MODE BUAT BARU", "💡 Jelaskan kode yang ingin dibuat.\n\nContoh:\n• 'Bot Telegram anti-spam'\n• 'Website portfolio keren'\n• 'REST API dengan Flask'\n\nAku akan rekomendasikan bahasa terbaik!", "waiting_description"),
        "mode_add": ("➕ MODE TAMBAH FITUR", "📤 Kirim file kode.\n📝 Jelaskan fitur baru.\n\nAku akan tanya referensi jika diperlukan.", "waiting_file_feature"),
        "mode_refactor": ("🔄 MODE ROMBAK", "📤 Kirim file kode.\n📝 Jelaskan hasil yang diinginkan.\n\nBisa:\n• Refactor (struktur lebih baik)\n• Rewrite (tulis ulang)\n• Convert (ubah bahasa)", "waiting_refactor"),
        "mode_analyze": ("🔍 MODE ANALISIS", "📤 Kirim file kode untuk dianalisis.\n\nAku akan cari:\n🔴 Error\n🟡 Warning\n🟢 Saran\n✅ Best Practice", "waiting_file_analyze"),
        "mode_search": ("🌐 MODE CARI REFERENSI", "📝 Ketik yang ingin dicari.\n\nContoh:\n• 'Cara deploy Flask ke Railway'\n• 'Best practice React hooks'\n• 'Tutorial MongoDB aggregation'", "waiting_search"),
        "mode_chat": ("💬 MODE DISKUSI AI", "🗣️ Ngobrol bebas! Tanya apa aja tentang koding.\n\nAku punya memory & belajar dari percakapan kita.\n\nKetik 'keluar' untuk berhenti.", "waiting_chat"),
    }
    
    if q.data in modes:
        title, desc, state = modes[q.data]
        user_state[uid] = {"state": state, "files": [], "complaints": [], "features": [], "refs": [], "lang": "python"}
        
        keyboard = [[InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="back_menu")]]
        
        await q.edit_message_text(
            f"*{title}*\n\n{desc}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    elif q.data == "back_menu":
        await start(update, context)
    
    elif q.data == "help":
        help_text = """
╔═══════════════════════════════╗
║   📖 *BANTUAN LENGKAP*      ║
╚═══════════════════════════════╝

*1️⃣ BACA FILE*
Kirim file → Lihat isi + statistik

*2️⃣ PERBAIKI KODE*
Kirim file → Ceritakan error → Aku perbaiki

*3️⃣ BUAT KODE BARU*
Jelaskan ide → Aku rekomendasikan bahasa → Aku buatkan kode

*4️⃣ TAMBAH FITUR*
Kirim file → Jelaskan fitur → Aku tambahkan

*5️⃣ ROMBAK KODE*
Kirim file → Jelaskan hasil → Aku rombak total

*6️⃣ ANALISIS KODE*
Kirim file → Aku cari error & saran

*7️⃣ CARI REFERENSI*
Ketik topik → Aku carikan

*8️⃣ DISKUSI AI*
Ngobrol bebas! Aku belajar dari kamu.

╭─────────────────────────────╮
│  🏷️ *WATERMARK*             │
╰─────────────────────────────╯
Setiap file output akan ada
tanda ©Felicia di bagian bawah.

╭─────────────────────────────╮
│  📦 *MULTI-FILE*            │
╰─────────────────────────────╯
Jika lebih dari 1 file,
dikirim dalam format ZIP.

━━━━━━━━━━━━━━━━━━━━━━━━━━━
© Felicia AI V3.0
"""
        keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="back_menu")]]
        await q.edit_message_text(help_text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler file"""
    uid = update.effective_user.id
    doc = update.message.document
    fname = doc.file_name
    ext = Path(fname).suffix.lower()
    
    state = user_state.get(uid, {}).get("state", "idle")
    
    if state == "idle":
        # Auto-detect
        if ext in SUPPORTED_READ:
            state = "waiting_read"
        elif ext in SUPPORTED_FIX:
            state = "waiting_file_fix"
        else:
            await update.message.reply_text(
                f"⚠️ Format *{ext}* belum didukung.\n\n"
                "Coba format: .py, .js, .html, .css, .json, .txt, dll.",
                parse_mode="Markdown"
            )
            return
    
    # Loading animasi
    load = await update.message.reply_text("📥 *Menerima file...*", parse_mode="Markdown")
    await asyncio.sleep(0.5)
    await load.edit_text("🔍 *Menganalisis file...*")
    
    # Download
    fobj = await context.bot.get_file(doc.file_id)
    content = (await fobj.download_as_bytearray()).decode('utf-8', errors='ignore')
    
    info = get_file_info(fname, content)
    
    # Simpan ke state
    user_state[uid]["files"] = [{"name": fname, "content": content}]
    user_state[uid]["lang"] = info['lang_code']
    
    await load.edit_text(
        f"✅ *File Diterima!*\n\n"
        f"{info['emoji']} *{info['name']}*\n"
        f"🔤 Bahasa: {info['language']}\n"
        f"📊 {info['lines']} baris | {info['words']} kata\n"
        f"💾 {info['size_kb']} KB\n\n"
        f"{'📖 Mode: Baca File' if state == 'waiting_read' else '📝 Sekarang jelaskan keluhan / fitur / instruksi:'}",
        parse_mode="Markdown"
    )
    
    # Kalo mode baca, langsung tampilkan
    if state == "waiting_read":
        await asyncio.sleep(0.5)
        await show_file_content(update, uid, fname, content, info)

async def show_file_content(update, uid, fname, content, info):
    """Tampilkan isi file"""
    # Info lengkap
    info_text = (
        f"📖 *ISI FILE*\n\n"
        f"{info['emoji']} `{fname}`\n"
        f"🔤 {info['language']} | 📊 {info['lines']} baris\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
    )
    
    # Kalo pendek, kirim langsung
    if info['chars'] <= 3500:
        await update.message.reply_text(
            info_text + f"```{info['lang_code']}\n{content}\n```",
            parse_mode="Markdown"
        )
    else:
        # Info dulu
        await update.message.reply_text(info_text, parse_mode="Markdown")
        
        # Kirim per bagian
        parts = split_long_message(content, 3500)
        total = len(parts)
        
        for i, part in enumerate(parts, 1):
            await update.message.reply_text(
                f"📄 *Bagian {i}/{total}*\n```{info['lang_code']}\n{part}\n```",
                parse_mode="Markdown"
            )
            if i < total:
                await asyncio.sleep(0.3)
    
    # Tombol aksi
    if info['ext'] in SUPPORTED_FIX:
        kb = [[
            InlineKeyboardButton("🔍 Analisis", callback_data="act_analyze"),
            InlineKeyboardButton("🔧 Perbaiki", callback_data="act_fix"),
            InlineKeyboardButton("🔄 Rombak", callback_data="act_refactor")
        ], [InlineKeyboardButton("🔙 Menu", callback_data="back_menu")]]
        
        await update.message.reply_text(
            "⚡ *Aksi Cepat:*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(kb)
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler pesan teks"""
    uid = update.effective_user.id
    txt = update.message.text
    state = user_state.get(uid, {}).get("state", "idle")
    
    # MODE DISKUSI AI
    if state == "waiting_chat":
        if txt.lower() == "keluar":
            user_state[uid]["state"] = "idle"
            await update.message.reply_text("👋 Kembali ke menu! /start", parse_mode="Markdown")
            return
        
        load = await update.message.reply_text("💬 *Berpikir...*", parse_mode="Markdown")
        reply = felicia_think(uid, txt)
        await load.edit_text(reply, parse_mode="Markdown")
        return
    
    # MODE CARI REFERENSI
    if state == "waiting_search":
        load = await update.message.reply_text("🌐 *Mencari referensi...*", parse_mode="Markdown")
        reply = felicia_think(uid, f"Cari informasi tentang: {txt}\n\nBerikan penjelasan, contoh kode, best practice, dan referensi.")
        await load.edit_text(reply, parse_mode="Markdown")
        user_state[uid]["state"] = "idle"
        return
    
    # MODE BUAT KODE BARU
    if state == "waiting_description":
        load = await update.message.reply_text("🤔 *Menganalisis permintaan...*", parse_mode="Markdown")
        
        # Rekomendasi bahasa
        lang_rec = felicia_think(uid, f"Rekomendasikan 1 bahasa pemrograman terbaik untuk: {txt}\nJawab 1 kata saja.", temperature=0.3)
        rec_lang = re.sub(r'[^a-zA-Z]', '', lang_rec).lower() or "python"
        
        await load.edit_text(f"⚡ *Membuat kode {rec_lang.upper()}...*\n\nMohon tunggu sebentar ✨", parse_mode="Markdown")
        
        code = felicia_think(uid, f"""Buat kode {rec_lang.upper()} lengkap untuk:
{txt}

Syarat:
- Kode lengkap siap pakai
- Best practice
- Komentar penjelasan
- Error handling
- Tambahkan watermark ©Felicia""", temperature=0.4)
        
        code = clean_code(code)
        code = add_watermark(code, rec_lang)
        
        ext = {"python":"py","javascript":"js","typescript":"ts","html":"html","css":"css",
               "php":"php","java":"java","cpp":"cpp","go":"go","rust":"rs","bash":"sh"}.get(rec_lang, "txt")
        
        fname = f"felicia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
        
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(code)
        
        await load.delete()
        
        wi
