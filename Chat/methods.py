import re

from discord import Forbidden

from helpers import prevent_self_calls, log_access_admin, log_state, commit_state, reset_state_from_local, \
    reset_state_from_remote, log_access


async def bryce(client, env):
    match = re.match("^.*([b|B]ryce).*$", env.content).groups()[0]
    await client.send_message(env.channel, "I love {}, don't you?".format(match))
    await client.add_reaction(env, "❤")


async def bryce_Bryce(client, env):
    await client.send_message(env.channel, "To bryce or not to Bryce?")
    await client.add_reaction(env, "🤔")


async def token(client, env):
    await client.send_message(env.channel, "Hide your tokens kiddos!")
    await client.add_reaction(env, "🐱")
    await client.add_reaction(env, "💻")


async def boat(client, env):
    await client.send_message(env.channel, "Big Boat Sailed! Keep an ear out for next years voyage!")
    await client.add_reaction(env, "⛵")


async def bryce_mention(client, env):
    for user in env.mentions:
        if user.display_name.lower().startswith("bryce"):
            await client.add_reaction(env, "🛐")
            return


@prevent_self_calls
@log_access_admin("set_all")
async def set_all(env, client):
    server = env.server
    new_nick = env.clean_content.strip()[:-7]
    await client.send_message(env.channel, 'Setting all nick-names to {}'.format(new_nick))
    if len(new_nick) < 32:
        state, file_name = await log_state(server)
        with open(file_name, "rb") as output:
            await client.send_file(env.channel, output)
        if state is not None:
            for key in state:
                state[key] = new_nick
            await commit_state(state, server, client)
            await client.send_message(env.channel, 'Execution Complete')

        else:
            await client.send_message(env.channel,
                                      'Execution failed; no targets found or state already exists')
    else:
        await client.send_message(env.channel,
                                  'Cannot change everyone\'s nickname to {} as len > 32'.format(new_nick))


INSTRUCTIONS_LEGACY = """USING THE BRYCE BOT
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
async def helpme(env, client):
    with open("helpme.desc") as description:
        await client.send_message(env.channel, description.read())


@prevent_self_calls
@log_access("about")
async def about(env, client):
    try:
        with open("about.desc") as description:
            await client.send_message(env.channel, description.read())
    except Exception as ex:
        await client.send_message(env.channel, "Could not load description! (Using Legacy)")
        await client.send_message(env.channel, INSTRUCTIONS_LEGACY)


@prevent_self_calls
@log_access_admin("restore")
async def restore(env, client):
    command = env.content.lower().strip()
    server = env.server
    if command == "!restore":
        await client.send_message(env.channel, 'Reverting nicknames to match local state')
        if not await reset_state_from_local(server, client):
            await client.send_message(env.channel, 'State reset failed; Reason, no current state available')

    if command.startswith("!restore from"):
        command_end = env.content.strip("!restore from").strip()
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if re.match(regex, command_end):
            await client.send_message(env.channel,
                                      "Reverting nicknames to match remote state @'{}'".format(command_end))
            if not await reset_state_from_remote(server, command_end, client):
                await client.send_message(env.channel, "OP failed; Bad file")
        elif env.attachments:
            for attachment in env.attachments:
                await client.send_message(env.channel,
                                          "Reverting nicknames to match attachment state @'{}'".format(
                                              attachment.url))
                if not await reset_state_from_remote(server, attachment, client):
                    await client.send_message(env.channel, "OP failed; Bad file")
        else:
            await client.send_message(env.channel, "OP failed; Bad file")


@prevent_self_calls
@log_access("IWannaBeLike")
async def i_wanna_be_like(env, client):
    message = env.content
    matcher = re.match("[I|i] wan(?:na|'t|t) (?:to)? be like <@!?(\d+)>", message)
    user_id = matcher.groups()[0]
    user_info = await client.get_user_info(user_id)
    try:
        await client.change_nickname(env.author, user_info.name)
    except Forbidden:
        await client.send_message(env.channel, "Can't touch that!")
        return
    await client.send_message(env.channel, "OK!")
