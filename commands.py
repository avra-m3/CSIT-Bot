import re

from Chat import Commands
from Chat.Classes import ChatCommand
from helpers import log_access, log_access_admin, log_state, reset_state_from_local, reset_state_from_remote, \
    commit_state, prevent_self_calls, ignore_bot_calls

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
    await client.send_message(message.channel, INSTRUCTIONS)


@prevent_self_calls
@log_access_admin("set_all")
async def set_all(message, client):
    server = message.server
    new_nick = message.clean_content.strip()[:-7]
    await client.send_message(message.channel, 'Setting all nick-names to {}'.format(new_nick))
    if len(new_nick) < 32:
        state, file_name = await log_state(server)
        with open(file_name, "rb") as output:
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
        await client.send_message(message.channel, 'Reverting nicknames to match local state')
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
            await client.send_message(message.channel,
                                      "Reverting nicknames to match remote state @'{}'".format(command_end))
            if not await reset_state_from_remote(server, command_end, client):
                await client.send_message(message.channel, "OP failed; Bad file")
        elif message.attachments:
            for attachment in message.attachments:
                await client.send_message(message.channel,
                                          "Reverting nicknames to match attachment state @'{}'".format(
                                              attachment.url))
                if not await reset_state_from_remote(server, attachment, client):
                    await client.send_message(message.channel, "OP failed; Bad file")
        else:
            await client.send_message(message.channel, "OP failed; Bad file")


commands = [
    ChatCommand("bryce", Commands.bryce_Bryce).alias("Bryce", required=True).blocks().is_case_sensitive(),
    ChatCommand("bryce", Commands.bryce).is_case_sensitive(),
    ChatCommand("Bryce", Commands.bryce).is_case_sensitive(),
    ChatCommand("token", Commands.token).alias("auth"),
    ChatCommand("boat", Commands.boat),
    ChatCommand("<@", Commands.bryce_mention).alias(">", required=True)
]


@prevent_self_calls
@ignore_bot_calls
async def mention(message, client):
    # Code Golf :)
    # [c(message=message.content, server=server, client=client) for c in commands if
    #  c.foundin(message.content)]

    for command in commands:
        if command.found_in(message.content):
            await command(message=message.content, server=message.server, client=client, env=message)
            if command.blocking:
                return
