import json
import os
import re

import discord
import requests

client = discord.Client()

TEMP_PATH = "./state_{}.temp.json"
INSTRUCTIONS = """USING THE BRYCE BOT
COMMANDS:
    !about - You know how to use this one already clearly
    BRYCE IT UP! - Turn everyone into a better version of themselves
    KILL THE LIGHTS - AND flip it back
"""


async def log_state(server, channel):
    """
    Logs the current nickname state of the server and uploads it to the default channel.
    :param channel:
    :param server: The discord server object
    :return: A state mapping or None if it was not safe to create a new state
    """
    state = {}
    for member in server.members:
        if member.top_role < server.me.top_role:
            state[member.id] = member.nick
    if os.path.isfile(TEMP_PATH.format(server.id)) or not state:
        return None
    with open(TEMP_PATH.format(server.id), "w+") as output:
        json.dump(state, output)
    with open(TEMP_PATH.format(server.id), "r") as output:
        await client.send_file(channel, output)
    print(state)
    return state


# def reset():


async def set_bryce_state(server):
    for member in server.members:
        if member.top_role < server.me.top_role:
            try:
                print("SET {} > {}".format(member.nick, "Bryce"))
                await client.change_nickname(member, "Bryce")
            except Exception:
                pass


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
    os.remove(TEMP_PATH.format(server.id))
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
        os.remove(TEMP_PATH.format(server.id))
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
    if command.endswith(' it up!'):
        await client.send_message(message.channel, 'ACK -> Executing subroutine \'Good Cop\'')
        state = await log_state(server, message.channel)
        if state is not None:
            for key in state:
                state[key] = message.content.strip()[:-7]
            await commit_state(state, server)
            await client.send_message(message.channel, 'Execution Complete')

        else:
            await client.send_message(message.channel, 'Execution failed; no targets found or state already exists')
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


try:
    client.run('NDc2NjYwNzc3MzU3NjcyNDU4.Dkw49Q.ScVynBxsAUugng1kib-pTSssjTY')
finally:
    print("Exiting")
    client.close()
