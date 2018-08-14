import re

from helpers import log_access, log_access_admin, log_state, reset_state_from_local, reset_state_from_remote, \
    commit_state, prevent_self_calls

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


@prevent_self_calls
@log_access("about")
async def about(message, client):
    await client.send_message(message.server, INSTRUCTIONS)


@prevent_self_calls
@log_access_admin("set_all")
async def set_all(message, client):
    server = message.server
    await client.send_message(message.channel, 'ACK -> Executing subroutine \'Good Cop\'')
    new_nick = message.clean_content.strip()[:-7]
    if len(new_nick) < 32:
        state, file_name = await log_state(server)
        with open(file_name, "r") as output:
            await client.send_file(message.channel, output)
        if state is not None:
            for key in state:
                state[key] = new_nick
            await commit_state(state, server, client)
            await client.send_message(message.channel, 'Execution Complete')

        else:
            await client.send_message(message.channel,
                                      'Execution failed; no targets found or state already exists')
    else:
        await client.send_message(message.channel,
                                  'Cannot change everyone\'s nickname to {} as len > 32'.format(new_nick))


@prevent_self_calls
@log_access_admin("restore")
async def restore(message, client):
    command = message.content.lower().strip()
    server = message.server
    if command == "!restore":
        await client.send_message(message.channel, 'ACK -> Executing subroutine \'Bad Cop\'')
        if not await reset_state_from_local(server, client):
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
            if not await reset_state_from_remote(server, command_end, client):
                await client.send_message(message.channel, "OP failed; Bad file")
        elif message.attachments:
            for attachment in message.attachments:
                await client.send_message(message.channel,
                                          "ACK -> Attempting restore from attachment at {}".format(
                                              attachment.url))
                if not await reset_state_from_remote(server, attachment, client):
                    await client.send_message(message.channel, "OP failed; Bad file")
        else:
            await client.send_message(message.channel, "OP failed; Bad file")


@prevent_self_calls
async def mention(message, client):
    command = message.content.lower().strip()
    server = message.server
    if "bryce" in command:
        if message.author != server.me:
            await client.send_message(message.channel, "I love Bryce, don't you?")
            await client.add_reaction(message, "❤")
    if "token" in command or "auth" in command:
        if message.author != server.me:
            await client.send_message(message.channel, "Hide your tokens kiddos!")
            await client.add_reaction(message, "🐱")
            await client.add_reaction(message, "💻")
