from Chat import methods
from Chat.Compilers import BlockingCommand, Command
from Chat.Matchers import CaseSensitiveMatcher, RegexMatcher
from Chat.methods import about, restore, set_all, helpme
from helpers import prevent_self_calls, ignore_bot_calls

commands = None


@prevent_self_calls
@ignore_bot_calls
async def mention(message, client):
    global commands
    if not commands:
        commands = [
            BlockingCommand(about).listens_for("^!about", RegexMatcher).alias("^❕ 🇦 🇧 🇴 🇺 🇹", RegexMatcher),
            BlockingCommand(helpme).listens_for("<@!?{}>".format(client.user.id), RegexMatcher),

            BlockingCommand(restore).listens_for("^!restore", RegexMatcher),
            BlockingCommand(set_all).listens_for("^.+ it up!", RegexMatcher),
            BlockingCommand(methods.bryce_Bryce).listens_for("bryce", CaseSensitiveMatcher).including("Bryce",
                                                                                                      CaseSensitiveMatcher),
            Command(methods.bryce).listens_for("bryce"),
            Command(methods.token).listens_for("token").alias("auth"),
            Command(methods.boat).listens_for("boat"),
            Command(methods.bryce_mention).listens_for("<@!?\d+>", RegexMatcher),
            Command(methods.i_wanna_be_like).listens_for("[I|i] wan(?:na|'t|t) (?:to )?be like <@!?(\d+)>", RegexMatcher)
        ]
    for command in commands:
        if command.compiler.matches(message.content):
            await command.compiler(message=message.content, server=message.server, client=client, env=message)
            if isinstance(command.compiler, BlockingCommand):
                return
