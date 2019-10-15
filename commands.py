import re

from discord import Message, Member, Client, TextChannel, File

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
    Mention me to check if I'm working
"""


@prevent_self_calls
@log_access("about")
async def about(message: Message):
    await message.channel.send(INSTRUCTIONS)


@prevent_self_calls
@log_access_admin("set_all")
async def set_all(message: Message, client: Client):
    server = message.guild
    new_nick = message.clean_content.strip()[:-7]
    if len(new_nick) < 32:
        state, file_name = await log_state(server)
        with open(file_name, "rb") as output:
            file = File(output, filename="state_before.json".format(message.content))
            await message.channel.send('Setting all nick-names to {}'.format(new_nick), file=file)
        if state is not None:
            for key in state:
                state[key] = new_nick
            await commit_state(state, server, client)
            await message.channel.send('Execution Complete')

        else:
            await message.channel.send('Execution failed; no targets found or state already exists')
    else:
        await message.channel.send('Cannot change everyone\'s nickname to {} as len > 32'.format(new_nick))


@prevent_self_calls
@log_access_admin("restore")
async def restore(message: Message, client: Client):
    command = message.content.lower().strip()
    server = message.guild
    if command == "!restore":
        await message.channel.send('Reverting nicknames to match local state')
        if not await reset_state_from_local(server, client):
            await message.channel.send('State reset failed; Reason, no current state available')

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
            await message.channel.send("Reverting nicknames to match remote state @'{}'".format(command_end))
            if not await reset_state_from_remote(server, command_end, client):
                await message.channel.send("OP failed; Bad file")
        elif message.attachments:
            for attachment in message.attachments:
                await message.channel.send("Reverting nicknames to match attachment state @'{}'".format(attachment.url))
                if not await reset_state_from_remote(server, attachment, client):
                    await message.channel.send("OP failed; Bad file")
        else:
            await message.channel.send("OP failed; Bad file")


async def welcome_user(member: Member):
    system_channel = member.guild.system_channel
    intro_message = ""
    for channel in member.guild.channels:  # type: TextChannel
        if channel.name.startswith("intro"):
            intro_message = """\nWe __highly__ recommend hopping over to {intro_channel} and saying hi {emoji}.""".format(
                emoji="👋", intro_channel=channel.mention)
            break
    message = """*Welcome* {user_mention}, you've joined the CSIT Society discord server! {say_hi_message}""".format(user_mention=member.mention, say_hi_message=intro_message)
    await system_channel.send(message)


commands = [
    ChatCommand("token", Commands.token).alias("auth"),
    ChatCommand("boat", Commands.boat),
    ChatCommand("<@", Commands.react).alias(">", required=True)
]


@prevent_self_calls
@ignore_bot_calls
async def mention(message, client):
    # Code Golf :)
    # [c(message=message.content, server=server, client=client) for c in commands if
    #  c.foundin(message.content)]

    for command in commands:
        if command.found_in(message.content):
            await command(message=message.content, server=message.guild, client=client, env=message)
            if command.blocking:
                return
