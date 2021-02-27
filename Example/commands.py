import json
from sys import path
from random import choice, randint
from discord import Embed, Colour
from auto_all import *

path.append('D:\\HDD_Coding\\Gitgud\\DiscordBot-Framework')
from DiscordBotFramework.command import CommandManager


__all__ = list()
start_all(globals())


@CommandManager.registerCommand(
    name="count", alias="c", category="Fun", usage="count [number]",
    description="Compte le nombre de Tx, `number` est optionnel."
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


@CommandManager.registerCommand(
    name="say", category="Fun", usage="say [msg]",
    description="Dit un message à ta place, ptêt parce que tu es trop paresseux..."
)
async def say(client, msg, args):
    if args is None:
        txt = "Alors, tu n'as rien de bon à dire ?"
    else: txt = args
    await msg.channel.send(txt)


@CommandManager.registerCommand(
    name="skill", category="Fun", usage="skill",
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


@CommandManager.registerCommand(
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
        for category, commands in client.CommandManager.commandCategories.items():
            field_content = str()

            # Field_content contains all the commands which belong to the category
            for cmd in commands:
                field_content += cmd.name + (f" / {cmd.alias}" if cmd.alias is not None else "") + "\n"

            if category is None:
                category = "Unclassified"

            help_message.add_field(
                name=category, inline=True,
                value=field_content)
        help_message.set_footer(text=f"Requested by: {msg.author.name}#{msg.author.discriminator}")

    else:
        if args in client.CommandManager.commandNames:
            cmd = client.CommandManager.commandNames[args]
            help_message = Embed(
                title=f"{cmd.name.capitalize()}" + (f" / {cmd.alias}" if cmd.alias is not None else ""),
                description=f"`{cmd.usage}` > {cmd.description}",
                color=Colour.purple())

            # This is for displaying the categories of my meme command
            if args == "meme":
                available_categories = str()
                for category in client.meme_dict.keys():
                    available_categories += f"`{category}`, "
                available_categories = available_categories[:-2]
                help_message.add_field(name="Catégories", value=available_categories)
        else:
            return await msg.channel.send(
                f"`{args}` is invalid, check the command list or try the full name of the command.",
                **client.error_kwargs)  # Remember the pre-made kwargs for error messages ?

    await msg.channel.send(content=None, embed=help_message)


@CommandManager.registerCommand(
    name="meme", category="Fun", usage="meme [category]",
    description="Affiche un meme aléatoire. Si `[category]` est ajouté, il affichera les memes de catégorie spécifiée."
)
async def parking_meme(client, msg, args):
    # If args is None, it will return the every meme of the google drive folder,
    #  else, it will look in the folder of the specified category
    if args is None:
        meme_list = client.API["drive"].extractFiles(
            client.meme_dict["all"], "id, name, webContentLink, webViewLink, mimeType, description"
        )

    else:
        if args.casefold() in client.meme_dict:
            meme_list = client.API["drive"].extractFiles(
                client.meme_dict[args], "id, name, webContentLink, webViewLink, mimeType, description"
            )

        else:
            return await msg.channel.send(
                f"The meme `{args}` category does not exist, check the available categories by doing `help meme`.",
                **client.error_kwargs
            )

    if len(meme_list) == 0:
        return await msg.channel.send(f"The `{args}` category is currently empty.", **client.error_kwargs)

    meme = choice(meme_list)
    title = meme["description"] if "description" in meme else meme["name"]

    meme_embed = Embed(title=title, url=meme["webViewLink"], colour=Colour.random())
    meme_embed.set_image(url=meme["webContentLink"])
    meme_embed.set_footer(text=f"Requested by: {msg.author.name}#{msg.author.discriminator}")
    await msg.channel.send(content=None, embed=meme_embed)


@CommandManager.registerCommand(
    name="ping", category="Utilitaire", usage="ping",
    description="Mesure la latence du bot."
)
async def ping(client, msg, args):
    latency = str(int(client.latency * 1000)) + " ms"
    await msg.channel.send(content=None, embed=Embed(title="Pong !", description=latency, color=Colour.purple()))


end_all(globals())
