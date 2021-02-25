import json
from sys import path
from random import choice, randint

path.append('D:\\HDD_Coding\\Gitgud\\DiscordBot-Framework')
from DiscordBotFramework.command import CommandHandler
from DiscordBotFramework.message import MessageHandler


@CommandHandler.registerCommand(
    name="count", alias="c", category="Fun",
    usage="count [number]",
    description="Compte le nombre de Tx, **number** est optionnel."
)
async def count(client, msg, args):
    txt, max_number = str(), 100
    if args is None:
        txt = "1, 2, 3 petits Tx..."
    elif args.isdigit() and args.find(" ") == -1:
        args = int(args)
        if 0 < args <= max_number:
            for n in range(1, args + 1):
                txt += f"{n}, "
            txt += "petit" + ("" if args <= 1 else "s") + " Tx..."
        else:
            txt = f"The number goes from 0 to {max_number}, are you trying to burn my CPU ? 😡"
    else:
        txt = "The arguments you tried to input are invalid, try to use a whole number."
    await client.MessageHandler.sendMessage(msg.channel.id, txt)


@CommandHandler.registerCommand(
    name="say", category="Fun",
    usage="say [msg]",
    description="Dit un msg à votre place, ptêt parce que vous êtes trop paresseux..."
)
async def say(client, msg, args):
    if args is None: txt = "Alors, tu n'as rien de bon à dire ?"
    else: txt = f"**{msg.author.display_name}** a dit: {args}"
    await msg.channel.send(txt)


@CommandHandler.registerCommand(
    name="skill", category="Fun",
    usage="skill",
    description="Jauge votre niveau de skill, idéal pour départager les matchs serrés."
)
async def skill(client, msg, args):
    # Generates the skill bar
    txt, random_number = f"{msg.author.display_name} a un skill de:\n⟪", randint(0, 100)
    sliced_rn, quote, quotes = random_number // 10, str(), list()

    if args is not None:
        await msg.channel.send("**Astuce**: skill n'a pas besoin d'arguments puisque c'est aléatoire 😉")

    for i in range(sliced_rn): txt += "█"
    for i in range(9 - sliced_rn + (1 if random_number < 100 else 0)): txt += "░"

    # Picks a random quote
    with open(f"{client.CLIENT_PATH}\\skill.json", "r", encoding="utf-8") as q:
        quotes_dict = json.load(q)
    for level in sorted(int(i) for i in quotes_dict.keys()):
        print(sorted(quotes_dict.keys()), level, sorted(int(i) for i in quotes_dict.keys()))
        if int(level) <= random_number:
            quotes = quotes_dict[str(level)]
        else: break
    if quotes: quote = choice(quotes)

    txt += f"⟫ {random_number}%. {quote}"
    await msg.channel.send(txt)


MessageHandler.registerReader(
    name="Honteux", keywords=["honteux", "pathétique"], quotes=["C'EST HONTEUX!"],
    detector=lambda msg, kwords: any(kword.casefold() in msg.content.casefold() for kword in kwords)
    # I changed the default lambda function to make the reader trigger even if the keywords are in capital letters
)


@MessageHandler.registerReader(
    name="idiot"
)
async def idiot(client, msg):
    if msg.content.casefold().find("idiot") != -1:
        await msg.channel.send(f"{msg.author.display_name} est un idiot lol!", delete_after=5)
