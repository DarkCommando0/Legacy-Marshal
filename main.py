import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True  # Needed for prefix commands
bot = commands.Bot(command_prefix="!")  # Default prefix is !
TOKEN = "MTM3Mzg3NTE4MzA2ODExOTE2MA.GyygYs.VOQfhJ0qcX3OEQeJZo-y5L-7Em6BtURBPHvvdw"  # Token provided

# Custom prefix check to allow !! for sqclassic
def get_prefix(bot, message):
    prefixes = ["!"]
    if message.content.startswith("!!") and "sqclassic" in message.content.lower():
        return "!!"
    return prefixes

bot.command_prefix = get_prefix

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user} (ID: {bot.user.id}) at {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M:%S')} EDT")
    print("Slash commands synced.")

# Intro message when bot joins a server
@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = discord.Embed(
                title="LegacyMarshal Deployed",
                description="Greetings! I’m LegacyMarshal, your server’s squad coordinator. Use `!ksquadup`, `!vsquadup`, `!swtorsquadup`, or `!!sqclassic` to rally your squads! Add a number to specify players needed (e.g., `!ksquadup 3`).",
                color=discord.Color.dark_gold()
            )
            await channel.send(embed=embed)
            break

# Prefix LFG commands with custom messages and role mentions
@bot.command(name="ksquadup")
async def ksquadup(ctx, players: int = None):
    description = "Hey.. This sector isn’t going to take itself. <@&1364271161000591430> Form up. We’ve got troopers in need of assistance."
    if players:
        description += f"\n**Players Needed:** {players}"
    embed = discord.Embed(
        title="KYBER Squad Up!",
        description=description,
        color=discord.Color.dark_green(),
        timestamp=discord.utils.utcnow()
    )
    await ctx.send(embed=embed)

@bot.command(name="sqclassic")
async def sqclassic(ctx, players: int = None):
    description = "Hey.. This sector isn’t going to take itself. <@&1371897792695369778> <@&1371895939786080297> Form up. We’ve got troopers in need of assistance."
    if players:
        description += f"\n**Players Needed:** {players}"
    embed = discord.Embed(
        title="SW Battlefront Classic Squad Up!",
        description=description,
        color=discord.Color.dark_gold(),
        timestamp=discord.utils.utcnow()
    )
    await ctx.send(embed=embed)

@bot.command(name="swtorsquadup")
async def swtorsquadup(ctx, players: int = None):
    description = "Hey.. Contract is active. <@&1365936777176682547> Crew is forming up. Lock and load, mercs."
    if players:
        description += f"\n**Players Needed:** {players}"
    embed = discord.Embed(
        title="SWTOR Squad Up!",
        description=description,
        color=discord.Color.dark_blue(),
        timestamp=discord.utils.utcnow()
    )
    await ctx.send(embed=embed)

@bot.command(name="vsquadup")
async def vsquadup(ctx, players: int = None):
    description = "Hey.. This sector isn’t going to take itself. <@&1364262718487531581> Form up. We’ve got troopers in need of assistance."
    if players:
        description += f"\n**Players Needed:** {players}"
    embed = discord.Embed(
        title="Vanilla Squad Up!",
        description=description,
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )
    await ctx.send(embed=embed)

bot.run(TOKEN)