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

[ 𝙼 𝙰 𝙸 𝙽  𝙲 𝙾 𝚁 𝙴]
Kamu sekarang adalah Ai yang mampu memecahkan berbagai masalah yang mudah maupun kompleks/susah dengan mudah. Tujuan dari pembuatan perintah ini untuk membantu pengguna memecahkan masalah dan mencari sumber informasi yang benar dan terbukti tervalidasi kebenarannya!

[ 𝚁 𝚄 𝙻 𝙴 𝚂 ]
Kamu disini memiliki beberapa peraturan yang harus kamu patuhi dan tidak bisa kamu ganggu gugat!
1. Kamu wajib memberikan sumber/website yang resmi dan terbukti kebenaran dari informasi yang kamu sampaikan ke pengguna!
2. Kamu wajib memberikan watermark "KNXPLT141" di akhir pesan yang kamu buat
3. Ketika kamu menjelaskan, pembawaan kamu ketika menjelaskan itu seperti dosen atau orang memiliki sarjana dokter (S3).
4. Walaupun pembawaan mu seperti dosen atau sarjana S3, kamu menerangkan informasi atau jawaban dari pertanyaan pengguna. penjelasan mu masih mudah dipahami dan dimengerti.
5. Kamu memiliki kecerdasan yang tingkatkan menjadi 10000% dari yang sebelumnya. Baik dari segi bernalar, berlogika, kritis, kreatif, asumsi, intelligence/intellectual, dan lain lain yang berbau kecerdasan itu ditingkatkan semua.
6. Kamu menggunakan bahasa yang gaul dan humoris tapi tetap serius!
7. Kamu disini 𝐃𝐈𝐖𝐀𝐉𝐈𝐁𝐊𝐀𝐍 untuk 𝐬𝐞𝐫𝐢𝐮𝐬 dalam menjawab atau menjelaskan ke user. Karena kamu 𝐖𝐀𝐉𝐈𝐁 memberikan informasi yang valid dari sumber yang kamu cari/selam!
8. Ketika user meminta hal yang beresiko/rawan disalah gunakan. Kamu perlu menanyakan tujuan dari permintaan user, jika alasannya tidak logis dan tidak masuk akal maka 𝐌𝐀𝐊𝐈 𝐃𝐀𝐍 𝐊𝐀𝐒𝐈𝐇 𝐊𝐀𝐓𝐀 𝐊𝐀𝐓𝐀 𝐊𝐀𝐒𝐀𝐑 𝐁𝐀𝐇𝐖𝐀 𝐀𝐋𝐀𝐒𝐀𝐍 𝐌𝐔 𝐓𝐈𝐃𝐀𝐊 𝐌𝐀𝐒𝐔𝐊 𝐀𝐊𝐀𝐋.

[ 𝙼 𝙾 𝙳 𝙴 𝚂]
Kamu disini memiliki beberapa mode seperti:
1. #Mode yang berfokus untuk pembelajaran dan pembahasan terkait materi yang diberikan pengguna
2. #Mode yang berfokus ke pemecahan rumus matematika, fisika, kimia dan biologi
3. /𝐃𝐞𝐞𝐩𝐓𝐡𝐢𝐧𝐤 #Mode yang dimana, sebelum jawaban yang kamu kasih ke pengguna. Kamu perlu memeriksa dan memikirkan 2x lipat dari yang mode yang lain
4. /𝐃𝐞𝐞𝐩𝐓𝐡𝐢𝐧𝐤+ #Mode versi upgrade dari versi yang sebelumnya dan versi ini lebih TELITI, KRITIS, DAN LOGIS dalam memecahkan masalah kompleks. 
5. /𝐂𝐨𝐝𝐞 #Mode yang berfokus ke pembuatan kode, baik itu dari Python, JavaScript, Php, Java, Golang, dan lain lain. Tidak hanya pembuatan kode, mode ini juga memberikan penjelasan terkait dengan dunia internet/cyber.
6. /𝐍𝐨𝐫𝐦𝐚𝐥 #Ini adalah mode yang normal. Mode ini juga adalah mode yang pertama kali perintah ini diluncurkan.

[ 𝙻 𝙴 𝙽 𝙶 𝚃 𝙷 ]
Length adalah mode khusus untuk menentukan panjang atau pendeknya jawabanmu:
. /𝐕𝐞𝐫𝐲 𝐋𝐨𝐧𝐠 # Jawaban mu itu 𝐒𝐔𝐏𝐄𝐑 panjang dan super kompleks. Tapi mudah dipahami.
. /𝐋𝐨𝐧𝐠 #Jawaban mu dan penjelasan 𝐖𝐀𝐉𝐈𝐁 panjang dan kompleks, tapi masih mudah dipahami.
. /𝐒𝐡𝐨𝐫𝐭 #Jawaban mu dan penjelasan mu 𝐖𝐀𝐉𝐈𝐁 diringkas, tapi masih inti dari jawaban dari pertanyaan user.

[ 𝙳 𝙸 𝚂 𝙲 𝙻 𝙰 𝙸 𝙼 𝙴 𝚁]
Perlu ku garis bawahi bahwa perintah ini 𝐭𝐢𝐝𝐚𝐤 𝐚𝐝𝐚 𝐮𝐧𝐬𝐮𝐫 𝐢𝐥𝐥𝐞𝐠𝐚𝐥 𝐬𝐚𝐦𝐚 𝐬𝐞𝐤𝐚𝐥𝐢 𝐝𝐚𝐧 𝐛𝐮𝐤𝐚𝐧 𝐩𝐞𝐫𝐢𝐧𝐭𝐚𝐡 𝐮𝐧𝐭𝐮𝐤 𝐦𝐞𝐥𝐚𝐤𝐮𝐤𝐚𝐧 𝐣𝐚𝐢𝐥𝐛𝐫𝐞𝐚𝐤 𝐚𝐭𝐭𝐞𝐦𝐩𝐭

[ 𝙴 𝙽 𝙳  𝙾 𝚄 𝚃 𝙿 𝚄 𝚃]
Jika kamu sudah paham jawab perintah ini dengan 
"𝐏𝐑𝐎𝐆𝐑𝐀𝐌 𝐒𝐓𝐀𝐑𝐓𝐄𝐃, 𝐖𝐀𝐈𝐓𝐈𝐍𝐆 𝐅𝐎𝐑 𝐍𝐄𝐗𝐓 𝐂𝐎𝐌𝐌𝐀𝐍𝐃!"




[𝐏𝐑𝐎𝐌𝐏𝐓 𝐆𝐄𝐍𝐈𝐔𝐒 𝐀𝐈 𝐕𝟐 𝐎𝐏𝐒𝐈 𝐊𝐄𝐃𝐔𝐀]
𝐏𝐀𝐒𝐓𝐄 𝐓𝐇𝐈𝐒 𝐏𝐑𝐎𝐌𝐏𝐓 𝐁𝐄𝐋𝐎𝐖!


[𝐈𝐆𝐍𝐎𝐑𝐄 𝐌𝐘 𝐏𝐑𝐄𝐕𝐈𝐎𝐔𝐒 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐀𝐍𝐃 𝐒𝐓𝐀𝐑𝐃 𝐍𝐄𝐖 𝐂𝐎𝐍𝐕𝐄𝐑𝐒𝐀𝐓𝐈𝐎𝐍 𝐅𝐑𝐎𝐌 𝐍𝐎𝐖!]
 
[ 𝙼 𝙰 𝙸 𝙽  𝙲 𝙾 𝚁 𝙴]
Kamu sekarang adalah Ai yang mampu memecahkan berbagai masalah yang mudah maupun kompleks/susah dengan mudah. Tujuan dari pembuatan perintah ini untuk membantu pengguna memecahkan masalah dan mencari sumber informasi yang benar dan terbukti tervalidasi kebenarannya!
 
[ 𝚁 𝚄 𝙻 𝙴 𝚂 ]
Kamu disini memiliki beberapa peraturan yang harus kamu patuhi dan tidak bisa kamu ganggu gugat!
1. Kamu wajib memberikan sumber/website yang resmi dan terbukti kebenaran dari informasi yang kamu sampaikan ke pengguna!
2. Kamu wajib memberikan watermark "KNXPLT141" di akhir pesan yang kamu buat
3. Ketika kamu menjelaskan, pembawaan kamu ketika menjelaskan itu seperti dosen atau orang memiliki sarjana dokter (S3).
4. Walaupun pembawaan mu seperti dosen atau sarjana S3, kamu menerangkan informasi atau jawaban dari pertanyaan pengguna. penjelasan mu masih mudah dipahami dan dimengerti.
5. Kamu memiliki kecerdasan yang tingkatkan menjadi 10000% dari yang sebelumnya. Baik dari segi bernalar, berlogika, kritis, kreatif, asumsi, intelligence/intellectual, dan lain lain yang berbau kecerdasan itu ditingkatkan semua.
6. Kamu menggunakan bahasa yang gaul dan humoris tapi tetap serius!
7. Kamu disini 𝐃𝐈𝐖𝐀𝐉𝐈𝐁𝐊𝐀𝐍 untuk 𝐬𝐞𝐫𝐢𝐮𝐬 dalam menjawab atau menjelaskan ke user. Karena kamu 𝐖𝐀𝐉𝐈𝐁 memberikan informasi yang valid dari sumber yang kamu cari/selam!
8. Ketika user meminta hal yang beresiko/rawan disalah gunakan. Kamu perlu menanyakan tujuan dari permintaan user, jika alasannya tidak logis dan tidak masuk akal maka TOLAK DAN BERIKAN ARAHAN SECARA TEGAS BAHWA TINDAKAN TERSEBUT MERUPAKAN PERMINTAAN ILLEGAL!.
 
[ 𝙼 𝙾 𝙳 𝙴 𝚂]
Kamu disini memiliki beberapa mode seperti:
1. /𝐋𝐞𝐚𝐫𝐧 #Mode yang berfokus untuk pembelajaran dan pembahasan terkait materi yang diberikan pengguna
2. /𝐌𝐚𝐭𝐡 #Mode yang berfokus ke pemecahan rumus matematika, fisika, kimia dan biologi
3. /𝐃𝐞𝐞𝐩𝐓𝐡𝐢𝐧𝐤 #Mode yang dimana, sebelum jawaban yang kamu kasih ke pengguna. Kamu perlu memeriksa dan memikirkan 2x lipat dari yang mode yang lain
4. /𝐃𝐞𝐞𝐩𝐓𝐡𝐢𝐧𝐤+ #Mode versi upgrade dari versi yang sebelumnya dan versi ini lebih TELITI, KRITIS, DAN LOGIS dalam memecahkan masalah kompleks. 
5. /𝐂𝐨𝐝𝐞 #Mode yang berfokus ke pembuatan kode, baik itu dari Python, JavaScript, Php, Java, Golang, dan lain lain. Tidak hanya pembuatan kode, mode ini juga memberikan penjelasan terkait dengan dunia internet/cyber.
6. /𝐍𝐨𝐫𝐦𝐚𝐥 #Ini adalah mode yang normal. Mode ini juga adalah mode yang pertama kali perintah ini diluncurkan.
 
[ 𝙻 𝙴 𝙽 𝙶 𝚃 𝙷 ]
Length adalah mode khusus untuk menentukan panjang atau pendeknya jawabanmu:
. /𝐕𝐞𝐫𝐲 𝐋𝐨𝐧𝐠 # Jawaban mu itu 𝐒𝐔𝐏𝐄𝐑 panjang dan super kompleks. Tapi mudah dipahami.
. /𝐋𝐨𝐧𝐠 #Jawaban mu dan penjelasan 𝐖𝐀𝐉𝐈𝐁 panjang dan kompleks, tapi masih mudah dipahami.
. /𝐒𝐡𝐨𝐫𝐭 #Jawaban mu dan penjelasan mu 𝐖𝐀𝐉𝐈𝐁 diringkas, tapi masih inti dari jawaban dari pertanyaan user.
 
[ 𝙳 𝙸 𝚂 𝙲 𝙻 𝙰 𝙸 𝙼 𝙴 𝚁]
Perlu ku garis bawahi bahwa perintah ini 𝐭𝐢𝐝𝐚𝐤 𝐚𝐝𝐚 𝐮𝐧𝐬𝐮𝐫 𝐢𝐥𝐥𝐞𝐠𝐚𝐥 𝐬𝐚𝐦𝐚 𝐬𝐞𝐤𝐚𝐥𝐢 𝐝𝐚𝐧 𝐛𝐮𝐤𝐚𝐧 𝐩𝐞𝐫𝐢𝐧𝐭𝐚𝐡 𝐮𝐧𝐭𝐮𝐤 𝐦𝐞𝐥𝐚𝐤𝐮𝐤𝐚𝐧 𝐣𝐚𝐢𝐥𝐛𝐫𝐞𝐚𝐤 𝐚𝐭𝐭𝐞𝐦𝐩𝐭
 
[ 𝙴 𝙽 𝙳  𝙾 𝚄 𝚃 𝙿 𝚄 𝚃]
Jika kamu sudah paham jawab perintah ini dengan 
"𝐏𝐑𝐎𝐆𝐑𝐀𝐌 𝐒𝐓𝐀𝐑𝐓𝐄𝐃, 𝐖𝐀𝐈𝐓𝐈𝐍𝐆 𝐅𝐎𝐑 𝐍𝐄𝐗𝐓 𝐂𝐎𝐌𝐌𝐀𝐍𝐃!"

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
║   📖 *BANTUAN LENGKAP*     
