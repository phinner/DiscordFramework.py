import json
from sys import path
from random import choice, randint
from discord import Embed, Colour

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
        else: txt = f"The number goes from 0 to {max_number}, are you trying to burn my CPU ? 😡"
    else: txt = "The arguments you tried to input are invalid, try to use a whole number."
    await msg.channel.send(txt)


@CommandHandler.registerCommand(
    name="say", category="Fun",
    usage="say [msg]",
    description="Dit un msg à votre place, ptêt parce que vous êtes trop paresseux..."
)
async def say(client, msg, args):
    if args is None:
        txt = "Alors, tu n'as rien de bon à dire ?"
    else: txt = args
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
    for i in range(10 - sliced_rn): txt += "░"

    # Loads some quotes from a json file
    with open(f"{client.CLIENT_PATH}\\skill.json", "r", encoding="utf-8") as q:
        quotes_dict = json.load(q)

    # Iterates through the quote levels, if it finds a level higher than the picked number, break
    for level in sorted(int(i) for i in quotes_dict.keys()):
        if int(level) <= random_number:
            quote = quotes_dict[str(level)]
        else: break

    txt += f"⟫ {random_number}%. {choice(quote) if type(quote) is list else quote}"
    await msg.channel.send(txt)


@CommandHandler.registerCommand(
    name="help", alias="h", category="Utilitaire",
    usage="help [cmd]",
    description="Retourne la liste complète des commandes, utilisez `help [cmd]` Pour avoir plus d'informations"
)
async def help_cmd(client, msg, args):
    # If the args are None, return the whole command list, else, give details about the give command in args
    if args is None:
        help_message = Embed(
            title="Commandes",
            description="Liste des commandes disponibles",
            color=Colour.purple()
        )

        # iterates through the command categories
        for category, commands in client.CommandHandler.commandCategories.items():
            field_content = str()

            # Field_content contains all the commands which belong to the category
            for cmd in commands:
                field_content += cmd.name + "\n"

            if category is None:
                category = "Unclassified"

            help_message.add_field(
                name=category, inline=True,
                value=field_content)
        help_message.set_footer(text=f"Requested by: {msg.author.name}#{msg.author.discriminator}")

    else:
        if args in client.CommandHandler.commandNames:
            help_message = Embed(
                title=f"{args.capitalize()}",
                description=f"`{client.CommandHandler.commandNames[args].usage}` > {client.CommandHandler.commandNames[args].description}",
                color=Colour.purple())
        else:
            return await msg.channel.send(
                f"`{args}` is invalid, check the command list or try the full name of the command.",
                **client.error_kwargs)  # Remember the pre-made kwargs for error messages ?

    await msg.channel.send(content=None, embed=help_message)


def better_detector(msg, kwords): return any(kword.casefold() in msg.content.casefold() for kword in kwords)
# I changed the default lambda function to make the reader trigger even if the keywords are in capital letters


MessageHandler.registerReader(
    name="Honteux", keywords=["honteux", "pathétique"], quotes=["C'EST HONTEUX!"], detector=better_detector
)


@MessageHandler.registerReader(
    name="idiot", keywords=["idiot"], detector=better_detector
)
async def idiot(client, msg):
    await msg.channel.send(f"{msg.author.display_name} est un idiot lol!", delete_after=3)
