from discord import Message

from Chat.Classes import ChatCommand


async def react(env: Message):
    if env.guild.me.mentioned_in(env):
        without_self = env.content.replace(env.guild.me.mention, "")
        if len(without_self.split()) > 2:
            await env.channel.send("Thanks {}, Right back at you :wink:".format(env.author.display_name))
            await env.add_reaction("❤")
        else:
            await env.channel.send("Hi, I'm a helpful assistance bot, try !about".format(env.author.display_name))


async def bryce_Bryce(env):
    await env.channel.send("To bryce or not to Bryce?")
    await env.add_reaction("🤔")


async def token(env: Message):
    await env.channel.send("Hide your tokens kiddos!")
    await env.add_reaction("🐱")
    await env.add_reaction("💻")


async def boat(env: Message):
    await env.channel.send("Big Boat, Much Oreo! (sign up now at https://tiny.cc/floatParty)")
    await env.add_reaction("⛵")


async def bryce_mention(env):
    for user in env.mentions:
        if user.display_name.lower().startswith("bryce"):
            await env.add_reaction("🛐")
            return
