# This example requires the 'members' privileged intent to use the Member converter.

import env
import typing
import random
import dumper
# import rick_and_morty_api
import requests
import bd
import datetime
import roles
import spin
import time
import mathem
import work_with_api
import uuid
import myconst

import nextcord
from nextcord.ext import commands
import interactions

intents = nextcord.Intents.default()
# intents.members = True

# bot = commands.Bot(command_prefix='/', intents=intents, help_command=None,
#                    activity=nextcord.Activity(type=nextcord.ActivityType.competing, name='/help'),
#                    owner_ids=[345526389665038336])

bot = commands.Bot(command_prefix='?', help_command=None, activity=nextcord.Activity(type=nextcord.ActivityType.competing, name='?help'))


# Ивенты
@bot.event
async def on_message(message):
    if check_for_user_mute(message.author.id) is True:
        return await message.delete()

    await bot.process_commands(message)


async def on_command_error(ctx, error):
    return await help(ctx)


@bot.command(name="передать")
async def pay_user_to_user(ctx: commands.Context, member: nextcord.Member, current_coins_count):
    current_coins_count = int(current_coins_count)

    sql_to_check_valid_coins = f"SELECT coins FROM `users` WHERE discord_id = {ctx.message.author.id}"
    sql_to_add_coins = f"UPDATE `users` SET coins = coins + %s WHERE discord_id = %s"
    sql_to_drop_coins = f"UPDATE `users` SET coins = coins - %s WHERE discord_id = %s"

    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True)

    cursor.execute(sql_to_check_valid_coins)
    result = cursor.fetchone()
    coins_result = result[0]
    current_coins_result = int(coins_result)
    connection.close()

    if current_coins_result < current_coins_count + 10:
        return await ctx.send('Недостаточно баланса для перевода (комиссия = 10 коинов)')

    connection.connect()
    cursor.execute(sql_to_add_coins, (current_coins_count, member.id))
    cursor.execute(sql_to_drop_coins, (current_coins_count + 10, ctx.message.author.id))
    connection.commit()
    connection.close()

    embed = nextcord.Embed(color=0x28fc64, title='Перевод коинов',
                          description='Перевод успешно выполнен. Коммисия за перевод - **10 коинов**')

    return await ctx.send(embed=embed)


@bot.command(name="создатель")
async def creator(ctx: commands.Context):
    embed = nextcord.Embed(color=0x28fc64, title="Создатель", description=myconst.CREATOR)
    return await ctx.send(embed=embed)


@bot.command(name="розыгрыш")
async def rozigrash_ebana(ctx: commands.Context, coins_count):
    if coins_count is None:
        return await ctx.send('Вы не указали сумму розыгрыша')
    if check_for_admin(str(ctx.message.author.id)) == 1:
        await ctx.send(f'Розыгрываем {coins_count} коинов')
    else:
        return await ctx.send('Куда ты лезешь, клуша ?')

    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_get_all_users = f"SELECT * FROM `users`"
    cursor.execute(sql_to_get_all_users)
    result = cursor.fetchall()
    arr_count = len(result)
    random_user = random.choice(result)
    connection.close()

    time.sleep(5)

    embed = nextcord.Embed(color=0x702687,
                          description=f'Кол-во участников: **{str(arr_count)}**\n\nРозыгрывается: **{coins_count} коинов**')

    await ctx.send(embed=embed)

    time.sleep(5)

    embed = nextcord.Embed(color=0x702687, title="Победитель!",
                          description=f'Победил: <@' + random_user["discord_id"] + '>')

    connection.connect()
    sql_to_add_user_coins = f"UPDATE `users` SET coins = coins + %s WHERE discord_id = %s"
    cursor.execute(sql_to_add_user_coins, (int(coins_count), random_user["discord_id"]))
    connection.commit()
    connection.close()

    return await ctx.send(embed=embed)


# Админ команды
@bot.command(name="бан")
async def ban_user(ctx: commands.Context, member: nextcord.Member, time_to_ban, reason):
    if check_for_admin(str(ctx.message.author.id)) == 0:
        return await ctx.send('Ты не мой модератор')

    if member == ctx.message.author:
        return await ctx.send('Я не могу забанить вас')

    if check_for_admin(member.id) is None:
        await member.send(f'Вы были забанены администратором - {ctx.message.author.name}')
        await nextcord.Guild.ban(self=ctx.message.author.guild, user=member, reason=reason,
                                delete_message_days=int(time_to_ban))

        str_to_msg_and_log = f'Я забанил юзера {member.name} по указанию {ctx.message.author.name}. Причина: {reason}'

        print(str_to_msg_and_log)

        return await ctx.send(str_to_msg_and_log)

    if check_for_admin(member.id) == 1:
        return await ctx.send('Я не могу забанить своего модератора')

    await member.send(f'Вы были забанены администратором - {ctx.message.author.name}')
    await nextcord.Guild.ban(self=ctx.message.author.guild, user=member, reason=reason,
                            delete_message_days=int(time_to_ban))

    str_to_msg_and_log = f'Я забанил юзера {member.name} по указанию {ctx.message.author.name}. Причина: {reason}'
    print(str_to_msg_and_log)

    return await ctx.send(str_to_msg_and_log)


@bot.command(name="разбан")
async def unban_user(ctx: commands.Context, member: nextcord.Member):
    is_admin = False

    if check_for_admin(member.id) is None or check_for_admin(member.id) == 0:
        is_admin = False
    else:
        is_admin = True

    if is_admin:
        str_to_msg_and_log = f'Я разбанил юзера {member.name} по указанию {ctx.message.author.name}'
        await ctx.send(str_to_msg_and_log)
        print(str_to_msg_and_log)
        return await nextcord.Guild.unban(self=ctx.message.author.guild, user=member)


@bot.command(name="мут")
async def mute_user(ctx: commands.Context, member: nextcord.Member):
    is_admin = False

    if check_for_admin(member.id) is None or check_for_admin(member.id) == 0:
        is_admin = False
    else:
        is_admin = True

    if is_admin:
        connection = bd.get_connection()
        cursor = connection.cursor(buffered=True, dictionary=True)
        sql_to_mute_user = f"UPDATE `users` SET muted = 1 WHERE discord_id = {member.id}"
        cursor.execute(sql_to_mute_user)
        connection.commit()
        connection.close()

        await member.send(f'Вы были замучены модератором {ctx.message.author.name}')

        return await ctx.send(
            f'Я замутил пользователя <@{member.id}>. По указанию модератора: <@{ctx.message.author.id}>')


@bot.command(name="размут")
async def unmute_user(ctx: commands.Context, member: nextcord.Member):
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_unmute_user = f"UPDATE `users` SET muted = 0 WHERE discord_id = {member.id}"
    cursor.execute(sql_to_unmute_user)
    connection.commit()
    connection.close()

    await member.send(f"Вы были размучены модератором {ctx.message.author.name}")

    return await ctx.send(f"Я размутил пользователя <@{member.id}>. По указанию модератора: <@{ctx.message.author.id}>")


def check_for_user_mute(user_id: str):
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_check_is_user_mute = f"SELECT muted FROM `users` WHERE discord_id = {user_id}"
    cursor.execute(sql_to_check_is_user_mute)
    result = cursor.fetchone()

    if result is None:
        return False

    if result['muted'] is None:
        return False

    if int(result['muted']) == 1:
        return True
    else:
        return False


@bot.command(name="clear")
async def clear_chat(ctx: commands.Context, amount):
    amount = int(amount)
    if check_for_admin(str(ctx.message.author.id)) == 0:
        return await ctx.send('Я не думаю, что ты мой модератор')

    await ctx.channel.purge(limit=amount)

    return await ctx.send('Я очистил чат', delete_after=10)


@bot.command(name="модераторы")
async def moderators_list(ctx: commands.Context):
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    moderators = []
    sql_to_get_moderator_list = f"SELECT discord_id FROM `users` WHERE is_admin = 1"
    cursor.execute(sql_to_get_moderator_list)
    result = cursor.fetchall()

    for item in result:
        moderators.append(item['discord_id'])

    current_moderators = []

    for item in moderators:
        current_moderators.append(f"<@{item}>")

    str_result = ''

    for item in current_moderators:
        str_result += f'{item}\n'

    embed = nextcord.Embed(color=0x6b4391, title='Мои модераторы', description=str_result)

    return await ctx.send(embed=embed)


@bot.command()
async def userinfo(ctx: commands.Context, user: nextcord.User):
    # In the command signature above, you can see that the `user`
    # parameter is typehinted to `nextcord.User`. This means that
    # during command invocation we will attempt to convert
    # the value passed as `user` to a `nextcord.User` instance.
    # The documentation notes what can be converted, in the case of `nextcord.User`
    # you pass an ID, mention or username (discrim optional)
    # E.g. 80088516616269824, @Danny or Danny#0007

    # NOTE: typehinting acts as a converter within the `commands` framework only.
    # In standard Python, it is use for documentation and IDE assistance purposes.

    # If the conversion is successful, we will have a `nextcord.User` instance
    # and can do the following:
    user_id = user.id
    username = user.name
    avatar = user.avatar_url
    await ctx.send('User found: {} -- {}\n{}'.format(user_id, username, avatar))


@userinfo.error
async def userinfo_error(ctx: commands.Context, error: commands.CommandError):
    # if the conversion above fails for any reason, it will raise `commands.BadArgument`
    # so we handle this in this error handler:
    if isinstance(error, commands.BadArgument):
        return await ctx.send('Couldn\'t find that user.')


# Custom Converter here
class ChannelOrMemberConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str):
        # In this example we have made a custom converter.
        # This checks if an input is convertible to a
        # `nextcord.Member` or `nextcord.TextChannel` instance from the
        # input the user has given us using the pre-existing converters
        # that the library provides.

        member_converter = commands.MemberConverter()
        try:
            # Try and convert to a Member instance.
            # If this fails, then an exception is raised.
            # Otherwise, we just return the converted member value.
            member = await member_converter.convert(ctx, argument)
        except commands.MemberNotFound:
            pass
        else:
            return member

        # Do the same for TextChannel...
        textchannel_converter = commands.TextChannelConverter()
        try:
            channel = await textchannel_converter.convert(ctx, argument)
        except commands.ChannelNotFound:
            pass
        else:
            return channel

        # If the value could not be converted we can raise an error
        # so our error handlers can deal with it in one place.
        # The error has to be CommandError derived, so BadArgument works fine here.
        raise commands.BadArgument('No Member or TextChannel could be converted from "{}"'.format(argument))


@bot.command(name='уведомить')
async def notify(ctx: commands.Context, target: ChannelOrMemberConverter):
    # This command signature utilises the custom converter written above
    # What will happen during command invocation is that the `target` above will be passed to
    # the `argument` parameter of the `ChannelOrMemberConverter.convert` method and
    # the conversion will go through the process defined there.

    print(ctx.message.guild.name)

    await target.send('Проверь {fchat}, {fname}!'.format(fchat=ctx.message.guild.name, fname=target.name))

    return await ctx.send('Уведомил', delete_after=60)


@bot.command()
async def ignore(ctx: commands.Context, target: typing.Union[nextcord.Member, nextcord.TextChannel]):
    # This command signature utilises the `typing.Union` typehint.
    # The `commands` framework attempts a conversion of each type in this Union *in order*.
    # So, it will attempt to convert whatever is passed to `target` to a `nextcord.Member` instance.
    # If that fails, it will attempt to convert it to a `nextcord.TextChannel` instance.
    # See: https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html#typing-union
    # NOTE: If a Union typehint converter fails it will raise `commands.BadUnionArgument`
    # instead of `commands.BadArgument`.

    # To check the resulting type, `isinstance` is used
    if isinstance(target, nextcord.Member):
        await ctx.send('Member found: {}, adding them to the ignore list.'.format(target.mention))
    elif isinstance(target, nextcord.TextChannel):  # this could be n `else` but for completeness' sakea.
        await ctx.send('Channel found: {}, adding it to the ignore list.'.format(target.mention))


@bot.command()
async def bibametr(ctx: commands.Context):
    happy_emoji = '<a:grinning:856976967353499699>'
    sad_emoji = '<a:grimacing:856977482367107132>'
    biba = random.randint(1, 30)
    if biba > 15:
        await ctx.send(str(biba) + ' см ' + happy_emoji)
    else:
        await ctx.send(str(biba) + ' см ' + sad_emoji)


@bot.command(name='гей')
async def gay(ctx: commands.Context):
    gay_emoji = '<a:pleading_face:856979480849416252>'
    not_gay_emoji = '<a:face_with_monocle:856979563497783346>'
    num = random.randint(1, 2)
    if num == 1:
        await ctx.send('Ты гей' + ' ' + gay_emoji)
    else:
        await ctx.send('Ты не гей' + ' ' + not_gay_emoji)


# RickAndMortyAPI
def get_single_character(character_id):
    url = env.RICK_AND_MORTY_URL + 'character/' + character_id
    response = requests.get(url)
    result = response.json()

    result_string = 'Имя: ' + result['name'] + ', ' + 'Статус: ' + result['status'] + ', ' + 'Расса: ' + result[
        'species'] + ', ' + 'Гендер: ' + result['gender']

    return {'result': result_string, 'image_url': result['image']}


@bot.command(name='рикиморти')
async def rickandmorty(ctx: commands.Context, character_id: str):
    embed = nextcord.Embed()
    result = get_single_character(character_id)
    embed.set_image(url=result['image_url'])
    await ctx.send(result['result'], embed=embed)


@bot.command(name='инфо')
async def info(ctx: commands.Context, discord_member: nextcord.Member):
    result = '```Id: ' + str(discord_member.id) + '\n' + 'Дата создания аккаунта: ' + str(
        discord_member.created_at) + '\n' + 'Дата входа в канал: ' + str(
        discord_member.joined_at) + '\n' + 'Имя: ' + str(discord_member.name) + '\n' + 'Ник: ' + str(
        discord_member.nick) + '\n' + 'Роли: ' + str(discord_member.roles) + '\n' + 'Статус: ' + str(
        discord_member.status) + '```' + '\n' + 'Аватар: ' + str(discord_member.avatar_url)

    embed = nextcord.Embed(color=0x8439DD, title='Информация о ' + str(discord_member.name), description=result)

    await ctx.send(embed=embed, delete_after=60)


@bot.command(name='регистрация')
async def register(ctx: commands.Context):
    author = ctx.message.author

    if author.bot:
        await ctx.send('You are a bot')
        raise Exception('Bot asked for registration')

    connection = bd.get_connection()
    cursor = connection.cursor(dictionary=True, buffered=True)

    user = cursor.execute('SELECT * FROM `users` WHERE discord_id = %s', (str(author.id), ))

    if user is None:
        now = datetime.datetime.utcnow()
        sql_to_create_user = f"INSERT INTO `users` (`discord_id`, `coins`, `opened_cases_count`, `is_admin`, `discord_name`) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql_to_create_user, (str(author.id), 0, 0, 0, author.name))
        connection.commit()
        print(sql_to_create_user)
        await ctx.send('Изи пизи, ты зареган <a:grinning:856976842158112788>')
        cursor.close()

    else:
        await ctx.send('Ты уже зареган, нюхай бебру')
        raise Exception('Юзер уже зарегестрирован')


@bot.command(name='кейс')
async def case(ctx: commands.Context, case_id=None):
    author = ctx.message.author

    if check_for_user_registration(author.id) is False:
        return await ctx.send('Ты не зареган')

    if case_id is None:
        await ctx.send('Введите пожалуйста айди кейса:\n\n'
                       '1 - кейс стоимостью 500 коинов\n'
                       '2 - кейс стоимость 1000 коинов\n'
                       '3 - кейс стоимостью 2000 коинов\n'
                       'Пример: !кейс 1\n'
                       '```Чем дороже кейс - тем больше шансов выиграть роль!```')

    case_id = int(case_id)

    if case_id > 3 or case_id < 1:
        await ctx.send('Неверный айди кейса')
        raise Exception('Неверный айди кейса')

    result = False
    case_price = 100000

    if case_id == 1:
        result = check_acc(str(author.id), roles.CASE_1_PRICE)
        case_price = roles.CASE_1_PRICE
    elif case_id == 2:
        result = check_acc(str(author.id), roles.CASE_2_PRICE)
        case_price = roles.CASE_2_PRICE
    elif case_id == 3:
        result = check_acc(str(author.id), roles.CASE_3_PRICE)
        case_price = roles.CASE_3_PRICE

    if result is False:
        await ctx.send(
            'Недостаточно коинов на балансе\n!баланс - проверить баланс')
        raise Exception('Недостаточный баланс - ' + str(author.id))

    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_minus_balance = "UPDATE `users` SET coins = coins - {} WHERE discord_id = {}".format(case_price, author.id)
    cursor.execute(sql_to_minus_balance)
    connection.commit()

    add_cases_count(author.id)

    prize = spin.spin(case_id=case_id)

    await ctx.send(f'**{ctx.message.author.name}:** Достаю кейс со склада...', delete_after=60)
    time.sleep(3)
    await ctx.send(f'**{ctx.message.author.name}:** Открываю кейс...', delete_after=60)
    time.sleep(5)
    await ctx.send(f'**{ctx.message.author.name}:** Достаю подарок', delete_after=60)
    time.sleep(3)

    if prize[0] is None:
        await ctx.send(
            f'**{ctx.message.author.name}: **```К сожалению ты ничего не выиграл```\n <a:pleading_face:857354338812297237>')
        raise Exception('Игрок ничего не выиграл - ' + str(author.id))
    else:
        await ctx.send('```Вы выиграли роль - ' + roles.ROLES_NAME[prize[0]] + '```')
        role = nextcord.utils.get(ctx.message.guild.roles, id=int(prize[0]))
        await author.add_roles(role)


@bot.command(name="сколькокейсов")
async def check_opened_cases_count_for_user(ctx: commands.Context):
    author = ctx.message.author

    if check_for_user_registration(author.id) is False:
        await ctx.send('Ты не зареган')

    await ctx.send('Вы открыли - ' + opened_cases_count(author.id) + ' кейсов')


def add_cases_count(discord_id):
    discord_id = int(discord_id)
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True)
    sql_request = f"UPDATE `users` SET opened_cases_count = opened_cases_count + 1 WHERE discord_id = {discord_id}"
    cursor.execute(sql_request)
    connection.commit()
    connection.close()


def opened_cases_count(discord_id):
    discord_id = int(discord_id)
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_request = f"SELECT opened_cases_count FROM `users` WHERE discord_id = {discord_id}"
    cursor.execute(sql_request)

    cases_count = cursor.fetchone()

    return str(cases_count['opened_cases_count'])


def check_acc(user_id: str, balance: int):
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_check_registered = "SELECT * FROM `users` WHERE discord_id = {}".format(int(user_id))
    cursor.execute(sql_to_check_registered)

    user = cursor.fetchone()

    if user is None:
        return False

    if user['coins'] >= balance:
        return True
    else:
        return False


@bot.command(name='баланс')
async def balance(ctx: commands.Context):
    author = ctx.message.author

    if check_for_user_registration(author.id) is False:
        return await ctx.send('Ты не зареган')

    connection = bd.get_connection()
    cursor = connection.cursor()
    sql_to_check_user_balance = "SELECT coins FROM users WHERE discord_id = {}".format(author.id)
    cursor.execute(sql_to_check_user_balance)
    coins = cursor.fetchone()
    embed = nextcord.Embed(color=0x4ad420, title=f'Баланс {ctx.message.author.name}',
                          description='**' + str(coins[0]) + ' коинов**')
    return await ctx.send(embed=embed)


@bot.command()
async def help(ctx):
    print('Command was called')
    embed = nextcord.Embed(color=0x17cf45, title='Помощь', description=myconst.USER_HELP)

    if check_for_admin(str(ctx.message.author.id)) == 1:
        moderator_embed = nextcord.Embed(color=0x17cf45, title="Помощь для модераторов", description=myconst.MODERATOR_HELP)
        await ctx.message.author.send(embed=moderator_embed)

    await ctx.send(embed=embed)


@bot.command(name="кацапы")
async def kazapi(ctx: commands.Context):
    embed = nextcord.Embed(color=0xCC0000, title='Дохлые кацапы', description=myconst.KAZAPI)

    return await ctx.send(embed=embed)


@bot.command(name='пример')
async def primer(ctx: commands.Context):
    author = ctx.message.author

    if check_for_user_registration(author.id) is False:
        return await ctx.send('Ты не зареган')

    my_number = random.randint(1, 100)

    math_example = mathem.generate_math_example(my_number)
    await ctx.send(str(math_example) + '\n\nРеши меньше чем за 30сек')

    try:
        answer = await bot.wait_for("message", timeout=30)
        answer = answer.content
    except TimeoutError:
        return await ctx.send('Время вышло, ты облажался')

    if int(answer) == int(my_number):
        connection = bd.get_connection()
        cursor = connection.cursor()
        sql_to_give_coins_for_math_answer = f"UPDATE users SET coins = coins + 20 WHERE discord_id = {author.id}"
        cursor.execute(sql_to_give_coins_for_math_answer)
        connection.commit()
        cursor.close()
        return await ctx.send('Все верно! Я начислил тебе 20 коинов')
    else:
        return await ctx.send('Неверно')


@bot.command(name='угадайчисло')
async def random_number(ctx: commands.Context):
    author = ctx.message.author

    if check_for_user_registration(author.id) is False:
        return await ctx.send('Ты не зареган')

    number = random.randint(1, 10)

    await ctx.send('Угадай число от 1 до 10, которое я загадал, у тебя есть 10 секунд')

    try:
        answer = await bot.wait_for("message", timeout=10)
        answer = answer.content
    except TimeoutError:
        return await ctx.send('Время вышло')

    if int(answer) == int(number):
        connection = bd.get_connection()
        cursor = connection.cursor()
        sql_to_give_coins_for_math_answer = f"UPDATE users SET coins = coins + 150 WHERE discord_id = {author.id}"
        cursor.execute(sql_to_give_coins_for_math_answer)
        connection.commit()
        cursor.close()
        return await ctx.send('Ты угадал! Я начислил тебе 150 коинов')
    else:
        return await ctx.send('Ты не угадал')


@bot.command(name="выдатькоины")
async def admin_give_coins(ctx: commands.Context, member: nextcord.Member, coins_count):
    coins_count = int(coins_count)
    author = ctx.message.author

    if check_for_admin(str(author.id)) != 1:
        return await ctx.send('Ты не администратор бота')

    result = {'is_admin': True}

    if result['is_admin'] is True:
        connection = bd.get_connection()
        cursor = connection.cursor(buffered=True, dictionary=True)
        sql_to_give_coins_by_admin = f'UPDATE users SET coins = coins + {coins_count} WHERE discord_id = {member.id}'
        cursor.execute(sql_to_give_coins_by_admin)
        connection.commit()
        return await ctx.send('Коины успешно зачислены', delete_after=10)


@bot.command(name="забратькоины")
async def admin_drop_coins(ctx: commands.Context, member: nextcord.Member, coins_count):
    coins_count = int(coins_count)
    author = ctx.message.author
    if str(author.id) == '345526389665038336':
        result = {'is_admin': True}
    else:
        return None

    if result['is_admin'] is True:
        connection = bd.get_connection()
        cursor = connection.cursor(buffered=True, dictionary=True)
        sql_to_drop_coins_by_admin = f"UPDATE users SET coins = coins - {coins_count} WHERE discord_id = {member.id}"
        cursor.execute(sql_to_drop_coins_by_admin)
        connection.commit()
        return await ctx.send('Коины успешно спизжены, поздравляю, вы ЕБУЧИЙ СКАМЕР', delete_after=360)


@bot.command(name="проверитьбаланс")
async def admin_get_user_balance(ctx: commands.Context, member: nextcord.Member):
    author = ctx.message.author
    if str(author.id) == '297650152691204096' or str(author.id) == '345526389665038336':
        result = {'is_admin': True}
    else:
        return None

    if result['is_admin'] is True:
        connection = bd.get_connection()
        cursor = connection.cursor(buffered=True, dictionary=True)
        sql_to_get_user_balance_by_admin = f"SELECT coins FROM `users` WHERE discord_id = {member.id}"
        cursor.execute(sql_to_get_user_balance_by_admin)
        result = cursor.fetchone()['coins']
        return await ctx.send(str(result))


@bot.command(name="юзеры")
async def check_users_count_on_server(ctx: commands.Context):
    await ctx.send(ctx.message.guild.member_count)


@bot.command(name="премиум")
async def check_premium_users_count(ctx: commands.Context):
    await ctx.send(ctx.message.guild.premium_subscription_count)


@bot.command(name="имя")
async def check_user_name_by_discord_id(ctx: commands.Context, discord_id):
    users = ctx.message.guild.members
    for user in users:
        if str(user.id) == str(discord_id):
            user_name = str(user.name)
            user_nick = str(user.nick)
            result = f"{user_name} ({user_nick})"
            await ctx.send(result)


@bot.command(name="faceit")
async def check_faceit_stat(ctx: commands.Context, nickname):
    nickname = str(nickname)
    result = work_with_api.get_faceit_stat_by_nicknsame(nickname=nickname)

    await ctx.send('```'
                   f'Ник - {result["nickname"]}\n'
                   f'Афк - {result["infractions"]["afk"]}\n'
                   f'Выходил - {result["infractions"]["leaver"]}\n'
                   f'Уровень - {result["games"]["csgo"]["skill_level_label"]}\n'
                   f'Эло - {result["games"]["csgo"]["faceit_elo"]}\n'
                   f'Тип подписки - {result["membership_type"]}```')


@bot.command(name="дуэль")
async def duel(ctx: commands.Context, member: nextcord.Member, coins_count):
    author_id = ctx.message.author.id

    if check_for_user_registration(author_id) is False:
        return await ctx.send('Ты не зареган')

    coins_count = int(coins_count)
    if coins_count == 0 or coins_count < 1:
        return await ctx.send('ТЫ ЧЕ НАХУЙ ДЕЛАЕШЬ ПИДАРАС ?')
    called_author_id = member.id

    answer = ''

    while answer == '':
        p_result = ''
        try:
            await ctx.send('Ожидаем ответа от ' + str(member.name))
            p_result = await bot.wait_for("message", timeout=25)
        except TimeoutError:
            return await ctx.send('Время вышло, соперник не ответил')

        if (str(p_result.content) == 'да' or str(p_result.content) == 'Да') and str(p_result.author.id) == str(member.id):
            answer = p_result
            await ctx.send('Начинаем!')

    # try:
    #     await ctx.send('Ожидаем ответа от ' + str(member.name))
    #     answer = await bot.wait_for("message", timeout=25)
    # except TimeoutError:
    #     await ctx.send('Время вышло, соперник не ответил')
    #
    # if (str(answer.content) == 'да' or str(answer.content) == 'Да') and str(answer.author.id) == str(member.id):
    #     await ctx.send('Начинаем!')
    # else:
    #     return await ctx.send('Ответил кто-то другой')

    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_check_author_balance = f"SELECT coins FROM `users` WHERE discord_id = {author_id}"
    cursor.execute(sql_to_check_author_balance)
    author_balance = cursor.fetchone()['coins']
    connection.close()

    if int(author_balance) < coins_count:
        return await ctx.send("У вас недостаточно баланса")

    connection.connect()
    sql_to_check_called_author_balance = f"SELECT coins FROM `users` WHERE discord_id = {called_author_id}"
    cursor.execute(sql_to_check_called_author_balance)
    called_author_balance = cursor.fetchone()['coins']

    if called_author_balance < coins_count:
        return await ctx.send('У вызываемого юзера недостаточно баланса')

    connection.close()

    author_random_int = random.randint(1, 100)
    await ctx.send(str(ctx.message.author.name) + ' выбил число ' + str(author_random_int))

    time.sleep(3)

    called_author_random_int = random.randint(1, 100)
    await ctx.send(str(member.name) + ' выбил число ' + str(called_author_random_int))

    if author_random_int > called_author_random_int:
        connection.connect()
        sql_to_add_coins_to_author = f"UPDATE `users` SET coins = coins + {coins_count} WHERE discord_id = {author_id}"
        sql_to_drop_coins_from_called_author = f"UPDATE `users` SET coins = coins - {coins_count} WHERE discord_id = {called_author_id}"
        cursor.execute(sql_to_add_coins_to_author)
        cursor.execute(sql_to_drop_coins_from_called_author)
        connection.commit()
        connection.close()
        return await ctx.send('Победил ' + ctx.message.author.name + '!')
    elif author_random_int < called_author_random_int:
        connection.connect()
        sql_to_drop_coins_from_author = f"UPDATE `users` SET coins = coins - {coins_count} WHERE discord_id = {author_id}"
        sql_to_add_coins_to_called_author = f"UPDATE `users` SET coins = coins + {coins_count} WHERE discord_id = {called_author_id}"
        cursor.execute(sql_to_drop_coins_from_author)
        cursor.execute(sql_to_add_coins_to_called_author)
        connection.commit()
        connection.close()
        return await ctx.send('Победил ' + member.name + '!')
    elif author_random_int == called_author_random_int:
        return await ctx.send('Ничья!')


@bot.command(name="розыграть")
async def start_event(ctx: commands.Context):
    return await ctx.send('Тест') #TODO: сделать команду розыгрыша


@bot.command(name="777")
async def casino_play(ctx: commands.Context, color: str, coins_count):
    if check_for_user_registration(ctx.message.author.id) is False:
        return await ctx.send('Ты не зареган')

    color = color.lower()
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_check_author_balance = f"SELECT coins FROM `users` WHERE discord_id = {ctx.message.author.id}"
    cursor.execute(sql_to_check_author_balance)
    author_balance = cursor.fetchone()['coins']
    connection.close()
    coins_count = int(coins_count)
    if coins_count == 0 or coins_count < 1:
        return await ctx.send('ПИДАРАС ТЫ ЧЕ НАХУЙ ДЕЛАЕШЬ ?', delete_after=30)

    if int(author_balance) < int(coins_count):
        return await ctx.send('Недостаточно коинов')

    if color != 'зеленый' and color != 'красный' and color != 'черный':
        return await ctx.send('Неверный цвет')

    color_array = ["красный", "черный", "зеленый"]

    random_color = random.choices(color_array, [80, 50, 10])[0]

    if random_color == 'красный':
        embed = nextcord.Embed(color=0xCC0000, title='Зеленский Casino', description='Кручу колесо')
        embed.set_image(url='https://cdn.discordapp.com/attachments/345528162668511242/858744572737224724/red.gif')
        await ctx.send(embed=embed, delete_after=20)
    elif random_color == 'черный':
        if random_color == color:
            coins_count = coins_count * 2
        embed = nextcord.Embed(color=0x000000, title='Зеленский Casino', description='Кручу колесо')
        embed.set_image(url='https://cdn.discordapp.com/attachments/345528162668511242/858743759184068678/black.gif')
        await ctx.send(embed=embed, delete_after=20)
    elif random_color == 'зеленый':
        if random_color == color:
            coins_count = coins_count * 5
        embed = nextcord.Embed(color=0x38761D, title='Зеленский Casino', description='Кручу колесо')
        embed.set_image(
            url='https://cdn.discordapp.com/attachments/345528162668511242/858743281105633290/87802a4cb981ea58.gif')
        await ctx.send(embed=embed, delete_after=20)

    time.sleep(5)

    await ctx.send(f"Выпал {random_color} цвет")

    time.sleep(2)

    if str(random_color) == color:
        connection.connect()
        sql_to_add_casino_coins = f"UPDATE `users` SET coins = coins + {coins_count} WHERE discord_id = {ctx.message.author.id}"
        cursor.execute(sql_to_add_casino_coins)
        connection.commit()
        connection.close()
        return await ctx.send('Ты победил! Я начислил тебе коины')
    else:
        connection.connect()
        sql_to_drop_casino_coins = f"UPDATE `users` SET coins = coins - {coins_count} WHERE discord_id = {ctx.message.author.id}"
        cursor.execute(sql_to_drop_casino_coins)
        connection.commit()
        connection.close()
        return await ctx.send('Ты проиграл, я забрал у тебя коины!')


def check_for_user_registration(user_id):
    user_id = str(user_id)
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_check_user_registration = f'SELECT * FROM `users` WHERE discord_id = {user_id}'
    cursor.execute(sql_to_check_user_registration)
    result = cursor.fetchone()
    connection.close()

    if result is None:
        return False
    else:
        return True


@bot.command(name="гоиграть")
async def go_in_game_cmd(ctx: commands.Context, game: str):
    if check_for_admin(str(ctx.message.author.id)) != 1:
        return await ctx.send('Ты не администратор бота')

    server_members = ctx.guild.members
    message_to_sent = f'Мощные типочки в {ctx.message.guild.name} идут в {game}, и набирают команду!'
    await ctx.send('Зову. Ожидайте...')
    for server_member in server_members:
        try:
            await server_member.send(message_to_sent, delete_after=1800)
            print(f"Sent user a DM to {server_member.id}")
        except Exception as e:
            print(f"Couldn't send DM, bcs: {e}")

    return await ctx.send('Позвал')


def check_for_admin(user_id: str):
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_check_for_admin = f"SELECT is_admin FROM `users` WHERE discord_id = {user_id}"
    cursor.execute(sql_to_check_for_admin)
    result = cursor.fetchone()
    connection.close()

    if result is None:
        return 0

    return int(result['is_admin'])


@bot.command(name="выдатьадминку")
async def set_an_admin(ctx: commands.Context, member: nextcord.Member):
    author = ctx.message.author
    if str(author.id) == '345526389665038336':
        print(f'{author.id} выдал админку {member.id}')
    else:
        return None

    print(author.id)

    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_set_user_as_admin = f"UPDATE `users` SET is_admin = %s WHERE discord_id = %s"
    cursor.execute(sql_to_set_user_as_admin, (1, member.id))
    connection.commit()
    return await ctx.send('Выдано')


@bot.command(name="забратьадминку")
async def unset_an_admin(ctx: commands.Context, member: nextcord.Member):
    author = ctx.message.author
    if str(author.id) == '345526389665038336':
        print('Допущен')
    else:
        return None

    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_set_user_as_admin = f"UPDATE `users` SET is_admin = 0 WHERE discord_id = {member.id}"
    cursor.execute(sql_to_set_user_as_admin)
    connection.commit()
    connection.close()
    return await ctx.send('Спиздил')


@bot.command(name="зарегатьрефералку")
async def referal_code_registration(ctx: commands.Context, referal_code: str):
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True)

    sql_to_check_referal_code = f"SELECT referal_code FROM `users`"
    cursor.execute(sql_to_check_referal_code)
    result = cursor.fetchone()
    connection.close()

    for item in result:
        if item == referal_code:
            return await ctx.send('Данный промокод уже зарегестрирован')

    connection.connect()
    sql_to_add_referal = f"UPDATE `users` SET referal_code = %s WHERE discord_id = %s"
    cursor.execute(sql_to_add_referal, (referal_code, ctx.message.author.id))
    connection.commit()
    connection.close()

    return await ctx.message.author.send(f"Ваш реферальный код - {referal_code} успешно зарегестрирован!")


@bot.command(name="реферал")
async def use_referal_code(ctx: commands.Context, referal_code: str):
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_check_referal = f"SELECT discord_id FROM `users` WHERE referal_code = {referal_code}"
    cursor.execute(sql_to_check_referal)
    result = cursor.fetchone()
    connection.close()
    if result['discord_id'] is None:
        return await ctx.send('Не нашел такого промокода')

    sql_to_add_coins_for_referal = f"UPDATE `users` SET coins = coins + 500 WHERE discord_id = {result['discord_id']}"
    connection.connect()
    cursor.execute(sql_to_add_coins_for_referal)
    connection.commit()
    connection.close()

    return await ctx.send('Ок')


@bot.event
async def on_ready():
    print('Bot is ready')
    global tdict
    tdict = {}
    # await bot.change_presence(activity=nextcord.Activity(type=nextcord.ActivityType.competing, name='Purple Сhat'))


@bot.event
async def on_voice_state_update(member, before, after):
    author = member.id
    if before.channel is None and after.channel is not None:
        t1 = time.time()
        tdict[author] = t1
    elif before.channel is not None and after.channel is None and author in tdict:
        t2 = time.time()
        result = t2 - tdict[author]
        coins_plus = int(int(result) / 15)
        result_in_hours = round(result / 60, 1)
        connection = bd.get_connection()
        cursor = connection.cursor(buffered=True, dictionary=True)
        sql_to_add_coins_count = f"UPDATE `users` SET coins = coins + {coins_plus} WHERE discord_id = {author}"
        cursor.execute(sql_to_add_coins_count)
        connection.commit()
        connection.close()
        await member.send(f'Ты провел в голосовом канале {result_in_hours} минут, тебе начислено {coins_plus} коинов')


@bot.command(name='лидеры')
async def table_of_the_leaders(ctx: commands.Context):
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_get_leaders = f"SELECT * FROM `users` ORDER BY coins DESC LIMIT 10"
    cursor.execute(sql_to_get_leaders)
    result = cursor.fetchall()
    conf = ''
    for item in result:
        conf += f'**Имя:** {item["discord_name"]}\n**Коины:** {item["coins"]}\n**Открытых кейсов:** {item["opened_cases_count"]}\n\n----\n\n'

    embed = nextcord.Embed(color=0x21f00e, title="Таблица лидеров", description=conf)

    return await ctx.send(embed=embed)


@bot.command(name="место")
async def get_user_place_in_leader_board(ctx: commands.Context):
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_get_user_place_in_leader_board = f"SELECT discord_id FROM `users` ORDER BY coins DESC"
    cursor.execute(sql_to_get_user_place_in_leader_board)
    result = cursor.fetchall()

    i = 0
    for item in result:
        i = i + 1
        if str(item['discord_id']) == str(ctx.message.author.id):
            embed = nextcord.Embed(color=0x21f00e, title="Ваше место", description=f'{i}')
            return await ctx.send(embed=embed)


@bot.command(name="обновитьимя")
async def update_user_discord_name(ctx: commands.Context):
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_update_nick_name = f"UPDATE `users` SET discord_name = %s WHERE discord_id = %s"
    cursor.execute(sql_to_update_nick_name, (ctx.message.author.name, ctx.message.author.id))
    connection.commit()
    connection.close()

    return await ctx.send('Обновлено')


bot.run(env.TOKEN)
