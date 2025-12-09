import os
import json
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from datetime import datetime, timezone

# ---------------------------
# Load environment variables
# ---------------------------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ---------------------------
# Load / Save Config
# ---------------------------
CONFIG_FILE = "config.json"

def load_config():
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)

config = load_config()

# ---------------------------
# Helper: Format dates nicely
# ---------------------------
def format_date(dt: datetime):
    return dt.strftime("%B %d, %Y • %I:%M %p")

# ---------------------------
# Intents
# ---------------------------
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ---------------------------
# Permission Check
# ---------------------------
def is_admin(member: discord.Member):
    admin_roles = config.get("admin_roles", [])
    return any(role.name in admin_roles for role in member.roles)

# ---------------------------
# Ready Event
# ---------------------------
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🚀 Bot is online as {bot.user}!")
    print("🔧 Slash commands synced.")

# ---------------------------
# Event: Member Join
# ---------------------------
@bot.event
async def on_member_join(member: discord.Member):

    # Load channels from config
    welcome_channel_name = config.get("welcome_channel", "welcome")
    modlog_channel_name = config.get("mod_log_channel", "mod-log")
    min_age = config.get("min_account_age", 2)
    auto_role_new = config.get("auto_role_new", "")

    channel = discord.utils.get(member.guild.text_channels, name=welcome_channel_name)
    mod_log = discord.utils.get(member.guild.text_channels, name=modlog_channel_name)

    if channel is None:
        print("⚠️ No welcome channel found.")
        return

    # Calculate account age
    now = datetime.now(timezone.utc)
    account_age_days = (now - member.created_at).days

    embed = discord.Embed(
        title="🎉 Welcome!",
        description=f"Glad you're here, **{member.mention}**!",
        color=0x9b59b6
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(name="🧑 Profile Name", value=member.display_name, inline=False)
    embed.add_field(name="👤 Username", value=member.name, inline=True)
    #embed.add_field(name="🌐 Global Name", value=member.global_name or "N/A", inline=True)

    embed.add_field(name="📅 Account Created", value=format_date(member.created_at), inline=False)
    embed.add_field(name="⏳ Account Age", value=f"{account_age_days} days old", inline=True)
    embed.add_field(name="🚪 Member Number", value=len(member.guild.members), inline=True)

    # Add suspicious warning
    if account_age_days < min_age:
        embed.add_field(
            name="⚠️ Warning",
            value=f"This account is very new (age: {account_age_days} days).",
            inline=False
        )

    embed.set_footer(text="Enjoy your stay!")

    await channel.send(embed=embed)

    # Send mod alert
    if account_age_days < min_age and mod_log:
        alert = discord.Embed(
            title="⚠ Suspicious Account Joined",
            description=f"{member.mention} (age: {account_age_days} days)",
            color=0xe67e22
        )
        alert.set_thumbnail(url=member.display_avatar.url)
        await mod_log.send(embed=alert)

    # Auto-role new accounts
    if auto_role_new and account_age_days < min_age:
        role = discord.utils.get(member.guild.roles, name=auto_role_new)
        if role:
            await member.add_roles(role)

# ---------------------------
# Event: Member Leave
# ---------------------------
@bot.event
async def on_member_remove(member: discord.Member):

    goodbye_channel_name = config.get("goodbye_channel", "goodbye")
    channel = discord.utils.get(member.guild.text_channels, name=goodbye_channel_name)

    if channel is None:
        print("⚠️ No goodbye channel found.")
        return

    embed = discord.Embed(
        title="👋 Goodbye!",
        description=f"{member.name} has left the server.",
        color=0xe74c3c
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(name="🧑 Profile Name", value=member.display_name, inline=False)
    embed.add_field(name="👤 Username", value=member.name, inline=True)
    #embed.add_field(name="🌐 Global Name", value=member.global_name or "N/A", inline=True)
    embed.add_field(name="📅 Account Created", value=format_date(member.created_at), inline=False)

    embed.set_footer(text="We hope to see you again.")

    await channel.send(embed=embed)

# ---------------------------
# Slash Command: Test Welcome
# ---------------------------
@bot.tree.command(name="test_welcome", description="Show your welcome message preview")
async def test_welcome(interaction: discord.Interaction):

    user = interaction.user
    now = datetime.now(timezone.utc)
    account_age_days = (now - user.created_at).days

    embed = discord.Embed(
        title="🎉 Test Welcome Message",
        description=f"This is how your welcome message looks.",
        color=0x3498db
    )

    embed.set_thumbnail(url=user.display_avatar.url)

    embed.add_field(name="🧑 Profile Name", value=user.display_name, inline=False)
    embed.add_field(name="👤 Username", value=user.name, inline=True)
    embed.add_field(name="⏳ Account Age", value=f"{account_age_days} days", inline=True)
    embed.add_field(name="📅 Account Created", value=format_date(user.created_at), inline=False)
    #embed.add_field(name="🌐 Global Name", value=user.global_name or "N/A", inline=True)
    
    

    await interaction.response.send_message(embed=embed, ephemeral=True)

# ---------------------------
# ADMIN COMMAND — Update Config
# ---------------------------
@bot.tree.command(name="setconfig", description="Update bot configuration")
@app_commands.describe(key="Config field to update", value="New value")
async def setconfig(interaction: discord.Interaction, key: str, value: str):

    if not is_admin(interaction.user):
        await interaction.response.send_message("❌ You do not have permission.", ephemeral=True)
        return

    if key not in config:
        await interaction.response.send_message("❌ Invalid config key.", ephemeral=True)
        return

    # Save change
    config[key] = value
    save_config(config)

    await interaction.response.send_message(f"✅ Updated `{key}` to `{value}`")

# ---------------------------
# Run the bot
# ---------------------------

@bot.event
async def on_ready():
    # Set status to show a slash command
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="/welcome"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)

    await bot.tree.sync()
    print(f"🚀 Bot is online as {bot.user}!")
    print("🔧 Slash commands synced.")

bot.run(TOKEN)
