import json
import os
import re
import time

import discord
import requests

client = discord.Client()

TEMP_PATH = "./state_{}.temp.json"
INSTRUCTIONS = """USING THE BRYCE BOT
COMMANDS:
    !about - You know how to use this one already clearly
    Requires the user be an administrator
        <insert text> it up! - change the name of all members to <insert text>
        !restore <args> - restore usernames
            default behaviour: restores from an internal state if one exists.
            from <url>: fetches the file from url and attempts to restore state from said file.
            from <attachment>: fetches the attachment and attempts to restore state from said file.
    Mention 'bryce' to check if the bot is online
"""


async def log_state(server, channel):
    """
    Logs the current nickname state of the server and uploads it to the default channel.
    :param channel:
    :param server: The discord server object
    :return: A state mapping or None if it was not safe to create a new state
    """
    if os.path.isfile(TEMP_PATH.format(server.id)):
        with open(TEMP_PATH.format(server.id), "r") as state_in:
            state = json.load(state_in)
    else:
        state = {}
    for member in server.members:
        if member.id not in state:
            if member.top_role < server.me.top_role:
                state[member.id] = member.nick
    if not state:
        return None
    with open(TEMP_PATH.format(server.id), "w+") as output:
        json.dump(state, output)
    with open(TEMP_PATH.format(server.id), "r") as output:
        await client.send_file(channel, output)
    return state


def archive(file_path):
    now = time.strftime("%y%m%d-%H%M%S")
    archive_path = "{p}_{time}.archive".format(p=file_path, time=now)
    os.rename(file_path, archive_path)


async def reset_state_from_local(server):
    """
    Consumes the state file and uses it to reset all server nicknames
    :param server: The discord server object
    :return: Whether the operation was a success
    """
    if not os.path.exists(TEMP_PATH.format(server.id)):
        return False
    state = {}
    with open(TEMP_PATH.format(server.id), "r") as state_in:
        state = json.load(state_in)

    await commit_state(state, server)
    archive(TEMP_PATH.format(server.id))
    return True


async def reset_state_from_remote(server, url):
    """
    Consumes a remote json attachment and uses it to reset all server nicknames
    :param attachment: A discord attachment object
    :param server: The discord server object
    :return: Whether the operation was a success
    """
    request = requests.get(url)
    try:
        state = json.loads(request.content)
    except Exception:
        return False
    await commit_state(state, server)
    if os.path.exists(TEMP_PATH.format(server.id)):
        archive(TEMP_PATH.format(server.id))
    return True


async def commit_state(state, server):
    for user_id in state:
        try:
            member = server.get_member(user_id)
            print("SET: {}({}) > {}".format(member.nick or str(member), user_id, state[user_id]))
            if member.top_role <= server.me.top_role:
                if member.nick == state[user_id]:
                    continue
                await client.change_nickname(member, state[user_id])
        except Exception:
            pass


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------\n\n')

    print("%-30s%-20s" % ("Connected Server", "Permission Status"))
    print("-" * 50)
    for server in client.servers:
        permissions = server.me.server_permissions
        if not (permissions.manage_nicknames and permissions.manage_roles and
                permissions.attach_files and permissions.send_messages and permissions.read_messages):
            await client.send_message(server,
                                      "Warning: This server does not have the correct permissions set to run this bot!")
            print("%-30s%-20s" % (server, "Bad"))
        else:
            print("%-30s%-20s" % (server, "Good"))



@client.event
async def on_message(message):
    server = message.server
    command = message.content.lower().strip()
    if command.startswith("!about"):
        await client.send_message(message.channel, INSTRUCTIONS)
    if message.author.server_permissions.administrator:
        if command.endswith(' it up!'):
            await client.send_message(message.channel, 'ACK -> Executing subroutine \'Good Cop\'')
            new_nick = message.clean_content.strip()[:-7]
            if len(new_nick) < 32:
                state = await log_state(server, message.channel)
                if state is not None:
                    for key in state:
                        state[key] = new_nick
                    await commit_state(state, server)
                    await client.send_message(message.channel, 'Execution Complete')

                else:
                    await client.send_message(message.channel, 'Execution failed; no targets found or state already exists')
            else:
                await client.send_message(message.channel,
                                          'Cannot change everyone\'s nickname to {} as len > 32'.format(new_nick))

        if command.startswith("!restore"):
            if command == "!restore":
                await client.send_message(message.channel, 'ACK -> Executing subroutine \'Bad Cop\'')
                if not await reset_state_from_local(server):
                    await client.send_message(message.channel, 'State reset failed; Reason, no current state available')

            if command.startswith("!restore from"):
                command_end = message.content.strip("!restore from").strip()
                regex = re.compile(
                    r'^(?:http|ftp)s?://'  # http:// or https://
                    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                    r'localhost|'  # localhost...
                    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                    r'(?::\d+)?'  # optional port
                    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
                if re.match(regex, command_end):
                    await client.send_message(message.channel, "ACK -> Attempting restore from {}".format(command_end))
                    if not await reset_state_from_remote(server, command_end):
                        await client.send_message(message.channel, "OP failed; Bad file")
                elif message.attachments:
                    for attachment in message.attachments:
                        await client.send_message(message.channel,
                                                  "ACK -> Attempting restore from attachment at {}".format(attachment.url))
                        if not await reset_state_from_remote(server, attachment):
                            await client.send_message(message.channel, "OP failed; Bad file")
                else:
                    await client.send_message(message.channel, "OP failed; Bad file")
    if "bryce" in command:
        if message.author != server.me:
            await client.send_message(message.channel, "I love Bryce, don't you?")
            await client.add_reaction(message, "❤")
    if "token" in command or "auth" in command:
        if message.author != server.me:
            await client.send_message(message.channel, "Hide your tokens kiddos!")
            await client.add_reaction(message, "🐱")
            await client.add_reaction(message, "💻")

try:
    client.run(os.getenv('AUTH'))
finally:
    print("Exiting")
    client.close()
