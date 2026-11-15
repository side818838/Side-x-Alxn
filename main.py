import discord
from discord.ext import commands, tasks
import asyncio
import json
import os
import time
from datetime import datetime, timedelta, timezone
from collections import defaultdict

TOKEN = os.getenv("DISCORD_BOT_TOKEN") or os.getenv("TOKEN")
PREFIX = ","

OWNER_IDS = [1310357536087740450]

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

ANTINUKE_ENABLED = True
ANTINUKE_LIMIT = 3
ANTINUKE_TIME = 10
ANTINUKE_BAN_REASON = "Anti-Nuke: Accion masiva detectada"

DATA_FILE = "data.json"
LOG_FILE = "logs.txt"

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, help_command=None, case_insensitive=True)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"whitelist": [], "welcome_channel": {}, "goodbye_channel": {}, "voice_stay": {}, "voice_lock": {}}

def save_data():
    try:
        data = {"whitelist": list(whitelist), "welcome_channel": welcome_channel, "goodbye_channel": goodbye_channel, "voice_stay": voice_stay, "voice_lock": voice_lock}
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Error guardando data: {e}")

def log_to_file(text):
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{now}] {text}\n")
    except:
        pass

_saved = load_data()
whitelist = set(_saved.get("whitelist", []))
welcome_channel = {int(k): v for k, v in _saved.get("welcome_channel", {}).items()}
goodbye_channel = {int(k): v for k, v in _saved.get("goodbye_channel", {}).items()}
voice_stay = {int(k): v for k, v in _saved.get("voice_stay", {}).items()}
voice_lock = {int(k): v for k, v in _saved.get("voice_lock", {}).items()}

action_log = defaultdict(list)
antinuke_bans = defaultdict(int)
_ultimo_intento_voz = {}
_intentos_voz = defaultdict(int)

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

async def antinuke_check(guild, user, action_name):
    if not ANTINUKE_ENABLED:
        return False
    if user is None or user.bot:
        return False
    if user.id in OWNER_IDS or user.id in whitelist:
        return False
    now = datetime.now(timezone.utc)
    key = (guild.id, user.id, action_name)
    action_log[key] = [t for t in action_log[key] if (now - t).total_seconds() < ANTINUKE_TIME]
    action_log[key].append(now)
    if len(action_log[key]) >= ANTINUKE_LIMIT:
        try:
            await guild.ban(user, reason=ANTINUKE_BAN_REASON)
            antinuke_bans[user.id] += 1
            log_to_file(f"ANTINUKE: Baneado {user} ({user.id}) en {guild.name} por {action_name} x{len(action_log[key])}")
            print(f"[ANTI-NUKE] Baneado {user} por {action_name}")
        except Exception as e:
            print(f"[ANTI-NUKE] No se pudo banear {user}: {e}")
            log_to_file(f"ANTINUKE ERROR: No se pudo banear {user}: {e}")
        action_log[key] = []
        return True
    return False

async def get_audit_user(guild, action):
    try:
        async for entry in guild.audit_logs(limit=1, action=action):
            diff = (datetime.now(timezone.utc) - entry.created_at).total_seconds()
            if diff < 5:
                return entry.user
    except Exception as e:
        print(f"Audit error: {e}")
    return None

@bot.event
async def on_guild_channel_delete(channel):
    user = await get_audit_user(channel.guild, discord.AuditLogAction.channel_delete)
    if user:
        await antinuke_check(channel.guild, user, "channel_delete")

@bot.event
async def on_guild_channel_create(channel):
    user = await get_audit_user(channel.guild, discord.AuditLogAction.channel_create)
    if user:
        await antinuke_check(channel.guild, user, "channel_create")

@bot.event
async def on_guild_channel_update(before, after):
    user = await get_audit_user(after.guild, discord.AuditLogAction.channel_update)
    if user:
        await antinuke_check(after.guild, user, "channel_update")

@bot.event
async def on_member_ban(guild, user):
    audit_user = await get_audit_user(guild, discord.AuditLogAction.ban)
    if audit_user:
        await antinuke_check(guild, audit_user, "ban")

@bot.event
async def on_guild_role_create(role):
    user = await get_audit_user(role.guild, discord.AuditLogAction.role_create)
    if user:
        await antinuke_check(role.guild, user, "role_create")

@bot.event
async def on_guild_role_delete(role):
    user = await get_audit_user(role.guild, discord.AuditLogAction.role_delete)
    if user:
        await antinuke_check(role.guild, user, "role_delete")

@bot.event
async def on_guild_role_update(before, after):
    user = await get_audit_user(after.guild, discord.AuditLogAction.role_update)
    if user:
        await antinuke_check(after.guild, user, "role_update")

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
    r = discord.utils.get(guild.roles, name=query)
    if r:
        return r
    for role in guild.roles:
        if role.name.lower() == query.lower():
            return role
    for role in guild.roles:
        if query.lower() in role.name.lower():
            return role
    return None

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
            if role in target.roles:
                await ctx.send(embed=embed_error(f"{target.mention} ya tiene `{role.name}`"))
                return
            await target.add_roles(role, reason=f"Role add por {ctx.author}")
            await ctx.send(embed=embed_success("Role Added", f"`{role.name}` para {target.mention}\nPuesto por: {ctx.author.mention}"))
            log_to_file(f"ROLE ADD: {ctx.author} dio {role.name} a {target} en {ctx.guild.name}")
        else:
            if role not in target.roles:
                await ctx.send(embed=embed_error(f"{target.mention} no tiene `{role.name}`"))
                return
            await target.remove_roles(role, reason=f"Role remove por {ctx.author}")
            await ctx.send(embed=embed_success("Role Removed", f"`{role.name}` quitado de {target.mention}\nQuitado por: {ctx.author.mention}"))
            log_to_file(f"ROLE REMOVE: {ctx.author} quito {role.name} a {target}")
    except discord.Forbidden:
        await ctx.send(embed=embed_error("No tengo permisos para manejar ese rol. Pon mi rol mas arriba."))
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
    try:
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
                if m:
                    lst.append(f"{m.mention} - `{uid}`")
                else:
                    lst.append(f"ID: `{uid}`")
            await ctx.send(embed=embed_base("Whitelist", "\n".join(lst)))
            return
        if action == "clear":
            whitelist.clear()
            save_data()
            await ctx.send(embed=embed_success("Whitelist", "Limpiada por completo"))
            return
        if action not in ["add", "remove", "quitar", "agregar"]:
            await ctx.send(embed=usage_embed(",wl add (id) (mencion)"))
            return
        target = member
        if target is None and user_arg:
            target = find_member(ctx.guild, user_arg)
        target_id = None
        if target:
            target_id = target.id
        elif user_arg and user_arg.isdigit():
            target_id = int(user_arg)
        elif member:
            target_id = member.id
        if target_id is None:
            await ctx.send(embed=usage_embed(",wl add (id) (mencion)"))
            return
        if action in ["add", "agregar"]:
            if target_id in whitelist:
                await ctx.send(embed=embed_error("Ya esta en whitelist"))
                return
            whitelist.add(target_id)
            save_data()
            display = target.mention if target else f"`{target_id}`"
            await ctx.send(embed=embed_success("Whitelist", f"{display} agregado a whitelist\nPor: {ctx.author.mention}"))
            log_to_file(f"WL ADD: {ctx.author} agrego {target_id}")
        else:
            if target_id not in whitelist:
                await ctx.send(embed=embed_error("No esta en whitelist"))
                return
            whitelist.discard(target_id)
            save_data()
            display = target.mention if target else f"`{target_id}`"
            await ctx.send(embed=embed_success("Whitelist", f"{display} quitado de whitelist"))
            log_to_file(f"WL REMOVE: {ctx.author} quito {target_id}")
    except Exception as e:
        await ctx.send(embed=embed_error(f"Error: `{e}`"))

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
    await ctx.send(embed=embed_success("Massban", f"Baneados: `{count}`\nFallidos: `{fails}`\nPor: {ctx.author.mention}"))
    log_to_file(f"MASSBAN: {ctx.author} baneo {count} en {ctx.guild.name}")

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
        await ctx.send(embed=embed_success("Unban", f"Desbaneado: `{user.name}` - `{user.id}`"))
    except discord.NotFound:
        await ctx.send(embed=embed_error("Ese ID no esta baneado o no existe"))
    except Exception as e:
        await ctx.send(embed=embed_error(f"No se pudo desbanear: `{e}`"))

@bot.command(name="unbanmass")
async def unbanmass_cmd(ctx, *, ids_text=None):
    if not await check_owner(ctx):
        return
    if not ids_text:
        await ctx.send(embed=usage_embed(",unbanmass + lista de IDs abajo"))
        await ctx.send(embed=embed_base("Ejemplo", "`,unbanmass\n123456789\n987654321\n555555555`"))
        return
    count = 0
    fails = 0
    for part in ids_text.replace(",", " ").replace("\n", " ").split():
        try:
            uid = int(part)
            user = await bot.fetch_user(uid)
            await ctx.guild.unban(user, reason=f"Unbanmass por {ctx.author}")
            count += 1
        except:
            fails += 1
    await ctx.send(embed=embed_success("Unbanmass", f"Desbaneados: `{count}`\nFallidos: `{fails}`"))

@bot.command(name="ban")
async def ban_cmd(ctx, member: discord.Member = None, *, reason="Sin razon"):
    if not await check_roles(ctx, ROLES_1_TO_2):
        return
    if not member:
        await ctx.send(embed=usage_embed(",ban (mencion) (razon)"))
        return
    if member.id in OWNER_IDS:
        await ctx.send(embed=embed_error("No puedes banear a un Owner"))
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(embed=embed_success("Ban", f"{member.mention} baneado\nRazon: `{reason}`\nPor: {ctx.author.mention}"))
        log_to_file(f"BAN: {ctx.author} baneo {member} razon: {reason}")
    except Exception as e:
        await ctx.send(embed=embed_error(f"Error: `{e}`"))

@bot.command(name="kick")
async def kick_cmd(ctx, member: discord.Member = None, *, reason="Sin razon"):
    if not await check_roles(ctx, ROLES_1_TO_2):
        return
    if not member:
        await ctx.send(embed=usage_embed(",kick (mencion) (razon)"))
        return
    if member.id in OWNER_IDS:
        await ctx.send(embed=embed_error("No puedes kickear a un Owner"))
        return
    try:
        await member.kick(reason=reason)
        await ctx.send(embed=embed_success("Kick", f"{member.mention} expulsado\nRazon: `{reason}`\nPor: {ctx.author.mention}"))
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
        log_to_file(f"NICK: {ctx.author} cambio nick de {member} a {new_nick}")
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
        await ctx.send(embed=embed_success("Timeout", f"{member.mention} muteado por `{format_time(seconds)}`\nRazon: `{reason}`"))
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
    if cantidad > 500:
        await ctx.send(embed=embed_error("Maximo 500 mensajes"))
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
            await interaction.response.send_message(embed=embed_success("Bienvenidas", f"Canal puesto: <#{cid}>\nGuardado para siempre"), ephemeral=True)
        else:
            goodbye_channel[interaction.guild_id] = cid
            save_data()
            await interaction.response.send_message(embed=embed_success("Despedidas", f"Canal puesto: <#{cid}>\nGuardado para siempre"), ephemeral=True)

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
    try:
        audit_user = await get_audit_user(member.guild, discord.AuditLogAction.kick)
        if audit_user:
            await antinuke_check(member.guild, audit_user, "kick")
    except:
        pass
    cid = goodbye_channel.get(member.guild.id)
    if cid:
        ch = member.guild.get_channel(cid)
        if ch:
            try:
                await ch.send(embed=embed_base("Despedida", f"Se fue {member.mention} de **{member.guild.name}**\nEramos `{member.guild.member_count + 1}` y ahora somos `{member.guild.member_count}`"))
            except:
                pass

@tasks.loop(seconds=60)
async def mantener_voz():
    if not voice_stay:
        return
    for guild in bot.guilds:
        ch_id = voice_stay.get(guild.id)
        if not ch_id:
            continue
        try:
            vc = guild.voice_client
            bot_member = guild.get_member(bot.user.id)
            realmente_en_voz = bot_member.voice and bot_member.voice.channel if bot_member else None
            if vc and vc.is_connected() and realmente_en_voz and realmente_en_voz.id == ch_id:
                _intentos_voz[guild.id] = 0
                continue
            ahora = time.time()
            if ahora - _ultimo_intento_voz.get(guild.id, 0) < 50:
                continue
            _ultimo_intento_voz[guild.id] = ahora
            _intentos_voz[guild.id] += 1
            ch = guild.get_channel(ch_id)
            if not ch:
                voice_stay.pop(guild.id, None)
                save_data()
                continue
            if vc and not vc.is_connected():
                try:
                    await vc.disconnect(force=True)
                except:
                    pass
                await asyncio.sleep(1)
            await ch.connect(self_deaf=True, self_mute=True, reconnect=True)
            _intentos_voz[guild.id] = 0
        except Exception as e:
            print(f"[VOZ] No pude reconectar en {guild.name}: {e}")

@bot.command(name="join")
async def join_cmd(ctx):
    if not await check_owner(ctx):
        return
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send(embed=embed_error("Tienes que estar en un canal de voz para usar `,join`"))
        return
    ch = ctx.author.voice.channel
    msg = await ctx.send(embed=embed_base("Voice", f"Conectando a `{ch.name}`..."))
    try:
        voice_stay[ctx.guild.id] = ch.id
        save_data()
        _intentos_voz[ctx.guild.id] = 0
        vc = ctx.guild.voice_client
        if vc and not vc.is_connected():
            try:
                await vc.disconnect(force=True)
            except:
                pass
            vc = None
            await asyncio.sleep(1)
        bot_member = ctx.guild.get_member(bot.user.id)
        realmente_en_voz = bot_member.voice and bot_member.voice.channel
        if realmente_en_voz and realmente_en_voz.id == ch.id and vc and vc.is_connected():
            await msg.edit(embed=embed_success("Voice", f"Ya estoy en `{ch.name}` y ahí me quedo 24/7"))
            return
        if vc and vc.is_connected():
            await vc.move_to(ch)
            try:
                await ctx.guild.change_voice_state(channel=ch, self_mute=True, self_deaf=True)
            except:
                pass
        else:
            await ch.connect(self_deaf=True, self_mute=True, reconnect=True)
        await msg.edit(embed=embed_success("Voice", f"Conectado a `{ch.name}` - Me quedo 24/7 solo activando"))
    except Exception as e:
        try:
            await msg.edit(embed=embed_error(f"Error al entrar: `{e}`"))
        except:
            await ctx.send(embed=embed_error(f"Error al entrar: `{e}`"))

@bot.command(name="leave")
async def leave_cmd(ctx):
    if not await check_owner(ctx):
        return
    voice_stay.pop(ctx.guild.id, None)
    save_data()
    _intentos_voz[ctx.guild.id] = 0
    vc = ctx.guild.voice_client
    bot_member = ctx.guild.get_member(bot.user.id)
    realmente_en_voz = bot_member.voice and bot_member.voice.channel
    if not vc and not realmente_en_voz:
        await ctx.send(embed=embed_error("Ni siquiera estoy en voz"))
        return
    try:
        if vc:
            await vc.disconnect(force=True)
    except:
        pass
    try:
        if realmente_en_voz:
            await bot_member.move_to(None)
    except:
        pass
    await asyncio.sleep(1)
    await ctx.send(embed=embed_success("Voice", "Desconectado"))

HELP_DESC = """**ROLES**
`,r add (id) (mencion) name role`
`,r remove (id) (mencion) name role`
`,r list`
`,roles`

**WHITELIST**
`,wl add (id) (mencion)`
`,wl remove (id) (mencion)`
`,wl list`
`,wl clear`

**MODERACION - OWNERS**
`,massban @wey1 @wey2`
`,unban (ID)`
`,unbanmass`

**MODERACION - ROL 1 Y 2**
`,ban (mencion) (razon)`
`,kick (mencion) (razon)`
`,nick (mencion) (nuevo nick)`
`,timeout (mencion) (tiempo)`
`,untimeout (mencion)`
`,lock`
`,unlock`

**MODERACION - ROL 1 AL 5**
`,clear (cantidad)`

**BIENVENIDAS / DESPEDIDAS - OWNERS**
`,bnv`
`,dpd`

**VOICE - OWNERS**
`,join`
`,leave`

**HELP**
`,h` / `,help` / `,ayuda`"""

@bot.command(name="h", aliases=["help", "ayuda"])
async def help_cmd(ctx):
    if not await check_roles(ctx, ROLES_1_TO_7):
        return
    e = embed_base("HELP - TODOS LOS COMANDOS", HELP_DESC)
    e.set_footer(text="Solo Rol 1 al 7 puede ver este panel")
    await ctx.send(embed=e)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=usage_embed(f"{PREFIX}{ctx.command} - Te falta un argumento"))
        return
    if isinstance(error, commands.BadArgument):
        await ctx.send(embed=embed_error("Argumento invalido. Revisa el usage con `,h`"))
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(embed=no_perm_embed())
        return
    print(f"Error en comando {ctx.command}: {error}")
    log_to_file(f"ERROR COMANDO {ctx.command}: {error}")

@bot.event
async def on_ready():
    print(f"Bot listo: {bot.user}")
    print(f"Servers: {len(bot.guilds)}")
    print(f"Whitelist cargada: {len(whitelist)}")
    print(f"Anti-Nuke: {'PRENDIDO' if ANTINUKE_ENABLED else 'APAGADO'}")
    print(f"Voice: {voice_stay}")
    if not mantener_voz.is_running():
        mantener_voz.start()

if __name__ == "__main__":
    bot.run(TOKEN)