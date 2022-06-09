import interactions
import nextcord
from nextcord.ext import commands

import env
import bd
import fun_functions
import myconst
import block_functions
import admin_functions
import moderator_functions

intents = nextcord.Intents.default()
intents.members = True

bot_moderator_guild_id = 984172930365796409

bot_description = 'Генерал Гачи Армии, служу на первой линни обороны очка админа'

bot = commands.Bot(command_prefix='/', description=bot_description, intents=intents, help_command=None,
                   activity=nextcord.Activity(type=nextcord.ActivityType.competing, name='?help'))


# Block commands

@bot.slash_command(
    name="help",
    description="Описание команд бота"
)
async def help(interaction: nextcord.Interaction):
    embed = nextcord.Embed(color=0x17cf45, title='Помощь', description=myconst.USER_HELP)

    if block_functions.check_for_admin(str(interaction.user.id)) == 1:
        moderator_embed = nextcord.Embed(color=0x17cf45, title="Помощь для модераторов",
                                         description=myconst.MODERATOR_HELP)
        await interaction.user.send(embed=moderator_embed)

    if block_functions.check_for_user_registration(str(interaction.user.id)):
        await interaction.send(embed=embed)
    else:
        view = block_functions.HelpButtonView()
        print('user not registered')
        await interaction.send(embed=embed, view=view)
        await view.wait()


@bot.slash_command(
    name="registration",
    description="Регистрация в моей базе",
)
async def registration(interaction: nextcord.Interaction):
    modal = block_functions.Registration()
    await interaction.response.send_modal(modal)


@bot.slash_command(
    name="balance",
    description="Проверить свой баланс",
)
async def balance(interaction):
    await block_functions.validate_registration(interaction)
    await block_functions.balance(interaction)


@bot.slash_command(
    name="pay",
    description="Передать коины другому пользователю"
)
async def pay(
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(description="кому", required=True),
        coins_to_pay: int = nextcord.SlashOption(description="кол-во коинов", required=True)):
    await block_functions.validate_registration(interaction)
    return await block_functions.pay(interaction, member, coins_to_pay)


@bot.slash_command(
    name="update",
    description="Обновить имя в моей базе",
)
async def update(interaction: nextcord.Interaction):
    await block_functions.validate_registration(interaction)
    modal = block_functions.UpdateName()
    await interaction.response.send_modal(modal)


# Fun commands


@bot.slash_command(
    name="case",
    description="Открыть кейс",
)
async def case(interaction: nextcord.Interaction):
    await block_functions.validate_registration(interaction)
    view = fun_functions.CaseDropdownView()

    return await interaction.send("Выберите кейс: ", view=view, ephemeral=True)


@bot.slash_command(
    name="casino",
    description="Казино",
)
async def casino(interaction: nextcord.Interaction):
    await block_functions.validate_registration(interaction)
    modal = fun_functions.Casino()
    await interaction.response.send_modal(modal)


@bot.slash_command(
    name="creator",
    description="Информация о создателе сервера",
)
async def creator(interaction: nextcord.Interaction):
    return await fun_functions.creator(interaction)


@bot.slash_command(
    name="bibametr",
    description="Узнай, насколько большой у тебя стручек ?",
)
async def bibametr(interaction: nextcord.Interaction):
    return await fun_functions.bibametr(interaction)


@bot.slash_command(
    name="gay",
    description="Узнай, считаю ли я тебя геем ?",
)
async def gay(interaction: nextcord.Interaction):
    return await fun_functions.gay(interaction)


@bot.slash_command(
    name="rickandmorty",
    description="Информация о герое из Рик и Морти"
)
async def rickandmorty(interaction: nextcord.Interaction, character_id: int = nextcord.SlashOption(description="Айди персонажа", required=True)):
    return await fun_functions.rickandmorty(interaction, character_id)


@bot.slash_command(
    name="cases",
    description="Узнай сколько ты открыл кейсов",
)
async def cases(interaction: nextcord.Interaction):
    return await fun_functions.cases(interaction)


# Administrator commands

@bot.slash_command(
    name="giveaway",
    description="Провести розыгрыш",
    guild_ids=[bot_moderator_guild_id],
)
async def giveaway(interaction: nextcord.Interaction):
    await block_functions.validate_registration(interaction)
    modal = admin_functions.Giveaway()
    await interaction.response.send_modal(modal)


# Moderator commands


bot.run(env.TOKEN)
