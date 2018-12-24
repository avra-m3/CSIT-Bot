from Chat.Classes import ChatCommand


async def bryce(command: ChatCommand, client, env):
    await client.send_message(env.channel, "I love {}, don't you?".format(command.name))
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
