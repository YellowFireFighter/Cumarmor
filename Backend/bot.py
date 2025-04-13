import discord
from discord import app_commands
from discord.ext import commands
import datetime
import mysql.connector
import random
import string
import asyncio
import threading
import time
from datetime import datetime, timedelta
from datetime import timezone

def generate_random_string(length):
  characters = string.ascii_letters

  result = ''.join(random.choice(characters) for i in range(length))
  return result

conn = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  auth_plugin='mysql_native_password',
  pool_name = "sqlpool",
  pool_size = 3
)
c = conn.cursor(buffered=True)

c.execute("use main;")

# Create invites table if not exists
create_table_query = '''CREATE TABLE IF NOT EXISTS invites (
                        id VARCHAR(255) PRIMARY KEY,
                        hwid VARCHAR(255) NOT NULL,
                        ip VARCHAR(255) NOT NULL,
                        invite VARCHAR(255) NOT NULL,
                        hwidresets INT NOT NULL,
                        lastreset VARCHAR(255) NOT NULL,
                        oldhwid VARCHAR(255) NOT NULL,
                        oldip VARCHAR(255) NOT NULL,
                        executions INT NOT NULL,
                        version INT NOT NULL,
                        expiration_date DATETIME,
                        days INT
                    )'''
c.execute(create_table_query)
conn.commit()

def ping():
    while True:
        c.execute("SELECT 1")
        print("Pinged DB")
        time.sleep(3600)

query_thread = threading.Thread(target=ping, daemon=True)
query_thread.start()

bot = commands.Bot(command_prefix="!", intents = discord.Intents.all())

@bot.tree.command(name="ping", description="delay between bot and discord")
async def ping(interation: discord.Interaction):
    print(bot.latency)
    await interation.response.send_message('{0} delay'.format(bot.latency, 1), ephemeral=True)

@bot.tree.command(name="status", description="crumbleware services status")
async def status(interation: discord.Interaction):
    embed=discord.Embed(title="Crumbleware V6 Status", color=0x00FF00)
    embed.add_field(name="Alt Gen:",value=f':red_circle: Offline',inline=False)
    embed.add_field(name="Project Delta:",value=f':green_circle: Online',inline=False)
    embed.add_field(name="Fallen:",value=f':red_circle: Offline',inline=False)
    embed.add_field(name="Lone Survival:",value=f':red_circle: Offline',inline=False)

    await interation.response.send_message(embed=embed)

@bot.tree.error
async def on_test_error(interation: discord.Interaction, error: app_commands.AppCommandError):
    await interation.response.defer()
    if isinstance(error, app_commands.CommandOnCooldown):
        embed2=discord.Embed(title=f"Generater Cooldown", description=f"Please wait {round(error.retry_after)} seconds before generating another account", color=0xFF5733)
        await interation.followup.send(embed=embed2)
        return
    else:
        raise error
    
@bot.tree.command(name="mass-role-buyers", description="Assigns a role to all whitelisted users")
@app_commands.describe(role="Role to assign to whitelisted members")
async def assign_role_to_whitelisted(interaction: discord.Interaction, role: discord.Role):
    # Send an initial response to acknowledge the command
    embed = discord.Embed(title="Role Assignment Started", description="Processing...", color=0x00FF00)
    summary_message = await interaction.followup.send(embed=embed, ephemeral=True)

    admin_role = discord.utils.get(interaction.guild.roles, name="/")

    if admin_role not in interaction.user.roles:
        embed = discord.Embed(title="Invalid Permission", description="You must be an Admin or Moderator", color=0xFF5733)
        await summary_message.edit(embed=embed)
        return

    assigned_count = 0
    total_members = len(interaction.guild.members)  # To get the total number of members in the guild
    tasks = []

    for member in interaction.guild.members:
        # Skip bots
        if member.bot:
            continue

        # Check if the member is whitelisted in the database
        check_query = '''SELECT * FROM invites WHERE id = %s'''
        c.execute(check_query, (str(member.id),))
        result = c.fetchone()

        if result is not None:
            # Assign the role if the user is whitelisted and doesn't already have it
            if role not in member.roles:
                try:
                    await member.add_roles(role)
                    assigned_count += 1

                    # Update progress every time a role is assigned
                    embed = discord.Embed(
                        title="Role Assignment In Progress",
                        description=f"Assigned role to {assigned_count}/{total_members} whitelisted users...",
                        color=0x00FF00
                    )
                    await summary_message.edit(embed=embed)
                except discord.DiscordException as e:
                    print(f"Error assigning role to {member.name}: {e}")

    # Final summary after processing all whitelisted members
    embed.title = "Role Assignment Summary"
    embed.description = f"Finished! Successfully assigned the role to {assigned_count} whitelisted users."
    await summary_message.edit(embed=embed)

@bot.tree.command(name="mass-role", description="Assigns a role to all members in the server")
@app_commands.describe(role="Role to assign to all members")
async def assign_role_to_all(interaction: discord.Interaction, role: discord.Role):
    # Send an initial response to acknowledge the command
    embed = discord.Embed(title="Role Assignment Started", description="Processing...", color=0x00FF00)
    summary_message = await interaction.followup.send(embed=embed, ephemeral=True)

    admin_role = discord.utils.get(interaction.guild.roles, name="/")

    if admin_role not in interaction.user.roles:
        embed = discord.Embed(title="Invalid Permission", description="You must be an Admin or Moderator", color=0xFF5733)
        await summary_message.edit(embed=embed)
        return

    assigned_count = 0
    total_members = len(interaction.guild.members)
    tasks = []

    # Loop over all members in the guild
    for member in interaction.guild.members:
        # Skip bot accounts
        if member.bot:
            continue
        
        # Assign the role if the member doesn't already have it
        if role not in member.roles:
            try:
                await member.add_roles(role)
                assigned_count += 1

                # Create an updated embed with live progress
                embed = discord.Embed(
                    title="Role Assignment In Progress",
                    description=f"Assigned role to {assigned_count}/{total_members} members...",
                    color=0x00FF00
                )
                await summary_message.edit(embed=embed)
            except discord.DiscordException as e:
                print(f"Error assigning role to {member.name}: {e}")

    # Final message once all roles are assigned
    embed = discord.Embed(
        title="Role Assignment Completed",
        description=f"Successfully assigned the role to {assigned_count}/{total_members} members.",
        color=0x00FF00
    )
    await summary_message.edit(embed=embed)

@bot.tree.command(name="mass-whitelist", description="Whitelists all users with the specified role")
@app_commands.describe(role="Role to whitelist members for", days="Number of days before expiration")
async def mass_whitelist(interaction: discord.Interaction, role: discord.Role, days: int):
    await interaction.response.defer()
    expiration_date = datetime.now(timezone.utc) + timedelta(days=days)
    
    whitelisted_count = 0
    for member in interaction.guild.members:
        if role in member.roles:
            try:
                key = generate_random_string(50)
                insert_query = '''INSERT INTO invites (id, hwid, invite, ip, hwidresets, lastreset, oldhwid, oldip, executions, version, expiration_date) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''
                c.execute(insert_query, (str(member.id), "", key, "", 0, "", "", "", 0, 1, expiration_date))
                conn.commit()
                whitelisted_count += 1
            except Exception as e:
                print(f"Error whitelisting {member.name}: {e}")
    
    embed = discord.Embed(
        title="Mass Whitelist Complete",
        description=f"Successfully whitelisted **{whitelisted_count}** users for **{days} days**.",
        color=0x00FF00
    )
    
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="whitelist", description="Whitelists a user")
@app_commands.describe(member="member", version="public or private", days="Number of days before expiration")
async def whitelist(interaction: discord.Interaction, member: discord.Member, version: str, days: int):
    await interaction.response.defer()

    # Check if member is None
    if not member:
        embed2 = discord.Embed(
            title="Error",
            description="The specified member is invalid.",
            color=0xFF5733
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)
        return
    
    if days > 9999:
        days = 9999

    # Role definitions
    role = discord.utils.get(interaction.guild.roles, name="/")  # Admin/Moderator role
    role2 = discord.utils.get(interaction.guild.roles, name="Buyer")  # Whitelist role

    # Validate permission
    if not role or role not in interaction.user.roles:
        embed2 = discord.Embed(
            title="Invalid Permission",
            description="You must be an Admin to whitelist users.",
            color=0xFF5733
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)
        return

    # Convert version input to database-compatible format
    version_map = {"public": 1, "private": 2}
    version = version.lower()

    if version not in version_map:
        embed2 = discord.Embed(
            title="Invalid Version",
            description="Version must be either public or private.",
            color=0xFF5733
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)
        return

    db_version = version_map[version]

    # Generate a random key for whitelisting
    key = generate_random_string(50)
    expiration_date = datetime.now(timezone.utc) + timedelta(days=days)
    insert_query = '''
        INSERT INTO invites (id, hwid, invite, ip, hwidresets, lastreset, oldhwid, oldip, executions, version, expiration_date) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    '''
    try:
        c.execute(insert_query, (str(member.id), "", key, "", 0, "", "", "", 0, db_version, expiration_date))
        conn.commit()

        # Assign the whitelist role
        await member.add_roles(role2)

        # Confirmation embeds
        embed_admin = discord.Embed(
            title=f"Whitelisted {member}",
            description=f"Successfully whitelisted user with **{version}** version.",
            color=0x00FF00
        )
        embed_user = discord.Embed(
            title="Whitelisted to Chronos.rip (Crumbleware V6)",
            description="You have been successfully whitelisted!",
            color=0x00FF00
        )
        embed_user.add_field(name="Key:", value=f'{key}', inline=True)
        embed_user.add_field(name="Version:", value=f'**{version.capitalize()}**', inline=True)

        # Send embeds
        await member.send(embed=embed_user)
        await interaction.followup.send(embed=embed_admin, ephemeral=True)
    except Exception as e:
        embed_error = discord.Embed(
            title="Error",
            description=f"An error occurred during whitelisting:\n{e}",
            color=0xFF0000
        )
        await interaction.followup.send(embed=embed_error, ephemeral=True)

@bot.tree.command(name="genkeys", description="Generates new keys")
@app_commands.describe(amount="Number of keys to generate")
@app_commands.describe(version="public or private")
@app_commands.describe(days="Number of days before expiration")
async def gen_keys(interaction: discord.Interaction, amount: int, version: str, days: int):
    await interaction.response.defer()
    role = discord.utils.get(interaction.guild.roles, name="/")  # Adjust role name as needed

    if role not in interaction.user.roles:
        embed2 = discord.Embed(
            title="Invalid Permission",
            description="You must have the specified role to generate keys.",
            color=0xFF5733
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)
        return

    version_map = {"public": 1, "private": 2}
    version = version.lower()

    if version not in version_map:
        embed2 = discord.Embed(
            title="Invalid Version",
            description="Version must be either public or private.",
            color=0xFF5733
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)
        return

    db_version = version_map[version]
    keys = []

    for _ in range(amount):
        key = generate_random_string(50)
        keys.append(key)

        insert_query = '''
            INSERT INTO invites (id, hwid, ip, invite, hwidresets, lastreset, oldhwid, oldip, executions, version, expiration_date, days) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL, %s)
        '''
        try:
            c.execute(insert_query, (key, "", "", key, 0, "", "", "", 0, db_version, days))
        except Exception as e:
            embed_error = discord.Embed(
                title="Database Error",
                description=f"An error occurred while inserting keys into the database:\n{e}",
                color=0xFF0000
            )
            await interaction.followup.send(embed=embed_error, ephemeral=True)
            return

    conn.commit()

    embed = discord.Embed(
        title="Generated Keys",
        description=f"You have generated the following keys for the **{version.capitalize()}** version with an expiration of {days} days:",
        color=0x00FF00
    )
    embed.add_field(name="Keys:", value="\n".join(keys), inline=False)

    try:
        await interaction.user.send(embed=embed)
        embed_confirmation = discord.Embed(
            title="Success",
            description="The keys have been sent to your DMs.",
            color=0x00FF00
        )
        await interaction.followup.send(embed=embed_confirmation, ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send(
            "I couldn't send you a DM. Please check your privacy settings and try again.",
            ephemeral=True
        )

@bot.tree.command(name="comp-all", description="Adds days to all keys")
@app_commands.describe(days="Number of days to add to all keys")
async def comp_all(interaction: discord.Interaction, days: int):
    await interaction.response.defer()
    role = discord.utils.get(interaction.guild.roles, name="/")  # Adjust role name as needed

    if role not in interaction.user.roles:
        embed2 = discord.Embed(
            title="Invalid Permission",
            description="You must have the specified role to generate keys.",
            color=0xFF5733
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)
        return

    update_query = '''UPDATE invites SET expiration_date = expiration_date + INTERVAL %s DAY'''
    c.execute(update_query, (days,))
    conn.commit()
    
    # Create an embed to notify the user
    embed = discord.Embed(
        title="Keys Extended",
        description=f"All keys have been successfully extended by {days} days.",
        color=0x00FF00
    )
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="comp-key", description="Adds days to a specific key")
@app_commands.describe(key="Key to extend", days="Number of days to add")
async def comp_key(interaction: discord.Interaction, key: str, days: int):
    await interaction.response.defer()
    role = discord.utils.get(interaction.guild.roles, name="/")  # Adjust role name as needed

    if role not in interaction.user.roles:
        embed2 = discord.Embed(
            title="Invalid Permission",
            description="You must have the specified role to generate keys.",
            color=0xFF5733
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)
        return

    update_query = '''UPDATE invites SET expiration_date = expiration_date + INTERVAL %s DAY WHERE invite = %s'''
    c.execute(update_query, (days, key))
    conn.commit()
    
    embed = discord.Embed(
        title="Key Extended",
        description=f"The expiration date has been successfully extended by {days} days.",
        color=0x00FF00
    )
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="comp-user", description="Adds days to a specific user's key")
@app_commands.describe(member="User to extend the key for", days="Number of days to add")
async def comp_user(interaction: discord.Interaction, member: discord.Member, days: int):
    await interaction.response.defer()
    
    # Check if the user has a key
    select_query = '''SELECT invite FROM invites WHERE id = %s'''
    c.execute(select_query, (str(member.id),))
    key = c.fetchone()
    
    if not key:
        embed = discord.Embed(
            title="Error",
            description=f"{member.mention} does not have a registered key.",
            color=0xFF0000
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    # Extend expiration date for the user's key
    update_query = '''UPDATE invites SET expiration_date = expiration_date + INTERVAL %s DAY WHERE id = %s'''
    c.execute(update_query, (days, str(member.id)))
    conn.commit()

    embed = discord.Embed(
        title="Key Extended",
        description=f"{member.mention}'s key has been successfully extended by {days} days.",
        color=0x00FF00
    )
    await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="unwhitelist", description="unwhitelists a user")
async def unwhitelist(interation: discord.Interaction, member: discord.Member):
    await interation.response.defer()
    role = discord.utils.get(interation.guild.roles, name="/")
    role2 = discord.utils.get(interation.guild.roles, name="Buyer")

    if not role in interation.user.roles:
        embed2=discord.Embed(title=f"Invalid Permission ", description=f"You must be a Admin or Moderator", color=0xFF5733)
        await interation.followup.send(embed=embed2, ephemeral=True)
        return
    
    if not role2 in member.roles:
        embed2=discord.Embed(title=f"User is not Whitelisted", description=f"User is not Whitelisted", color=0xFF5733)
        await interation.followup.send(embed=embed2, ephemeral=True)
        return
    
    insert_query = '''DELETE FROM invites WHERE id = %s'''
    c.execute(insert_query, (str(member.id),))
    conn.commit()

    await member.remove_roles(role2)

    embed2=discord.Embed(title=f"UnWhitelisted {member}", description=f"Succesfully UnWhitelisted User", color=0x00FF00)
    embed=discord.Embed(title=f"Blacklisted from Chronos.rip (Crumbleware V6)", description=f"You Have Been Blacklisted", color=0x00FF00)
    await member.send(embed=embed)
    await interation.followup.send(embed=embed2, ephemeral=True)
    return

@bot.tree.command(name="versionchanger", description="Changes a user's version")
@app_commands.describe(member="member")
@app_commands.describe(version="public or private")
async def version(interaction: discord.Interaction, member: discord.Member, version: str):
    await interaction.response.defer()
    
    # Role definitions
    role = discord.utils.get(interaction.guild.roles, name="/")  # Admin/Moderator role
    role2 = discord.utils.get(interaction.guild.roles, name="Buyer")  # Whitelist role

    if not role or role not in interaction.user.roles:
        embed2 = discord.Embed(
            title="Invalid Permission",
            description="You must be an Admin or Moderator.",
            color=0xFF5733
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)
        return

    # Check if the user is whitelisted
    if not role2 in member.roles:
        embed2 = discord.Embed(
            title="User Not Whitelisted",
            description="User must be whitelisted first before changing versions.",
            color=0xFF5733
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)
        return

    # Convert version input to 1 (public) or 2 (private)
    version_map = {"public": 1, "private": 2}
    version = version.lower()

    if version not in version_map:
        embed2 = discord.Embed(
            title="Invalid Version",
            description="Version must be either `public` or `private`.",
            color=0xFF5733
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)
        return

    db_version = version_map[version]

    try:
        # Update the version column for the specific user
        update_query = '''UPDATE invites SET version = %s WHERE id = %s'''
        c.execute(update_query, (db_version, str(member.id)))
        conn.commit()

        # Success Embed for the Admin
        embed2 = discord.Embed(
            title="Version Changed",
            description=f"Successfully changed **{member.display_name}**'s version to **{version.capitalize()}**.",
            color=0x00FF00
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)

        # Notify the User
        embed = discord.Embed(
            title="Version Updated",
            description=f"Your version has been updated to **{version.capitalize()}**.",
            color=0x00FF00
        )
        await member.send(embed=embed)
    
    except Exception as e:
        # Handle errors gracefully
        embed2 = discord.Embed(
            title="Error",
            description=f"An error occurred while changing the version.\n```{e}```",
            color=0xFF0000
        )
        await interaction.followup.send(embed=embed2, ephemeral=True)

@bot.tree.command(name="resethwid", description="Resets your HWID")
async def resethwid(interaction: discord.Interaction):
    await interaction.response.defer()
    role = discord.utils.get(interaction.guild.roles, name="Buyer")

    if role not in interaction.user.roles:
        embed = discord.Embed(title="Invalid Permission", description="You must be a Buyer", color=0xFF5733)
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(title="hwid resets are disabled", description="uh oh that sucks", color=0xFF5733)
    await interaction.followup.send(embed=embed, ephemeral=True)
    return

    user_id = str(interaction.user.id)

    # Check lastreset value
    select_query = '''SELECT lastreset FROM invites WHERE id = %s'''
    c.execute(select_query, (user_id,))
    lastreset = c.fetchone()

    current_time = datetime.now()

    if lastreset is None or lastreset[0] is None or lastreset[0] == '':
        # If lastreset is blank, set it to the current date
        update_query = '''UPDATE invites SET lastreset = %s WHERE id = %s'''
        c.execute(update_query, (current_time, user_id))
        conn.commit()

        # Reset HWID to a blank string
        reset_hwid_query = '''UPDATE invites SET hwid = '' WHERE id = %s'''
        c.execute(reset_hwid_query, (user_id,))
        conn.commit()

        # Add hwid reset value
        increment_query = '''UPDATE invites SET hwidresets = hwidresets + 1 WHERE id = %s'''
        c.execute(increment_query, (user_id,))
        conn.commit()

        embed = discord.Embed(title="HWID Reset", description="Your HWID has been successfully reset.", color=0x00FF00)
        await interaction.followup.send(embed=embed, ephemeral=True)

    else:
        # If there is a lastreset date, check if it's been 7 days
        lastreset_date_str = lastreset[0]

        if lastreset_date_str:  # Ensure it's not an empty string
            lastreset_date = datetime.fromisoformat(lastreset_date_str)
            if current_time - lastreset_date >= timedelta(days=7):
                # Reset HWID
                update_query = '''UPDATE invites SET hwid = '', lastreset = %s WHERE id = %s'''
                c.execute(update_query, (current_time, user_id))
                conn.commit()

                # Add hwid reset value
                increment_query = '''UPDATE invites SET hwidresets = hwidresets + 1 WHERE id = %s'''
                c.execute(increment_query, (user_id,))
                conn.commit()

                embed = discord.Embed(title="HWID Reset", description="Your HWID has been successfully reset.", color=0x00FF00)
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                # Not enough time has passed
                time_remaining = (lastreset_date + timedelta(days=7)) - current_time
                embed = discord.Embed(title="HWID Reset Denied", description=f"You can reset your HWID in {time_remaining.days} days and {time_remaining.seconds // 3600} hours.", color=0xFF5733)
                await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            # Handle unexpected empty string case
            embed = discord.Embed(title="Error", description="An unexpected error occurred. Please contact support.", color=0xFF5733)
            await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="get-script", description="Sends the script and your key")
async def script_command(interaction: discord.Interaction):
    #try:
        await interaction.response.defer()
        role = discord.utils.get(interaction.guild.roles, name="Buyer")

        if role not in interaction.user.roles:
            embed = discord.Embed(title="Invalid Permission", description="You must be a Buyer", color=0xFF5733)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        # Retrieve the user's key from the database
        check_query = '''SELECT invite FROM invites WHERE id = %s'''
        c.execute(check_query, (str(interaction.user.id),))
        result = c.fetchone()

        if result is None:
            embed = discord.Embed(title="No Key Found", description="You do not have a key associated with your account.", color=0xFF5733)
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        user_key = result[0]

        # Prepare the script
        script_code = f'script_key = "{user_key}"\n' + 'loadstring(request({Url = "https://chronos.rip/static/loader.lua", Method = "Get"}).Body)()'
        #script_code2 = f'script_key = "{user_key}"\nloadstring(game:HttpGet("https://raw.githubusercontent.com/YellowFireFighter/V6/refs/heads/main/Loader"))()'
        #script_code = "script is down sorry idiot"

        # Create an embed for the script
        script_embed = discord.Embed(title="Chronos.rip (Crumbleware V6) Script", color=0x00FF00)
        script_embed.add_field(name="V6:", value=f"```lua\n{script_code}\n```", inline=False)
        #script_embed.add_field(name="V5:", value=f"```lua\n{script_code2}\n```", inline=False)

        # Send the embed in a DM
        try:
            await interaction.user.send(embed=script_embed)
            embed = discord.Embed(title="Sent Script", description="The script has been sent to your DMs.", color=0x00FF00)
            await interaction.followup.send(embed=embed, ephemeral=True)
        except discord.Forbidden:
            embed = discord.Embed(title="DMs Closed", description="I cannot send you a DM. Please open your DMs and try again.", color=0xFF5733)
            await interaction.followup.send(embed=embed, ephemeral=True)
    #except:
     #   print("not again bruh")

@bot.tree.command(name="force-resethwid", description="force resets a users HWID")
@app_commands.describe(member="The member whose HWID will be reset")
async def force_resethwid(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.defer()
    admin_role = discord.utils.get(interaction.guild.roles, name="/")
    role = discord.utils.get(interaction.guild.roles, name="Buyer")

    if admin_role not in interaction.user.roles:
        embed = discord.Embed(title="Invalid Permission", description="You must be an Admin or Moderator", color=0xFF5733)
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    if role not in member.roles:
        embed = discord.Embed(title="Invalid Permission", description="The user must be a Buyer", color=0xFF5733)
        await interaction.followup.send(embed=embed, ephemeral=True)
        return
    
    current_time = datetime.now()

    # If lastreset is blank, set it to the current date
    update_query = '''UPDATE invites SET lastreset = %s WHERE id = %s'''
    c.execute(update_query, (current_time, str(member.id),))
    conn.commit()

    # set old hwid
    update_query = '''UPDATE invites SET oldhwid = hwid WHERE id = %s'''
    c.execute(update_query, (str(member.id),))
    conn.commit()

    # reset HWID to a blank string
    update_query = '''UPDATE invites SET hwid = '' WHERE id = %s'''
    c.execute(update_query, (str(member.id),))
    conn.commit()

    # add hwid reset value
    update_query = '''UPDATE invites SET hwidresets = hwidresets + 1 WHERE id = %s'''
    c.execute(update_query, (str(member.id),))
    conn.commit()

    # Feedback to the command invoker
    embed_invoker = discord.Embed(title="HWID Reset", description=f"Successfully reset HWID for {member.mention}.", color=0x00FF00)
    await interaction.followup.send(embed=embed_invoker, ephemeral=True)

    # Optionally, inform the user whose HWID was reset
    embed_member = discord.Embed(title="HWID Reset", description="Your HWID has been reset by an Admin.", color=0x00FF00)
    await member.send(embed=embed_member)

@bot.tree.command(name="stats", description="Displays your current stats")
async def stats(interaction: discord.Interaction):
    # Fetch the user's Discord ID
    user_id = str(interaction.user.id)

    # Fetch user stats from the database
    select_query = '''SELECT * FROM invites WHERE id = %s'''
    c.execute(select_query, (user_id,))
    user_stats = c.fetchone()

    # Check if user stats were found
    if user_stats is None:
        embed = discord.Embed(
            title="Stats Not Found",
            description="No stats found for your account.",
            color=0xFF5733
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Unpack the stats
    id, hwid, ip, invite, hwidresets, lastreset, oldhwid, oldip, executions, version, expiration_date, days = user_stats

    # Convert version to readable format
    version_readable = "Public" if version == 1 else "Private" if version == 2 else "Unknown"

    # Calculate remaining days
    if expiration_date:
        remaining_days = (expiration_date - datetime.now()).days
        remaining_days_text = f"{remaining_days} days left"
    else:
        remaining_days_text = "N/A"

    # Create an embed with the user's stats
    embed = discord.Embed(title="Chronos.rip Stats", color=0x00FF00)
    embed.add_field(name="Executions", value=executions or 0, inline=False)
    embed.add_field(name="Key", value=invite or "N/A", inline=False)
    embed.add_field(name="HWID", value=hwid or "N/A", inline=False)
    embed.add_field(name="HWID Resets", value=hwidresets or 0, inline=False)
    embed.add_field(name="Last Reset", value=lastreset or "N/A", inline=False)
    embed.add_field(name="Old HWID", value=oldhwid or "N/A", inline=False)
    embed.add_field(name="Version", value=version_readable, inline=False)
    embed.add_field(name="Expiration Date", value=remaining_days_text, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="force-stats", description="Displays another user's stats")
@app_commands.describe(member="The member whose stats you want to view")
async def force_stats(interaction: discord.Interaction, member: discord.Member):
    # Define the admin role that can access other users' stats
    required_role = discord.utils.get(interaction.guild.roles, name="/")
    
    # Check for permissions
    if required_role not in interaction.user.roles:
        embed = discord.Embed(
            title="Permission Denied",
            description="You do not have permission to view other users' stats.",
            color=0xFF5733
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Fetch the target user's Discord ID
    user_id = str(member.id)

    # Fetch user stats from the database
    select_query = '''SELECT * FROM invites WHERE id = %s'''
    c.execute(select_query, (user_id,))
    user_stats = c.fetchone()

    # Check if user stats were found
    if user_stats is None:
        embed = discord.Embed(
            title="Stats Not Found",
            description="No stats found for this account.",
            color=0xFF5733
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Unpack the stats
    id, hwid, ip, invite, hwidresets, lastreset, oldhwid, oldip, executions, version, expiration_date, days = user_stats

    # Convert version to readable format
    version_readable = "Public" if version == 1 else "Private" if version == 2 else "Unknown"

    # Calculate remaining days
    if expiration_date:
        remaining_days = (expiration_date - datetime.now()).days
        remaining_days_text = f"{remaining_days} days left"
    else:
        remaining_days_text = "N/A"

    # Create an embed with the user's stats
    embed = discord.Embed(title=f"{member.display_name}'s Stats", color=0x00FF00)
    embed.add_field(name="Executions", value=executions or 0, inline=False)
    embed.add_field(name="Key", value=invite or "N/A", inline=False)
    embed.add_field(name="HWID", value=hwid or "N/A", inline=False)
    embed.add_field(name="HWID Resets", value=hwidresets or 0, inline=False)
    embed.add_field(name="Last Reset", value=lastreset or "N/A", inline=False)
    embed.add_field(name="Old HWID", value=oldhwid or "N/A", inline=False)
    embed.add_field(name="Version", value=version_readable, inline=False)
    embed.add_field(name="Expiration Date", value=remaining_days_text, inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="top_users", description="Displays the top 10 users with the most executions")
async def top_stats(interaction: discord.Interaction):
    """Displays the top 10 users with the most executions in an embed."""
    
    # Fetch the top 10 users directly
    top_query = '''
    SELECT id, executions 
    FROM invites 
    ORDER BY executions DESC 
    LIMIT 10
    '''
    c.execute(top_query)
    top_users = c.fetchall()

    if not top_users:
        embed = discord.Embed(
            title="No Stats Found",
            description="No execution data available.",
            color=0xFF5733
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Create the embed
    embed = discord.Embed(title="Top 10 Users by Executions", color=0x00FF00)

    for rank, (user_id, executions) in enumerate(top_users, start=1):
        user = await bot.fetch_user(int(user_id))  # Fetch the Discord user object
        username = user.name if user else f"Unknown ({user_id})"
        embed.add_field(
            name=f"#{rank} {username}",
            value=f"Executions: {executions}",
            inline=False
        )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="keyfinder", description="Finds a user from there key")
async def stats(interaction: discord.Interaction, key: str):
    # Define the admin role that can access other users' stats
    required_role = discord.utils.get(interaction.guild.roles, name="/")

    # If the user tries to access another member's stats
    if required_role not in interaction.user.roles:
        embed = discord.Embed(title="Permission Denied", description="You do not have permission to view other users' stats.", color=0xFF5733)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Fetch user stats from the database
    select_query = '''SELECT * FROM invites WHERE invite = %s'''
    c.execute(select_query, (key,))
    user_stats = c.fetchone()

    # Check if user stats were found
    if user_stats is None:
        embed = discord.Embed(title="User Not Found", description="No user found for this key.", color=0xFF5733)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    # Unpack the stats
    id, hwid, ip, invite, hwidresets, lastreset, oldhwid, oldip, executions = user_stats

    # Create an embed with the user's stats
    embed = discord.Embed(title=f"User Found: <@{id}>", color=0x00FF00)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="cleankeys", description="Deletes unused keys")
async def clean_keys(interaction: discord.Interaction):
    # Define the admin role that can access this command
    required_role = discord.utils.get(interaction.guild.roles, name="/")

    # Check if the user has the required role
    if required_role not in interaction.user.roles:
        embed = discord.Embed(
            title="Permission Denied",
            description="You do not have permission to use this command.",
            color=0xFF5733
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    try:
        # Execute the DELETE query and count the number of affected rows
        delete_query = '''DELETE FROM invites WHERE invite = id'''
        c.execute(delete_query)
        rows_deleted = c.rowcount  # Get the number of rows affected

        # Commit the changes to the database
        conn.commit()

        # Send a success message with the count of deleted keys
        embed = discord.Embed(
            title="Keys Cleaned",
            description=f"Successfully deleted {rows_deleted} unused keys.",
            color=0x00FF00
        )
        await interaction.response.send_message(embed=embed)

        # Log the result to the console
        print(f"{rows_deleted} keys deleted where invite = id.")

    except Exception as e:
        # Handle any errors and rollback changes if needed
        conn.rollback()
        embed = discord.Embed(
            title="Error",
            description=f"An error occurred while deleting keys: {str(e)}",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Log the error to the console
        print(f"Error deleting keys: {str(e)}")

@bot.tree.command(name="redeem", description="Redeem a key to receive the buyer role")
@app_commands.describe(key="The key to redeem")
async def redeem_key(interaction: discord.Interaction, key: str):
    await interaction.response.defer()

    select_query = '''SELECT id, expiration_date, days FROM invites WHERE invite = %s'''
    c.execute(select_query, (key,))
    result = c.fetchone()

    if result is None:
        embed = discord.Embed(title="Invalid Key", description="The provided key does not exist or is invalid.", color=0xFF5733)
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

    assigned_id, expiration_date, days = result

    if assigned_id != key:
        embed = discord.Embed(title="Key Already Redeemed", description="This key has already been redeemed.", color=0xFF5733)
        await interaction.followup.send(embed=embed, ephemeral=True)
        return

    # Calculate expiration date upon redemption
    expiration_date = datetime.now(timezone.utc) + timedelta(days=days)

    try:
        update_query = '''UPDATE invites SET id = %s, expiration_date = %s WHERE invite = %s'''
        c.execute(update_query, (str(interaction.user.id), expiration_date, key))
        
        conn.commit()

        role = discord.utils.get(interaction.guild.roles, name="Buyer")  # Adjust role name as needed
        if role:
            await interaction.user.add_roles(role)

        embed = discord.Embed(title="Key Redeemed", description=f"Your key has been successfully redeemed! It will expire on {expiration_date.strftime('%Y-%m-%d %H:%M:%S UTC')}.", color=0x00FF00)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except:
        embed = discord.Embed(title="Invalid User", description="The provided user ID is already associated with a key.", color=0xFF5733)
        await interaction.followup.send(embed=embed, ephemeral=True)

@bot.tree.command(name="username", description="changes bots username")
async def change_username(interaction, new_username: str):
    await interaction.response.defer()

    role = discord.utils.get(interaction.guild.roles, name="/")  # Adjust role name as needed

    # Check if user has the required role
    if role not in interaction.user.roles:
        embed2 = discord.Embed(title="Invalid Permission", description="You must have the specified role to generate keys.", color=0xFF5733)
        await interaction.followup.send(embed=embed2, ephemeral=True)
        return
    
    try:
        # Change the bot's username
        await bot.user.edit(username=new_username)
        embed = discord.Embed(title="Username Changed", description="Bots username has succesfully changed.", color=0x00FF00)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except discord.HTTPException as e:
        embed2 = discord.Embed(title="Failed to change username", description=f"Bots username could not be changed: {str(e)}.", color=0xFF5733)
        await interaction.followup.send(embed=embed2, ephemeral=True)

# Function to remove expired keys and roles
async def remove_expired_keys(bot):
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.now(timezone.utc)
        c.execute("SELECT id FROM invites WHERE expiration_date <= %s", (now,))
        expired_keys = c.fetchall()
        guild = bot.guilds[0]  # Adjust based on your bot setup
        for key in expired_keys:
            member = guild.get_member(int(key[0]))
            if member:
                role = discord.utils.get(guild.roles, name="Buyer")
                await member.remove_roles(role)
            print(f"Removing: {key[0]}")
            c.execute("DELETE FROM invites WHERE id = %s", (key[0],))
        conn.commit()
        await asyncio.sleep(60) 
        
@bot.event
async def on_ready():
    print("Loading...")
    bot.loop.create_task(remove_expired_keys(bot))
    try: 
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as err:
        print(err)
    print("Loaded!")

bot.run("Bot_Token")
