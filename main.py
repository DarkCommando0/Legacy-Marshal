import discord
from discord.ext import commands, tasks
from flask import Flask, send_file
from threading import Thread
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")  # Load token only from .env
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN not found in .env file")

# Flask setup for keep-alive
app = Flask('')
@app.route('/')
def home():
    return "LegacyMarshal LFG Bot is operational!"
@app.route('/favicon.ico')
def favicon():
    return send_file('static/favicon.ico', mimetype='image/x-icon') if os.path.exists('static/favicon.ico') else ('', 204)
def run_flask():
    app.run(host='0.0.0.0', port=5000, threaded=True)
def keep_alive():
    t = Thread(target=run_flask, daemon=True)
    t.start()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True  # Needed for prefix commands
intents.guilds = True  # Needed for guild and role events
intents.members = True  # Needed for bot member info
bot = commands.Bot(command_prefix="!", intents=intents)  # Pass intents here

# Define desired role order with actual role IDs
desiredRoleOrder = [
    '1361851144350994502',  # BF Legacy Unbound Team
    '1361885428516389035',  # Owner
    '1376982714561069158',  # Team Droids
    '1374140680380743814',  # LegacyMarshal
    '1362476681356509427',  # Droids
    '1369803214765162749',  # D5-BD
    '1363371322373046418',  # Q1-TX
    '1374083454668505222',  # R3-KT
    '1366050907862863955',  # T1-VC
    '1363221290747433100',  # TH3-DX
    '1380201310711840949',  # KYBER Team Manager
    '1363638233208062155',  # KYBER Team
    '1364773133197905952',  # Content Creators
    '1362644827883180142',  # Legacy Unbound Tester
    '1373174776985681970',  # Kyber Luminary
    '1362488297510797443',  # Guardian
    '1362488420299047024',  # Consular
    '1362488467757465981',  # Marauder
    '1362488521671311601',  # Sentinel
    '1362488684469026976',  # Mandalorian
    '1362488725111705650',  # Balanced
    '1362490015648579845',  # Inquisitor
    '1362490083017625640',  # Sorcerer
    '1362489042821972219',  # Grey Warden
    '1364271161000591430',  # LFG-KYBER
    '1364262718487531581',  # LFG-VANILLA
    '1365936777176682547',  # LFG-SWTOR
    '1371897792695369778',  # LFG-CLASSIC2005
    '1371895939786080297',  # LFG-CLASSIC2004
    '1377310669954875572',  # PhantomZone
]

# Cache for role positions (to avoid unnecessary updates)
role_position_cache = {}

async def check_and_reorder_roles(force=False):
    print('🔍 Checking role order...', 'Forced' if force else '')
    try:
        guild = bot.guilds[0] if bot.guilds else None
        if guild:
            print(f"Connected to guild: {guild.name} (ID: {guild.id})")
        if not guild:
            print('❌ No guild found for role reordering')
            return

        bot_member = guild.get_member(bot.user.id)
        if not bot_member:
            print('❌ Bot member not found in guild')
            return

        print(f'ℹ️ Bot: {bot.user.name}#{bot.user.discriminator}, Role: {bot_member.top_role.name}, Position: {bot_member.top_role.position}')
        if not bot_member.guild_permissions.manage_roles:
            print('❌ Bot lacks MANAGE_ROLES permission for role reordering')
            return

        await guild.fetch_roles()
        print(f"Roles fetched: {len(guild.roles)} roles found")
        roles = guild.roles

        print('ℹ️ Available roles in guild:')
        for role in roles:
            print(f'- ID: {role.id}, Name: {role.name}, Position: {role.position}')

        current_order = {role.id: role.position for role in roles if role.id in desiredRoleOrder}

        is_out_of_order = force or any(
            role_id not in current_order or
            (not role_position_cache or current_order[role_id] != role_position_cache.get(role_id))
            for role_id in desiredRoleOrder
        )

        if not is_out_of_order and role_position_cache and not force:
            print('ℹ️ Role order is correct, no changes needed')
            return

        new_positions = []
        base_position = bot_member.top_role.position - 1  # Start just below the bot
        for role_id in desiredRoleOrder:
            role = discord.utils.get(roles, id=role_id)
            if role:
                if base_position < 1:  # Ensure we don’t go below the minimum position
                    print('❌ Position too low to assign roles; bot role position too low')
                    return
                new_positions.append((role, base_position))
                base_position -= 1  # Decrement for each role to move downward
            else:
                print(f'⚠️ Role {role_id} not found in guild - check ID or role existence')

        print('ℹ️ Intended role positions:')
        for role, position in new_positions:
            print(f'- ID: {role.id}, Name: {role.name}, New Position: {position}')

        try:
            if new_positions:
                await guild.edit_role_positions(new_positions)
                print('✅ Role positions updated successfully')
                role_position_cache.clear()
                for role in roles:
                    if role.id in desiredRoleOrder:
                        role_position_cache[role.id] = role.position
            else:
                print('⚠️ No valid roles to reorder')
        except discord.HTTPException as err:
            print(f'❌ Error updating role positions: {err}')
    except Exception as err:
        print(f'❌ Error in check_and_reorder_roles: {err}')

# Background task to periodically check and reorder roles
@tasks.loop(hours=12)  # Runs every 12 hours
async def auto_reorder_roles():
    await check_and_reorder_roles()

# Event to trigger reordering on guild role updates
@bot.event
async def on_guild_role_update(before, after):
    if after.id in desiredRoleOrder:
        print(f'🔄 Role {after.name} (ID: {after.id}) updated, triggering reorder')
        await check_and_reorder_roles(force=True)

# Custom prefix check to allow !! for sqclassic
def get_prefix(bot, message):
    prefixes = ["!"]
    if message.content.startswith("!!") and "sqclassic" in message.content.lower():
        return "!!"
    return prefixes

bot.command_prefix = get_prefix

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id}) at {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')} EDT")
    keep_alive()  # Start Flask keep-alive
    await check_and_reorder_roles()  # Initial reorder on startup
    auto_reorder_roles.start()  # Start the background task

# Intro message when bot joins a server
@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(
                title="LegacyMarshal Deployed",
                description="Greetings! I’m LegacyMarshal, your server’s squad coordinator. Use `!kybersquad-up`, `!vanillasquad-up`, `!swtorsquad-up`, `!classic2005squad-up`, or `!classic2004squad-up` to rally your squads! Add a number to specify players needed (e.g., `!kybersquad-up 3`).",
                color=discord.Color.dark_gold()
            )
            await channel.send(embed=embed)
            break

# Prefix LFG commands with custom messages and role mentions based on desiredRoleOrder
@bot.command(name="kybersquad-up")
async def kybersquad_up(ctx, players: int = None):
    # Use only LFG-KYBER role from desiredRoleOrder
    kyber_roles = [f"<@&{role_id}>" for role_id in desiredRoleOrder if 'LFG-KYBER' in desiredRoleOrder]
    description = f"Hey.. This sector isn’t going to take itself. {', '.join(kyber_roles)} Form up. We’ve got troopers in need of assistance."
    if players:
        description += f"\n**Players Needed:** {players}"
    embed = discord.Embed(
        title="KYBER Squad Up!",
        description=description,
        color=discord.Color.dark_green(),
        timestamp=discord.utils.utcnow()
    )
    await ctx.send(embed=embed)

@bot.command(name="vanillasquad-up")
async def vanillasquad_up(ctx, players: int = None):
    # Use roles from desiredRoleOrder that match VANILLA-related roles
    vanilla_roles = [f"<@&{role_id}>" for role_id in desiredRoleOrder if 'LFG-VANILLA' in desiredRoleOrder]
    description = f"Hey.. This sector isn’t going to take itself. {', '.join(vanilla_roles)} Form up. We’ve got troopers in need of assistance."
    if players:
        description += f"\n**Players Needed:** {players}"
    embed = discord.Embed(
        title="Vanilla Squad Up!",
        description=description,
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )
    await ctx.send(embed=embed)

@bot.command(name="swtorsquad-up")
async def swtorsquad_up(ctx, players: int = None):
    # Use roles from desiredRoleOrder that match SWTOR-related roles
    swtor_roles = [f"<@&{role_id}>" for role_id in desiredRoleOrder if 'LFG-SWTOR' in desiredRoleOrder]
    description = f"Hey.. Contract is active. {', '.join(swtor_roles)} Crew is forming up. Lock and load, mercs."
    if players:
        description += f"\n**Players Needed:** {players}"
    embed = discord.Embed(
        title="SWTOR Squad Up!",
        description=description,
        color=discord.Color.dark_blue(),
        timestamp=discord.utils.utcnow()
    )
    await ctx.send(embed=embed)

@bot.command(name="classic2005squad-up")
async def classic2005squad_up(ctx, players: int = None):
    # Use roles from desiredRoleOrder that match CLASSIC2005-related roles
    classic_roles = [f"<@&{role_id}>" for role_id in desiredRoleOrder if 'LFG-CLASSIC2005' in desiredRoleOrder]
    description = f"Hey.. This sector isn’t going to take itself. {', '.join(classic_roles)} Form up. We’ve got troopers in need of assistance."
    if players:
        description += f"\n**Players Needed:** {players}"
    embed = discord.Embed(
        title="SW Battlefront Classic 2005 Squad Up!",
        description=description,
        color=discord.Color.dark_gold(),
        timestamp=discord.utils.utcnow()
    )
    await ctx.send(embed=embed)

@bot.command(name="classic2004squad-up")
async def classic2004squad_up(ctx, players: int = None):
    # Use roles from desiredRoleOrder that match CLASSIC2004-related roles
    classic_roles = [f"<@&{role_id}>" for role_id in desiredRoleOrder if 'LFG-CLASSIC2004' in desiredRoleOrder]
    description = f"Hey.. This sector isn’t going to take itself. {', '.join(classic_roles)} Form up. We’ve got troopers in need of assistance."
    if players:
        description += f"\n**Players Needed:** {players}"
    embed = discord.Embed(
        title="SW Battlefront Classic 2004 Squad Up!",
        description=description,
        color=discord.Color.dark_gold(),
        timestamp=discord.utils.utcnow()
    )
    await ctx.send(embed=embed)

bot.run(TOKEN)