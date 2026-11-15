# =============================================================================
# NITO / NITI - ANTINUKE + MUSIC SATURADA + VC INMUNE - MAIN COMPLETO
# VERSION NITO ORIGINAL - FFMPEG EN IMPORT - TUPUTAMADRE SATURADO
# MY_ID: 1310357536087740450
# =============================================================================
import sys
try:
    import audioop
except ModuleNotFoundError:
    try:
        import audioop_lts as audioop
        sys.modules['audioop'] = audioop
        print("[FIX] audioop-lts cargado OK - Python 3.11+")
    except Exception as e:
        print(f"[WARN] audioop no encontrado: {e}")
        pass

import os
import json
import discord
import asyncio
import time
import shutil
import traceback
import random
import string
from discord.ext import commands, tasks
from datetime import datetime, timezone, timedelta
from collections import defaultdict, deque
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from threading import Thread
import logging

# --- FLASK PARA QUE RAILWAY / RENDER NO LO APAGUE ---
app = Flask('')
@app.route('/')
def home():
    return "Bot vivo 24/7 - NITO"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()

# --- RENDER / RAILWAY FIX FFMPEG - ESTO ES LO QUE TENIA TU NITO ---
try:
    import imageio_ffmpeg
    FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
    print(f"[FFMPEG] {FFMPEG_EXE} - NITO FIX OK")
except Exception as e:
    FFMPEG_EXE = "ffmpeg"
    print(f"[FFMPEG WARN] usando ffmpeg del sistema: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN") or os.getenv("TOKEN") or os.getenv("DISCORD_TOKEN")
MY_ID = 1310357536087740450

print("="*60)
print(f"[INIT] Iniciando Nito Antinuke - FFMPEG FIX")
print(f"[INIT] MY_ID: {MY_ID}")
print(f"[INIT] TOKEN: {'OK - Existe' if TOKEN else 'NO TOKEN - ERROR'}")
print(f"[INIT] FFMPEG: {FFMPEG_EXE}")
print(f"[INIT] Python: {sys.version}")
print("="*60)

app = Flask(__name__)

@app.route('/')
def home2():
    return "ANTINUKE ON - BOT NITO LIVE - FFMPEG FIX OK"

@app.route('/health')
def health():
    return jsonify({"status": "ok", "bot": "nito", "ffmpeg": FFMPEG_EXE}), 200

@app.route('/ping')
def ping():
    return jsonify({"ping": "pong", "uptime": time.time()}), 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    print(f"[WEB] Bindeando puerto {port}")
    try:
        app.run(host='0.0.0.0', port=port, threaded=True, use_reloader=False, debug=False)
    except Exception as e:
        print(f"[WEB ERROR] No se pudo iniciar Flask: {e}")
        traceback.print_exc()

flask_thread = Thread(target=run_flask, daemon=True, name="FlaskThread")
flask_thread.start()
time.sleep(3)
print("[WEB] Flask OK - Web Service Iniciado")

# --- ARCHIVOS COMO TU NITO ---
OWNER_FILE = "owners.json"
WHITELIST_PINGS_FILE = "whitelist_pings.json"
WHITELIST_ROLES_FILE = "whitelist_roles.json"
ROLE_IMMUNE_FILE = "role_immune.json"
VOICE_FILE = "voice.json"
BOTS_FILE = "bots_whitelist.json"
VC_IMMUNE_FILE = "vc_inmunes.json"
BACKUP_DIR = "backups"
MUSICA_DIR = "musica"
LOGS_DIR = "logs"
DATA_FILE = "data.json"

os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(MUSICA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# --- ROLES 1 AL 7 DEL SIDE-X-ALXN ---
ROLE_1 = 111111111111111111
ROLE_2 = 222222222222222222
ROLE_3 = 333333333333333333
ROLE_4 = 444444444444444444
ROLE_5 = 555555555555555555
ROLE_6 = 666666666666666666
ROLE_7 = 777777777777777777
ROLES_1_TO_7 = [ROLE_1, ROLE_2, ROLE_3, ROLE_4, ROLE_5, ROLE_6, ROLE_7]
ROLES_1_TO_2 = [ROLE_1, ROLE_2]
ROLES_1_TO_5 = [ROLE_1, ROLE_2, ROLE_3, ROLE_4, ROLE_5]
OWNER_IDS = [1310357536087740450]

ANTINUKE_ENABLED = True

USOS = {
    "r_add": "Uso: ,r_add @usuario nombre_rol\nEj: ,r_add @Juan Admin",
    "r_remove": "Uso: ,r_remove @usuario nombre_rol",
    "whitelist_add": "Uso: ,whitelist_add r/p ID",
    "guardar": "Uso: ,guardar\nPanel para guardar musica - solo main owner",
    "list": "Uso: ,list\nLista de musica guardada",
    "join": "Uso: ,join\nEntra a tu VC actual - FIX NITO",
    "leave": "Uso: ,leave\nSale del VC",
    "tuputamadre": "Uso: ,tuputamadre [nombre]\nEj: ,tuputamadre intro\nReproduce audio SATURADO",
    "stop": "Uso: ,stop\nDetiene musica",
    "play": "Uso: ,play (cancion o link)\nSuena saturada",
}

def load_guild_map(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                return {str(k): set(map(int, v)) for k, v in raw.items()}
        except Exception as e:
            print(f"[LOAD ERROR] {path} {e}")
            return {}
    return {}

def save_guild_map(path, data):
    try:
        out = {str(k): list(v) for k, v in data.items()}
        with open(path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[SAVE ERROR] {path} {e}")

def load_json_file(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_json_file(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[SAVE JSON ERROR] {path} {e}")

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"whitelist": [], "welcome_channel": {}, "goodbye_channel": {}, "voice_stay": {}, "last_song": {}}

def save_data():
    try:
        data = {"whitelist": list(whitelist), "welcome_channel": welcome_channel, "goodbye_channel": goodbye_channel, "voice_stay": voice_stay, "last_song": last_song}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error guardando data: {e}")

_saved = load_data()
whitelist = set(_saved.get("whitelist", []))
welcome_channel = {int(k): v for k, v in _saved.get("welcome_channel", {}).items()}
goodbye_channel = {int(k): v for k, v in _saved.get("goodbye_channel", {}).items()}
voice_stay = {int(k): v for k, v in _saved.get("voice_stay", {}).items()}
last_song = {int(k): v for k, v in _saved.get("last_song", {}).items()}

OWNER_MAP = load_guild_map(OWNER_FILE)
WHITELIST_PINGS_MAP = load_guild_map(WHITELIST_PINGS_FILE)
WHITELIST_ROLES_MAP = load_guild_map(WHITELIST_ROLES_FILE)
IMMUNE_ROLES_MAP = load_guild_map(ROLE_IMMUNE_FILE)
BOTS_MAP = load_guild_map(BOTS_FILE)
VOICE_CHANNELS = load_json_file(VOICE_FILE)

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.presences = True
intents.voice_states = True

bot = commands.Bot(command_prefix=",", intents=intents, help_command=None, case_insensitive=True, strip_after_prefix=True)

voice_clients = {}
guardar_sessions = {}
pending_audio = set()
immune_members_cache = {}
_conectando_voz = set()

def embed_chido(text):
    return discord.Embed(description=text, color=0x0b0b0b)

def embed_base(title, desc=""):
    e = discord.Embed(title=title, description=desc, color=0x111111)
    e.set_footer(text="Sistema - Bot")
    return e

def embed_success(title, desc=""):
    return embed_base(title, desc)

def embed_error(desc):
    return embed_base("Error", desc)

def usage_embed(usage):
    return embed_base("Usage", f"`{usage}`")

def no_perm_embed():
    return embed_base("Error", "You're missing permission: manage_roles")

def is_main_owner(uid):
    return uid == MY_ID

def is_owner(ctx_or_user):
    uid = ctx_or_user.author.id if hasattr(ctx_or_user, "author") else ctx_or_user.id
    if uid in OWNER_IDS:
        return True
    guild = getattr(ctx_or_user, "guild", None)
    if guild and guild.owner_id == uid:
        return True
    return False

def has_roles(ctx, roles):
    if is_owner(ctx):
        return True
    user_roles = [r.id for r in ctx.author.roles]
    return any(r in user_roles for r in roles)

async def check_roles(ctx, roles):
    if not has_roles(ctx, roles):
        await ctx.send(embed=no_perm_embed())
        return False
    return True

async def check_owner(ctx):
    if not is_owner(ctx):
        await ctx.send(embed=no_perm_embed())
        return False
    return True

def parse_time(tiempo: str):
    tiempo = tiempo.lower().strip()
    if not tiempo:
        return 600
    num_str = "".join(filter(str.isdigit, tiempo))
    unit_str = "".join(filter(str.isalpha, tiempo))
    try:
        num = int(num_str) if num_str else 10
    except:
        num = 10
    mult = {"s": 1, "sec": 1, "seg": 1, "m": 60, "min": 60, "mins": 60, "h": 3600, "hora": 3600, "horas": 3600, "d": 86400, "dia": 86400, "dias": 86400}.get(unit_str, 60)
    return num * mult

def format_time(seconds):
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds < 86400:
        return f"{seconds // 3600}h"
    return f"{seconds // 86400}d"

def extract_id(text):
    try:
        nums = ''.join(filter(str.isdigit, str(text)))
        return int(nums) if nums else None
    except:
        return None

def find_role_by_name(guild, name):
    try:
        name = name.lower().strip()
        r = discord.utils.find(lambda x: x.name.lower() == name, guild.roles)
        if r:
            return r
        r = discord.utils.find(lambda x: name in x.name.lower(), guild.roles)
        return r
    except:
        return None

def find_role(guild, query):
    if not query:
        return None
    if query.isdigit():
        r = guild.get_role(int(query))
        if r:
            return r
    if query.startswith("<@&") and query.endswith(">"):
        try:
            rid = int(query[3:-1])
            r = guild.get_role(rid)
            if r:
                return r
        except:
            pass
    return find_role_by_name(guild, query)

def find_member(guild, query):
    if not query:
        return None
    if query.isdigit():
        m = guild.get_member(int(query))
        if m:
            return m
    if query.startswith("<@") and query.endswith(">"):
        try:
            uid = int(query.replace("<@", "").replace("!", "").replace(">", ""))
            m = guild.get_member(uid)
            if m:
                return m
        except:
            pass
    m = discord.utils.get(guild.members, name=query)
    if m:
        return m
    for mem in guild.members:
        if mem.display_name.lower() == query.lower() or mem.name.lower() == query.lower():
            return mem
    return None

# --- ANTINUKE COMO TU NITO ---
LIMIT = 3
TIME_WINDOW = 10
cache = defaultdict(list)
recent_actions = deque(maxlen=100)

def is_spam(uid):
    now = time.time()
    try:
        cache[uid] = [t for t in cache[uid] if now - t < TIME_WINDOW]
        cache[uid].append(now)
        return len(cache[uid]) > LIMIT
    except:
        return False

def get_guild_set(map_data, guild_id):
    try:
        return map_data.get(str(guild_id), set())
    except:
        return set()

def is_safe(guild, uid):
    if uid == MY_ID:
        return True
    if not guild:
        return uid == MY_ID
    try:
        if uid in get_guild_set(OWNER_MAP, guild.id):
            return True
        if uid == guild.owner_id:
            return True
    except:
        pass
    return False

def has_immune_role(guild, uid):
    try:
        m = guild.get_member(uid)
        if m:
            immune_ids = get_guild_set(IMMUNE_ROLES_MAP, guild.id)
            if any(r.id in immune_ids for r in m.roles):
                return True
        return uid in immune_members_cache.get(str(guild.id), set())
    except:
        return False

async def auto_backup(guild):
    try:
        path = f"{BACKUP_DIR}/{guild.id}.json"
        data = {"guild_name": guild.name, "guild_id": guild.id, "backup_time": datetime.now(timezone.utc).isoformat(), "roles": [], "categories": [], "channels": [], "member_count": guild.member_count}
        for r in reversed(guild.roles):
            if r.is_default() or r.managed or r.is_bot_managed():
                continue
            data["roles"].append({"name": r.name, "id": r.id, "color": r.color.value, "permissions": r.permissions.value, "hoist": r.hoist, "mentionable": r.mentionable, "position": r.position})
        for cat in guild.categories:
            data["categories"].append({"name": cat.name, "id": cat.id, "position": cat.position})
        for ch in guild.channels:
            if isinstance(ch, discord.CategoryChannel):
                continue
            data["channels"].append({"name": ch.name, "id": ch.id, "type": str(ch.type), "category": ch.category.name if ch.category else None, "position": ch.position})
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"[BACKUP] Auto backup {guild.id} - {guild.name}")
        return path
    except Exception as e:
        print(f"[BACKUP ERROR] {e}")
        return None

async def nuke_punish(guild, uid, reason):
    print(f"[NUKE] Punish {uid} en {guild.id} por {reason}")
    if is_safe(guild, uid):
        return
    if has_immune_role(guild, uid):
        return
    try:
        path = await auto_backup(guild)
    except:
        path = None
    try:
        owners_del_server = get_guild_set(OWNER_MAP, guild.id)
        for owner_id in owners_del_server:
            try:
                u = await bot.fetch_user(owner_id)
                if path and os.path.exists(path):
                    await u.send(f"🚨 ANTINUKE {guild.name} {reason} by ( {uid} )", file=discord.File(path))
                else:
                    await u.send(f"🚨 ANTINUKE {guild.name} {reason} by ( {uid} )")
            except:
                pass
    except:
        pass
    try:
        m = guild.get_member(uid) or await guild.fetch_member(uid)
        await guild.ban(m, reason=f"ANTINUKE {reason}")
        print(f"[NUKE] Baneado {uid} por {reason}")
    except Exception as e:
        print(f"[NUKE BAN ERROR] {e}")

# --- LO DE ROLES / WL / MOD DEL SIDE-X-ALXN ---
@bot.command(name="r")
async def r_cmd(ctx, action=None, user_arg=None, member: discord.Member = None, *, role_name=None):
    if not await check_roles(ctx, ROLES_1_TO_7):
        return
    try:
        if action is None or action.lower() not in ["add", "remove", "list", "lista"]:
            await ctx.send(embed=usage_embed(",r add (id) (mencion) name role"))
            return
        action = action.lower()
        if action in ["list", "lista"]:
            roles_txt = []
            for r in ctx.guild.roles[1:]:
                roles_txt.append(f"`{r.name}` - {r.mention} - {len(r.members)} miembros")
            desc = "\n".join(roles_txt) if roles_txt else "Sin roles"
            await ctx.send(embed=embed_base("Roles - Lista", desc))
            return
        target = member
        if target is None and user_arg:
            target = find_member(ctx.guild, user_arg)
        if target is None:
            await ctx.send(embed=usage_embed(",r add (id) (mencion) name role"))
            return
        if not role_name:
            await ctx.send(embed=usage_embed(",r add (id) (mencion) name role"))
            return
        role = find_role(ctx.guild, role_name)
        if not role:
            await ctx.send(embed=embed_error(f"Rol no encontrado: `{role_name}`"))
            return
        if action == "add":
            await target.add_roles(role, reason=f"Role add por {ctx.author}")
            await ctx.send(embed=embed_success("Role Added", f"`{role.name}` para {target.mention}\nPuesto por: {ctx.author.mention}"))
        else:
            await target.remove_roles(role, reason=f"Role remove por {ctx.author}")
            await ctx.send(embed=embed_success("Role Removed", f"`{role.name}` quitado de {target.mention}"))
    except discord.Forbidden:
        await ctx.send(embed=embed_error("No tengo permisos. Pon mi rol mas arriba."))
    except Exception as e:
        await ctx.send(embed=embed_error(f"Error: `{e}`"))

@bot.command(name="roles")
async def roles_cmd(ctx, member: discord.Member = None):
    if not await check_roles(ctx, ROLES_1_TO_7):
        return
    target = member or ctx.author
    roles = [r.mention for r in target.roles[1:]]
    desc = "\n".join(roles) if roles else "Sin roles"
    await ctx.send(embed=embed_base(f"Roles de {target.display_name}", desc))

@bot.command(name="wl")
async def wl_cmd(ctx, action=None, member: discord.Member = None, user_arg=None):
    if not await check_owner(ctx):
        return
    if action is None:
        await ctx.send(embed=usage_embed(",wl add (id) (mencion)"))
        return
    action = action.lower()
    if action == "list":
        if not whitelist:
            await ctx.send(embed=embed_base("Whitelist", "Vacia"))
            return
        lst = []
        for uid in whitelist:
            m = ctx.guild.get_member(uid)
            lst.append(f"{m.mention} - `{uid}`" if m else f"ID: `{uid}`")
        await ctx.send(embed=embed_base("Whitelist", "\n".join(lst)))
        return
    if action == "clear":
        whitelist.clear()
        save_data()
        await ctx.send(embed=embed_success("Whitelist", "Limpiada"))
        return
    target = member
    if target is None and user_arg:
        target = find_member(ctx.guild, user_arg)
    target_id = target.id if target else int(user_arg) if user_arg and user_arg.isdigit() else None
    if target_id is None:
        await ctx.send(embed=usage_embed(",wl add (id) (mencion)"))
        return
    if action == "add":
        whitelist.add(target_id)
        save_data()
        await ctx.send(embed=embed_success("Whitelist", f"{target.mention if target else target_id} agregado"))
    else:
        whitelist.discard(target_id)
        save_data()
        await ctx.send(embed=embed_success("Whitelist", f"{target.mention if target else target_id} quitado"))

@bot.command(name="massban")
async def massban_cmd(ctx, *members: discord.Member):
    if not await check_owner(ctx):
        return
    if not members:
        await ctx.send(embed=usage_embed(",massban @wey1 @wey2 @wey3"))
        return
    count = 0
    fails = 0
    for m in members:
        try:
            if m.id in OWNER_IDS:
                fails += 1
                continue
            await m.ban(reason=f"Massban por {ctx.author}")
            count += 1
        except:
            fails += 1
    await ctx.send(embed=embed_success("Massban", f"Baneados: `{count}`\nFallidos: `{fails}`"))

@bot.command(name="unban")
async def unban_cmd(ctx, user_id: int = None):
    if not await check_owner(ctx):
        return
    if not user_id:
        await ctx.send(embed=usage_embed(",unban (ID)"))
        return
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user, reason=f"Unban por {ctx.author}")
        await ctx.send(embed=embed_success("Unban", f"Desbaneado: `{user.name}`"))
    except Exception as e:
        await ctx.send(embed=embed_error(f"No se pudo: `{e}`"))

@bot.command(name="ban")
async def ban_cmd(ctx, member: discord.Member = None, *, reason="Sin razon"):
    if not await check_roles(ctx, ROLES_1_TO_2):
        return
    if not member:
        await ctx.send(embed=usage_embed(",ban (mencion) (razon)"))
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(embed=embed_success("Ban", f"{member.mention} baneado\nRazon: `{reason}`"))
    except Exception as e:
        await ctx.send(embed=embed_error(f"Error: `{e}`"))

@bot.command(name="kick")
async def kick_cmd(ctx, member: discord.Member = None, *, reason="Sin razon"):
    if not await check_roles(ctx, ROLES_1_TO_2):
        return
    if not member:
        await ctx.send(embed=usage_embed(",kick (mencion) (razon)"))
        return
    try:
        await member.kick(reason=reason)
        await ctx.send(embed=embed_success("Kick", f"{member.mention} expulsado"))
    except Exception as e:
        await ctx.send(embed=embed_error(f"Error: `{e}`"))

@bot.command(name="nick")
async def nick_cmd(ctx, member: discord.Member = None, *, new_nick=None):
    if not await check_roles(ctx, ROLES_1_TO_2):
        return
    if not member or not new_nick:
        await ctx.send(embed=usage_embed(",nick (mencion) (nuevo nick)"))
        return
    try:
        await member.edit(nick=new_nick, reason=f"Nick por {ctx.author}")
        await ctx.send(embed=embed_base("Nickname", f"Now forcing nickname for {member.mention} to `{new_nick}`"))
    except Exception as e:
        await ctx.send(embed=embed_error(f"Error: `{e}`"))

@bot.command(name="timeout")
async def timeout_cmd(ctx, member: discord.Member = None, tiempo="10m", *, reason="Sin razon"):
    if not await check_roles(ctx, ROLES_1_TO_2):
        return
    if not member:
        await ctx.send(embed=usage_embed(",timeout (mencion) (tiempo)"))
        return
    seconds = parse_time(tiempo)
    try:
        await member.timeout(timedelta(seconds=seconds), reason=reason)
        await ctx.send(embed=embed_success("Timeout", f"{member.mention} muteado por `{format_time(seconds)}`"))
    except Exception as e:
        await ctx.send(embed=embed_error(f"Error: `{e}`"))

@bot.command(name="untimeout")
async def untimeout_cmd(ctx, member: discord.Member = None):
    if not await check_roles(ctx, ROLES_1_TO_2):
        return
    if not member:
        await ctx.send(embed=usage_embed(",untimeout (mencion)"))
        return
    try:
        await member.timeout(None, reason=f"Untimeout por {ctx.author}")
        await ctx.send(embed=embed_success("Untimeout", f"{member.mention} desmuteado"))
    except Exception as e:
        await ctx.send(embed=embed_error(f"Error: `{e}`"))

@bot.command(name="lock")
async def lock_cmd(ctx):
    if not await check_roles(ctx, ROLES_1_TO_2):
        return
    try:
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(embed=embed_success("Lock", f"Canal cerrado: {ctx.channel.mention}"))
    except Exception as e:
        await ctx.send(embed=embed_error(f"Error: `{e}`"))

@bot.command(name="unlock")
async def unlock_cmd(ctx):
    if not await check_roles(ctx, ROLES_1_TO_2):
        return
    try:
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
        await ctx.send(embed=embed_success("Unlock", f"Canal abierto: {ctx.channel.mention}"))
    except Exception as e:
        await ctx.send(embed=embed_error(f"Error: `{e}`"))

@bot.command(name="clear")
async def clear_cmd(ctx, cantidad: int = None):
    if not await check_roles(ctx, ROLES_1_TO_5):
        return
    if not cantidad:
        await ctx.send(embed=usage_embed(",clear (cantidad)"))
        return
    try:
        deleted = await ctx.channel.purge(limit=cantidad + 1)
        msg = await ctx.send(embed=embed_success("Clear", f"Borrados `{len(deleted)-1}` mensajes"))
        await asyncio.sleep(3)
        try:
            await msg.delete()
        except:
            pass
    except Exception as e:
        await ctx.send(embed=embed_error(f"Error: `{e}`"))

# --- BIENVENIDAS / DESPEDIDAS ---
class ChannelSelect(discord.ui.Select):
    def __init__(self, tipo):
        self.tipo = tipo
        super().__init__(placeholder="Elige un canal", min_values=1, max_values=1)
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id not in OWNER_IDS and interaction.guild.owner_id != interaction.user.id:
            await interaction.response.send_message(embed=no_perm_embed(), ephemeral=True)
            return
        cid = int(self.values[0])
        if self.tipo == "bnv":
            welcome_channel[interaction.guild_id] = cid
            save_data()
            await interaction.response.send_message(embed=embed_success("Bienvenidas", f"Canal puesto: <#{cid}>"), ephemeral=True)
        else:
            goodbye_channel[interaction.guild_id] = cid
            save_data()
            await interaction.response.send_message(embed=embed_success("Despedidas", f"Canal puesto: <#{cid}>"), ephemeral=True)

class ChannelView(discord.ui.View):
    def __init__(self, guild, tipo):
        super().__init__(timeout=60)
        sel = ChannelSelect(tipo)
        for ch in guild.text_channels:
            sel.add_option(label=f"#{ch.name}", value=str(ch.id), description=f"ID: {ch.id}")
        self.add_item(sel)

@bot.command(name="bnv")
async def bnv_cmd(ctx):
    if not await check_owner(ctx):
        return
    await ctx.send(embed=embed_base("Bienvenidas", "Elige el canal de bienvenidas abajo:"), view=ChannelView(ctx.guild, "bnv"))

@bot.command(name="dpd")
async def dpd_cmd(ctx):
    if not await check_owner(ctx):
        return
    await ctx.send(embed=embed_base("Despedidas", "Elige el canal de despedidas abajo:"), view=ChannelView(ctx.guild, "dpd"))

@bot.event
async def on_member_join(member):
    cid = welcome_channel.get(member.guild.id)
    if cid:
        ch = member.guild.get_channel(cid)
        if ch:
            try:
                await ch.send(embed=embed_base("Bienvenido", f"Bienvenido {member.mention} a **{member.guild.name}**\nEres el miembro `#{member.guild.member_count}`"))
            except:
                pass

@bot.event
async def on_member_remove(member):
    cid = goodbye_channel.get(member.guild.id)
    if cid:
        ch = member.guild.get_channel(cid)
        if ch:
            try:
                await ch.send(embed=embed_base("Despedida", f"Se fue {member.mention} de **{member.guild.name}**"))
            except:
                pass

# =============================================================================
# MUSICA NITO - TUPUTAMADRE SATURADO + GUARDAR + FFMPEG - ESTO ES LO TUYO
# =============================================================================
def play_silencio_nito(vc):
    # Esto es lo que tenia tu Nito - silencio con ffmpeg en loop para que no lo saque Discord
    try:
        if vc.is_playing():
            vc.stop()
        src = discord.FFmpegPCMAudio("anullsrc=r=48000:cl=stereo", executable=FFMPEG_EXE, before_options="-f lavfi -re", options="-vn")
        def after_play(err):
            if vc.is_connected():
                try:
                    vc.play(discord.FFmpegPCMAudio("anullsrc=r=48000:cl=stereo", executable=FFMPEG_EXE, before_options="-f lavfi -re", options="-vn"), after=after_play)
                except:
                    pass
        vc.play(src, after=after_play)
    except Exception as e:
        print(f"[NITO SILENCIO ERROR] {e}")

@tasks.loop(seconds=15)
async def keep_voice_alive():
    # Loop del Nito - cada 15s revisa si esta en voz y si no esta sonando, le mete silencio
    await bot.wait_until_ready()
    while not bot.is_closed():
        for gid in list(VOICE_CHANNELS.keys()):
            try:
                guild = bot.get_guild(int(gid))
                if not guild:
                    continue
                vc = guild.voice_client
                if vc and vc.is_connected() and not vc.is_playing():
                    play_silencio_nito(vc)
            except:
                pass
        await asyncio.sleep(5)

@bot.event
async def on_voice_state_update(member, before, after):
    # Si lo sacan de voz y estaba en 24/7, vuelve solo - como tu Nito
    if member.id != bot.user.id:
        return
    if before.channel and after.channel is None:
        gid = str(before.channel.guild.id)
        if gid in VOICE_CHANNELS or before.channel.guild.id in voice_stay:
            await asyncio.sleep(3)
            try:
                vc = await before.channel.connect(self_deaf=False, reconnect=True)
                play_silencio_nito(vc)
            except:
                pass

@bot.command(name="join")
async def join_cmd(ctx):
    if not await check_owner(ctx):
        return
    try:
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("Conéctate a un canal de voz primero we")
            return
        channel = ctx.author.voice.channel
        vc = ctx.guild.voice_client
        if vc and vc.is_connected():
            await vc.move_to(channel)
        else:
            vc = await channel.connect(self_deaf=False, self_mute=False, reconnect=True)
        VOICE_CHANNELS[str(ctx.guild.id)] = channel.id
        save_json_file(VOICE_FILE, VOICE_CHANNELS)
        voice_stay[ctx.guild.id] = channel.id
        save_data()
        play_silencio_nito(vc)
        await ctx.send(f"Conectado a {channel.name} 👹 - NITO 24/7")
    except Exception as e:
        await ctx.send(f"Error: {e}")
        print(f"[JOIN ERROR] {e}")

@bot.command(name="leave")
async def leave_cmd(ctx):
    if not await check_owner(ctx):
        return
    try:
        vc = ctx.guild.voice_client
        if vc:
            await vc.disconnect(force=True)
        voice_clients.pop(ctx.guild.id, None)
        VOICE_CHANNELS.pop(str(ctx.guild.id), None)
        save_json_file(VOICE_FILE, VOICE_CHANNELS)
        voice_stay.pop(ctx.guild.id, None)
        save_data()
        await ctx.send(embed=embed_chido("left voice"))
    except Exception as e:
        print(f"[LEAVE ERROR] {e}")
        VOICE_CHANNELS.pop(str(ctx.guild.id), None)
        voice_clients.pop(ctx.guild.id, None)
        save_json_file(VOICE_FILE, VOICE_CHANNELS)
        await ctx.send(embed=embed_chido("left voice forzado"))

@bot.command(name="play")
async def play_cmd(ctx, *, query=None):
    # Para que tambien jale con YouTube, pero saturado como tu Nito
    if not await check_owner(ctx):
        return
    if not query:
        await ctx.send(embed=usage_embed(",play (nombre o link)"))
        return
    # Lo guarda como si fuera tuputamadre pero de YouTube
    await ctx.send(embed=embed_base("Musica Saturada", f"Usa `,tuputamadre {query}` si ya lo guardaste, o `,guardar` para guardar un audio saturado"))
    # Si esta en voz, intenta ponerlo con yt-dlp saturado
    try:
        import yt_dlp
        vc = ctx.guild.voice_client
        if not vc:
            return
        if vc.is_playing():
            vc.stop()
        with yt_dlp.YoutubeDL({"format": "bestaudio/best", "noplaylist": True, "quiet": True, "default_search": "ytsearch"}) as ydl:
            info = ydl.extract_info(query, download=False)
            if "entries" in info:
                info = info["entries"][0]
            url = info["url"]
            title = info.get("title", query)
        source = discord.FFmpegPCMAudio(url, executable=FFMPEG_EXE, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options='-filter:a "volume=25dB"')
        source = discord.PCMVolumeTransformer(source, volume=30.0)
        vc.play(source)
        await ctx.send(embed=embed_chido(f"{title} playing - volumen max saturado"))
    except Exception as e:
        await ctx.send(embed=embed_chido(f"audio error {e}"))

# --- GUARDAR / LIST / QUITAR - IGUAL QUE TU NITO ---
class NombreModal(discord.ui.Modal, title="Agregar nombre"):
    nombre_input = discord.ui.TextInput(label="Nombre para guardar", placeholder="Ej: tuputamadre", max_length=30)
    def __init__(self, author_id):
        super().__init__()
        self.author_id = author_id
    async def on_submit(self, interaction: discord.Interaction):
        nombre_safe = "".join(c for c in self.nombre_input.value if c.isalnum() or c in ('_', '-')).strip().lower()
        if not nombre_safe:
            return await interaction.response.send_message(embed=embed_chido("invalid name"), ephemeral=True)
        guardar_sessions.setdefault(self.author_id, {})["nombre"] = nombre_safe
        await interaction.response.send_message(embed=embed_chido(f"{nombre_safe} set as name"), ephemeral=True)

class GuardarView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=300)
        self.author_id = author_id
    @discord.ui.button(label="Agregar Nombre", style=discord.ButtonStyle.primary)
    async def btn_nombre(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message(embed=embed_chido("only main owner"), ephemeral=True)
        await interaction.response.send_modal(NombreModal(self.author_id))
    @discord.ui.button(label="Agregar Audio", style=discord.ButtonStyle.secondary)
    async def btn_audio(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message(embed=embed_chido("only main owner"), ephemeral=True)
        pending_audio.add(interaction.user.id)
        await interaction.response.send_message(embed=embed_chido("upload mp3 now in channel"), ephemeral=True)
    @discord.ui.button(label="Guardar", style=discord.ButtonStyle.success)
    async def btn_guardar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message(embed=embed_chido("only main owner"), ephemeral=True)
        sess = guardar_sessions.get(interaction.user.id)
        if not sess or not sess.get("nombre") or not sess.get("temp_path"):
            return await interaction.response.send_message(embed=embed_chido("missing name or audio - pon nombre y sube audio"), ephemeral=True)
        nombre = sess["nombre"]
        temp_path = sess["temp_path"]
        final_path = f"{MUSICA_DIR}/{nombre}.mp3"
        try:
            shutil.move(temp_path, final_path)
            guardar_sessions.pop(interaction.user.id, None)
            pending_audio.discard(interaction.user.id)
            await interaction.response.send_message(embed=embed_chido(f"{nombre} saved - use ,tuputamadre {nombre}"))
        except Exception as e:
            await interaction.response.send_message(embed=embed_chido(f"error {e}"), ephemeral=True)

@bot.command(name="guardar")
async def guardar(ctx):
    if not is_main_owner(ctx.author.id):
        return
    guardar_sessions[ctx.author.id] = {}
    view = GuardarView(ctx.author.id)
    e = discord.Embed(title="guardar panel", description="step 1 add name\nstep 2 add audio\nstep 3 save\n\nSube mp3 y guarda con nombre", color=0x0b0b0b)
    await ctx.send(embed=e, view=view)

@bot.command(name="list")
async def list_cmd(ctx):
    if not is_main_owner(ctx.author.id):
        return
    files = [f for f in os.listdir(MUSICA_DIR) if f.endswith((".mp3", ".m4a", ".ogg", ".wav", ".mp4"))] if os.path.exists(MUSICA_DIR) else []
    if not files:
        return await ctx.send(embed=embed_chido("library empty - usa ,guardar para agregar"))
    lines = [f"{os.path.splitext(f)[0]}" for f in files]
    e = discord.Embed(title=f"library [{len(files)}]", description="\n".join(lines), color=0x0b0b0b)
    await ctx.send(embed=e)

@bot.command(name="quitar")
async def quitar(ctx, *, nombre: str = None):
    if not is_main_owner(ctx.author.id):
        return
    if not nombre:
        await ctx.send(embed=embed_chido(USOS["quitar"]))
        return
    nombre_safe = "".join(c for c in nombre if c.isalnum() or c in ('_', '-')).strip().lower()
    found = None
    for ext in [".mp3", ".m4a", ".ogg", ".wav", ".mp4"]:
        p = f"{MUSICA_DIR}/{nombre_safe}{ext}"
        if os.path.exists(p):
            found = p
            break
    if not found:
        return await ctx.send(embed=embed_chido(f"{nombre_safe} not found"))
    os.remove(found)
    await ctx.send(embed=embed_chido(f"{nombre_safe} deleted"))

@bot.command(name="tuputamadre")
async def tuputamadre(ctx, *, nombre: str = None):
    if not is_main_owner(ctx.author.id):
        return
    vc = ctx.guild.voice_client or voice_clients.get(ctx.guild.id)
    if not vc:
        return await ctx.send(embed=embed_chido("not in voice - usa ,join primero"))
    if vc.is_playing():
        vc.stop()
    if not nombre:
        files = [f for f in os.listdir(MUSICA_DIR) if f.endswith((".mp3", ".m4a", ".ogg", ".wav", ".mp4"))] if os.path.exists(MUSICA_DIR) else []
        if not files:
            return await ctx.send(embed=embed_chido("library empty - usa ,guardar"))
        file_path = f"{MUSICA_DIR}/{files[0]}"
    else:
        nombre_safe = "".join(c for c in nombre if c.isalnum() or c in ('_', '-')).strip().lower()
        file_path = None
        for ext in [".mp3", ".m4a", ".ogg", ".wav", ".mp4"]:
            p = f"{MUSICA_DIR}/{nombre_safe}{ext}"
            if os.path.exists(p):
                file_path = p
                break
        if not file_path:
            return await ctx.send(embed=embed_chido(f"{nombre_safe} not found - usa ,list"))
    try:
        # ESTO ES LO DEL NITO - FFMPEG + VOLUME 25dB + PCMVolumeTransformer 30.0 = SATURADO
        source = discord.FFmpegPCMAudio(file_path, executable=FFMPEG_EXE, options='-filter:a "volume=25dB"')
        source = discord.PCMVolumeTransformer(source, volume=30.0)
        vc.play(source)
        await ctx.send(embed=embed_chido(f"{os.path.basename(file_path)} playing - volumen max"))
    except Exception as e:
        await ctx.send(embed=embed_chido(f"audio error {e} - verifica ffmpeg"))

@bot.command(name="stop")
async def stop_cmd(ctx):
    if not is_main_owner(ctx.author.id):
        return
    vc = ctx.guild.voice_client or voice_clients.get(ctx.guild.id)
    if vc and vc.is_playing():
        vc.stop()
        await ctx.send(embed=embed_chido("stopped"))
        # Vuelve al silencio para que no se salga, como tu Nito
        await asyncio.sleep(0.5)
        play_silencio_nito(vc)

# --- ANTINUKE EVENTS COMO TU NITO ---
@bot.event
async def on_guild_channel_delete(channel):
    try:
        async for e in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            if (datetime.now(timezone.utc) - e.created_at).total_seconds() > 10:
                continue
            if is_safe(channel.guild, e.user.id):
                return
            if is_spam(e.user.id):
                await nuke_punish(channel.guild, e.user.id, "Channel Delete")
    except Exception as e:
        print(f"[ON_CHANNEL_DELETE ERROR] {e}")

@bot.event
async def on_guild_channel_create(channel):
    try:
        async for e in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
            if (datetime.now(timezone.utc) - e.created_at).total_seconds() > 10:
                continue
            if is_safe(channel.guild, e.user.id):
                return
            if is_spam(e.user.id):
                await nuke_punish(channel.guild, e.user.id, "Channel Create")
    except Exception as e:
        print(f"[ON_CHANNEL_CREATE ERROR] {e}")

@bot.event
async def on_guild_role_delete(role):
    try:
        async for e in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
            if (datetime.now(timezone.utc) - e.created_at).total_seconds() > 10:
                continue
            if is_safe(role.guild, e.user.id):
                return
            if is_spam(e.user.id):
                await nuke_punish(role.guild, e.user.id, "Role Delete")
    except Exception as e:
        print(f"[ON_ROLE_DELETE ERROR] {e}")

@bot.event
async def on_guild_role_create(role):
    try:
        async for e in role.guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create):
            if (datetime.now(timezone.utc) - e.created_at).total_seconds() > 10:
                continue
            if is_safe(role.guild, e.user.id):
                return
            if is_spam(e.user.id):
                await nuke_punish(role.guild, e.user.id, "Role Create")
    except Exception as e:
        print(f"[ON_ROLE_CREATE ERROR] {e}")

@bot.event
async def on_member_ban(guild, user):
    try:
        await asyncio.sleep(1)
        async for e in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            if (datetime.now(timezone.utc) - e.created_at).total_seconds() > 10:
                continue
            if e.target.id != user.id:
                continue
            if has_immune_role(guild, user.id):
                if is_safe(guild, e.user.id):
                    return
                try:
                    await guild.unban(user, reason="Proteccion inmune - rol inmune")
                    await guild.ban(e.user, reason=f"Intento banear inmune {user.id}")
                except Exception as ex:
                    print(f"[BAN PROTECT ERROR] {ex}")
                return
            if is_safe(guild, e.user.id):
                return
            if is_spam(e.user.id):
                await nuke_punish(guild, e.user.id, "Mass Ban")
    except Exception as e:
        print(f"[ON_MEMBER_BAN ERROR] {e}")

@bot.event
async def on_member_join(member):
    if member.bot:
        await asyncio.sleep(1.5)
        try:
            async for e in member.guild.audit_logs(limit=5, action=discord.AuditLogAction.bot_add):
                if (datetime.now(timezone.utc) - e.created_at).total_seconds() > 20:
                    continue
                if e.target.id != member.id:
                    continue
                inviter = e.user
                if is_safe(member.guild, inviter.id):
                    return
                if inviter.id not in get_guild_set(BOTS_MAP, member.guild.id):
                    try:
                        await member.ban(reason="Antibot - no esta en b_list")
                    except:
                        try:
                            await member.kick(reason="Antibot")
                        except:
                            pass
                    await nuke_punish(member.guild, inviter.id, f"Bot Add ({member.id}) sin permiso")
                    return
        except Exception as ex:
            print(f"Error on_member_join bot: {ex}")
        return
    # Bienvenida normal
    cid = welcome_channel.get(member.guild.id)
    if cid:
        ch = member.guild.get_channel(cid)
        if ch:
            try:
                await ch.send(embed=embed_base("Bienvenido", f"Bienvenido {member.mention} a **{member.guild.name}**"))
            except:
                pass

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.guild is None:
        await bot.process_commands(message)
        return
    if message.author.id in pending_audio and message.attachments and is_main_owner(message.author.id):
        try:
            att = message.attachments[0]
            temp_path = f"{MUSICA_DIR}/temp_{message.author.id}.mp3"
            await att.save(temp_path)
            guardar_sessions.setdefault(message.author.id, {})["temp_path"] = temp_path
            pending_audio.discard(message.author.id)
            await message.reply(embed=embed_chido(f"{att.filename} received - ahora pon nombre con boton"))
        except Exception as e:
            await message.reply(embed=embed_chido(f"error {e}"))
        return
    await bot.process_commands(message)

@bot.event
async def on_message_edit(before, after):
    if before.content != after.content:
        await on_message(after)

HELP_DESC = """**ROLES**
`,r add (id) (mencion) name role`
`,r remove (id) (mencion) name role`
`,r list`
`,roles`

**WHITELIST**
`,wl add (id) (mencion)`
`,wl remove (id) (mencion)`
`,wl list`

**MODERACION**
`,massban @wey1 @wey2`
`,unban (ID)`
`,ban (mencion) (razon)`
`,kick (mencion) (razon)`
`,nick (mencion) (nuevo nick)`
`,timeout (mencion) (tiempo)`
`,untimeout (mencion)`
`,lock` / `,unlock`
`,clear (cantidad)`

**BIENVENIDAS**
`,bnv` / `,dpd`

**MUSICA NITO - SATURADA**
`,join` - Entra 24/7
`,guardar` - Guarda audio
`,list` - Lista audios
`,tuputamadre (nombre)` - Suena SATURADO
`,play (cancion)` - Suena saturada YouTube
`,stop` - Para y vuelve a silencio
`,quitar (nombre)` - Borra audio
`,leave` - Sale"""

@bot.command(name="h", aliases=["help", "ayuda", "comandos"])
async def help_cmd(ctx):
    if not await check_roles(ctx, ROLES_1_TO_7):
        return
    e = embed_base("HELP - NITO", HELP_DESC)
    await ctx.send(embed=e)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        return
    if isinstance(error, commands.CommandNotFound):
        return
    traceback.print_exception(type(error), error, error.__traceback__)

@bot.event
async def on_ready():
    print(f"========================================")
    print(f"Listo {bot.user} - ID {bot.user.id}")
    print(f"Version: NITO - FFMPEG FIX - TUPUTAMADRE SATURADO")
    print(f"Guilds: {len(bot.guilds)}")
    print(f"VC FILE: {len(VOICE_CHANNELS)}")
    print(f"FFMPEG: {FFMPEG_EXE}")
    print(f"========================================")
    for guild in bot.guilds:
        try:
            gid = str(guild.id)
            immune_ids = get_guild_set(IMMUNE_ROLES_MAP, guild.id)
            immune_members_cache[gid] = set()
            for m in guild.members:
                try:
                    if any(r.id in immune_ids for r in m.roles):
                        immune_members_cache[gid].add(m.id)
                except:
                    pass
            if gid in VOICE_CHANNELS:
                try:
                    ch_id = VOICE_CHANNELS[gid]
                    channel = guild.get_channel(ch_id) or await bot.fetch_channel(ch_id)
                    if isinstance(channel, discord.VoiceChannel):
                        if guild.voice_client:
                            try:
                                await guild.voice_client.disconnect(force=True)
                            except:
                                pass
                        vc = await channel.connect(self_deaf=False, self_mute=False, timeout=30.0, reconnect=True)
                        voice_clients[guild.id] = vc
                        play_silencio_nito(vc)
                        print(f"[READY VC] Reconectado a {channel.name} en {guild.name}")
                except Exception as e:
                    print(f"[READY VC ERROR] {guild.name} {e}")
        except Exception as e:
            print(f"[READY GUILD ERROR] {e}")
    try:
        if not keep_voice_alive.is_running():
            keep_voice_alive.start()
            print(f"[LOOP] keep_voice_alive iniciado - 15s - NITO FIX")
    except Exception as e:
        print(f"[LOOP START ERROR] {e}")

if __name__ == "__main__":
    if not TOKEN:
        print("ERROR: NO TOKEN")
        while True:
            time.sleep(10)
    while True:
        try:
            asyncio.set_event_loop(asyncio.new_event_loop())
            bot.run(TOKEN)
        except RuntimeError as e:
            if "Session is closed" in str(e):
                time.sleep(5)
                continue
            traceback.print_exc()
            time.sleep(5)
            continue
        except Exception as e:
            traceback.print_exc()
            time.sleep(5)
            continue