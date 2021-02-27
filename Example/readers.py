from sys import path
from auto_all import *

path.append('D:\\HDD_Coding\\Gitgud\\DiscordBot-Framework')
from DiscordBotFramework.message import MessageHandler


def _better_detector(msg, kwords):
    return any(kword.casefold() in msg.content.casefold() for kword in kwords)
# I changed the default lambda function to make the reader trigger even if the keywords are in capital letters


__all__ = list()
start_all(globals())


MessageHandler.registerReader(
    name="Honteux", keywords=["honteux", "pathétique"], quotes=["C'EST HONTEUX!"], detector=_better_detector
)


@MessageHandler.registerReader(
    name="idiot", keywords=["idiot"], detector=_better_detector
)
async def idiot(client, msg):
    await msg.channel.send(f"{msg.author.display_name} est un idiot lol!", delete_after=3)


end_all(globals())
