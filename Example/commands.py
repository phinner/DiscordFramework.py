import json

from random import choice
from random import randint
from discord import Embed
from discord import Colour
from auto_all import *

from Framework.command import CommandManager
from Framework.utils import readPICKLE, readJSON


__all__ = list()
start_all(globals())

# ------------------------------------------------------------------------------- #

@CommandManager.registerCommand(
    name="count",
    alias="c",
    category="Fun",
    usage="count [number]",
    description="Compte le nombre de Tx, `number` est optionnel."
)
async def count(client, msg, args):
    txt, max_number = str(), 100

    # The default response
    if args is None:
        txt = "1, 2, 3 petits Tx..."

    # If the argument is a number, the spam begins...
    elif args.isdigit() and args.find(" ") == -1:
        args = int(args)

        if 0 < args <= max_number:
            for n in range(1, args + 1):
                txt += f"{n}, "
            txt += "petit" + ("" if args <= 1 else "s") + " Tx..."
        else:
            txt = f"Le nombre va de 0 à {max_number}, es-tu en train d'essayer de brûler mon processeur ? 😡"
    else:
        txt = "Les arguments que vous avez essayé d'entrer sont invalides, essagez des nombres entiers."

    await msg.channel.send(txt)

# ------------------------------------------------------------------------------- #

@CommandManager.registerCommand(
    name="say",
    category="Fun",
    usage="say [msg]",
    description="Dit un message à ta place, ptêt parce que tu es trop paresseux..."
)
async def say(client, msg, args):
    if args is None:
        txt = "Alors, tu n'as rien de bon à dire ?"
    else:
        txt = args

    await msg.channel.send(txt)

# ------------------------------------------------------------------------------- #

@CommandManager.registerCommand(
    name="skill",
    category="Fun",
    usage="skill",
    description="Jauge votre niveau de skill, idéal pour départager les matchs serrés."
)
async def skill(client, msg, args):
    txt = f"{msg.author.display_name} a un skill de:\n⟪"
    number = randint(0, 100)
    quote= str()

    if args is not None:
        await msg.channel.send("**Astuce**: skill n'a pas besoin d'arguments puisque c'est aléatoire 😉")

    # Generates the skill bar
    for i in range(number // 10):
        txt += "█"
    for i in range(10 - (number // 10)):
        txt += "░"

    # Loads some quotes from a json file
    with open(f"{client.CLIENT_PATH}\\skill.json", "r", encoding="utf-8") as q:
        quotes_dict = json.load(q)

    # Iterates through the quote levels, if it finds a level higher than the picked number, break
    for level in sorted(int(i) for i in quotes_dict.keys()):
        if int(level) <= number:
            quote = quotes_dict[str(level)]
        else:
            break

    txt += f"⟫ {number}%. {choice(quote) if type(quote) is list else quote}"

    await msg.channel.send(txt)

# ------------------------------------------------------------------------------- #

@CommandManager.registerCommand(
    name="ping",
    category="Utilitaire",
    usage="ping",
    description="Mesure la latence du bot."
)
async def ping(client, msg, args):
    latency = str(int(client.latency * 1000)) + " ms"
    await msg.channel.send(content=None, embed=Embed(title="Pong !", description=latency, color=client.getDisplayColour(msg)))

# ------------------------------------------------------------------------------- #

@CommandManager.registerCommand(
    name="embed"
)
async def img(client, msg, args):
    test = Embed()
    test.set_image(url=args)
    await msg.channel.send(content=None, embed=test)

# ------------------------------------------------------------------------------- #

@CommandManager.registerCommand(
    name="meme",
    category="Fun",
    usage="meme [category]",
    description="Affiche un meme aléatoire. Si `[category]` est ajouté, il affichera les memes de la catégorie spécifiée."
)
async def parking_meme(client, msg, args):
    def getMeme(index):
        if not index:
            return None

        meme = choice(list(index.items()))
        if type(meme[1]) == dict:
            return getMeme(meme[1])

        return meme

    meme_index = readJSON(f"{client.CLIENT_PATH}\\memes.json")

    # If args is None, it will return a random meme
    # else, it will look in the folder of the specified category
    if args is None:
        meme = getMeme(meme_index)
    else:
        category = args.casefold()

        if category in meme_index and type(meme_index[category]) == dict:
            meme = getMeme(meme_index[category])
        else:
            return await msg.channel.send(
                f"The meme `{category}` category does not exist, check the available categories by doing `help meme`.",
                **client.error_kwargs
            )

    if meme == None:
        return await msg.channel.send(f"The `{args}` category is currently empty.", **client.error_kwargs)

    meme_embed = Embed(title=meme[0].split(".")[0], url=meme[1], colour=Colour.random())
    meme_embed.set_image(url=(meme[1][:-1] + "1"))  # -> Make the link embedable by replacing ?dl=0 by ?dl=1
    meme_embed.set_footer(text=f"Requested by: {msg.author.name}#{msg.author.discriminator}")
    await msg.channel.send(content=None, embed=meme_embed)

# ------------------------------------------------------------------------------- #

@CommandManager.registerCommand(
    name="help",
    alias="h",
    category="Utilitaire",
    usage="help [cmd]",
    description="Retourne la liste complète des commandes, utilisez `help [cmd]` Pour avoir plus d'informations"
)
async def help_cmd(client, msg, args):
    # If the args are None, return the whole command list, else, give details about the give command in args
    if args is None:
        help_message = Embed(
            title="Commandes",
            description="Liste des commandes disponibles",
            color=client.getDisplayColour(msg)
        )

        # iterates through the command categories
        for category, commands in client.CommandManager.Categories.items():
            field_content = str()

            # Field_content contains all the commands which belong to the category
            for cmd in commands:
                field_content += cmd.name + (f" / {cmd.alias}" if cmd.alias is not None else "") + "\n"

            help_message.add_field(name=category, inline=True, value=field_content)

    else:
        if args in client.CommandManager.Index:
            cmd = client.CommandManager.Index[args]

            help_message = Embed(
                title=f"{cmd.name.capitalize()}" + (f" / {cmd.alias}" if cmd.alias is not None else ""),
                description=f"`{cmd.usage}` > {cmd.description}",
                color=client.getDisplayColour(msg)
            )

            # This is for displaying the categories of my meme command
            if args == "meme":
                categories = readPICKLE(f"{client.CLIENT_PATH}\\memes.pickle")["categories"]

                if categories:
                    text = f"`{categories[0]}`"

                    for n in range(1, len(categories)):
                        text += f", `{categories[n]}`"

                    help_message.add_field(name="Catégories", value=text)

        else:
            return await msg.channel.send(
                f"`{args}` is invalid, check the command list by doing ` \
                {client.GuildManager.Index[str(msg.guild.id)].prefix}help`.",
                **client.error_kwargs)  # Remember the pre-made kwargs for error messages ?

    help_message.set_footer(text=f"Requested by: {msg.author.name}#{msg.author.discriminator}")

    await msg.channel.send(content=None, embed=help_message)

# ------------------------------------------------------------------------------- #

end_all(globals())

# ------------------------------------------------------------------------------- #

""" I tried to make a debug command, but exec act like a new python file so it's useless
@CommandManager.registerCommand(
    name="exec",
    category="Developeur",
    usage="exec [```code```]",
    description="Execute le code"
)
async def execute(client, msg, args):
    async def output(text):
        await msg.channel.send(f"```\n{text}\n```")

    if args.startswith("```") and args.endswith("```"):
        try:
            output(eval(args[3:-3]))
        except Exception as e:
            await output(str(e))
    else:
        await msg.channel.send("This is not a block of code")
"""

"""
The old meme command, imma never touch google drive API again for image management, even if it's easier

@CommandManager.registerCommand(
    name="meme", category="Fun", usage="meme [category]",
    description="Affiche un meme aléatoire. Si `[category]` est ajouté, il affichera les memes de catégorie spécifiée."
)
async def parking_meme(client, msg, args):
    # If args is None, it will return the every meme of the google drive folder,
    #  else, it will look in the folder of the specified category
    if args is None:
        meme_list = client.API["drive"].extractFiles(
            client.meme_dict["all"], "trashed = 'false'", "name, webContentLink, webViewLink, mimeType"
        )

    else:
        if args.casefold() in client.meme_dict:
            meme_list = client.API["drive"].extractFiles(
                client.meme_dict[args], "trashed = 'false'", "name, webContentLink, webViewLink, mimeType"
            )

        else:
            return await msg.channel.send(
                f"The meme `{args}` category does not exist, check the available categories by doing `help meme`.",
                **client.error_kwargs
            )

    if len(meme_list) == 0:
        return await msg.channel.send(f"The `{args}` category is currently empty.", **client.error_kwargs)

    meme = choice(meme_list)

    meme_embed = Embed(title=meme["name"].split(".")[0], url=meme["webViewLink"], colour=Colour.random())
    meme_embed.set_image(url=meme["webContentLink"])
    meme_embed.set_footer(text=f"Requested by: {msg.author.name}#{msg.author.discriminator}")
    await msg.channel.send(content=None, embed=meme_embed)
"""

# ------------------------------------------------------------------------------- #
