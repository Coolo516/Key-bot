import discord
from discord.ext import commands
from discord import app_commands
import secrets
import asyncio

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True  # Required to manage roles
bot = commands.Bot(command_prefix="/", intents=intents)

# Dictionary to store generated keys and their associated role and duration
keys = {}

# Function to remove role after a delay
async def remove_role_after_delay(user, role, duration_minutes):
    await asyncio.sleep(duration_minutes * 60)  # Sleep for the specified duration
    try:
        await user.remove_roles(role)
        await user.send(f"Your role '{role.name}' has been removed after {duration_minutes} minutes.")
        print(f"Removed role '{role.name}' from user '{user.display_name}' after {duration_minutes} minutes.")
    except Exception as e:
        print(f"Error removing role: {e}")

# Command for admins to generate keys
@bot.tree.command(name="generate_key", description="Generate a key for a specific role and duration.")
@app_commands.describe(role="Role to assign", duration="Duration in minutes")
async def generate_key(interaction: discord.Interaction, role: discord.Role, duration: int):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    key = secrets.token_hex(8)  # Generate a random key
    keys[key] = {"role": role, "duration": duration, "redeemed": False}
    await interaction.response.send_message(f"Key generated: `{key}` for role {role.name} with duration {duration} minutes")
    print(f"Generated key '{key}' for role '{role.name}' with duration {duration} minutes")

# Command for users to redeem keys
@bot.tree.command(name="redeem", description="Redeem a key to get a role.")
@app_commands.describe(key="The key to redeem")
async def redeem(interaction: discord.Interaction, key: str):
    user = interaction.user
    if key not in keys or keys[key]["redeemed"]:
        await interaction.response.send_message("Invalid or already redeemed key.", ephemeral=True)
        return

    # Retrieve role and duration associated with the key
    role = keys[key]["role"]
    duration = keys[key]["duration"]

    # Assign role and mark key as redeemed
    try:
        await user.add_roles(role)
        await interaction.response.send_message(f"{user.mention} has been given the role {role.name} for {duration} minutes!")
        print(f"Assigned role '{role.name}' to user '{user.display_name}' for {duration} minutes using key '{key}'")
        
        # Mark the key as redeemed
        keys[key]["redeemed"] = True

        # Schedule role removal
        await remove_role_after_delay(user, role, duration)
    except Exception as e:
        await interaction.response.send_message("Failed to assign the role.", ephemeral=True)
        print(f"Error adding role: {e}")

# Sync commands to make sure they're available as slash commands
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f'Logged in as {bot.user}!')

# Start the bot
bot.run('YOUR DISCORD BOT TOKEN')
