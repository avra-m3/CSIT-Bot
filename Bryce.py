import os

import discord

from commands import *

client = discord.Client()


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------\n\n')

    print("%-30s%-20s" % ("Connected Server", "Permission Status"))
    print("-" * 50)
    for guild in client.guilds:  # type: discord.Guild
        try:
            permissions = guild.me.guild_permissions  # type: discord.Permissions
            if not (permissions.manage_nicknames and permissions.manage_roles and
                    permissions.attach_files and permissions.send_messages and permissions.read_messages):
                if guild.system_channel:
                    await guild.system_channel.send(
                        "Warning: This server does not have the correct permissions set to run this bot!")
                print("%-30s%-20s" % (guild, "Bad"))
            else:
                print("%-30s%-20s" % (guild, "Good"))
        except discord.errors.DiscordException:
            print("%-30s%-20s" % (guild, "Errored"))


@client.event
async def on_member_join(member: discord.Member):
    welcome_user(member)


@client.event
async def on_message(message: Message):
    command = message.content.lower().strip()
    # if command == "!update":
    # await update(message)
    if command.startswith("!about") or command.startswith("!help"):
        await about(message)
    elif command.endswith(' it up!'):
        await set_all(message, client)
    elif command.startswith("!restore"):
        await restore(message, client)
    else:
        await mention(message, client)


try:
    client.run(os.getenv('AUTH'))
finally:
    print("Exiting")
    client.close()
