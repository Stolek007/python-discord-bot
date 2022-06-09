import interactions
import nextcord
import bd
import datetime
import block_functions
import roles
import spin
import time
import random
import myconst
import env
import requests


# >>> case
class SelectDropdown(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(
                label="Кейс 1 - 500 коинов", emoji="🟦", value="1"
            ),
            nextcord.SelectOption(
                label="Кейс 2 - 1000 коинов", emoji="🟩", value="2"
            ),
            nextcord.SelectOption(
                label="Кейс 3 - 2000 коинов", emoji="🟥", value="3"
            )
        ]

        super().__init__(
            placeholder="Выберите кейс, который хотите открыть",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: nextcord.Interaction):
        author = interaction.user

        if block_functions.check_for_user_registration(author.id) is False:
            return await interaction.response.send_message('Ты не зареган')

        case_id = int(self.values[0])

        result = False
        case_price = 100000

        if case_id == 1:
            result = block_functions.check_if_user_has_money(str(author.id), roles.CASE_1_PRICE)
            case_price = roles.CASE_1_PRICE
        elif case_id == 2:
            result = block_functions.check_if_user_has_money(str(author.id), roles.CASE_2_PRICE)
            case_price = roles.CASE_2_PRICE
        elif case_id == 3:
            result = block_functions.check_if_user_has_money(str(author.id), roles.CASE_3_PRICE)
            case_price = roles.CASE_3_PRICE

        if result is False:
            await interaction.send(
                'Недостаточно коинов на балансе\n!баланс - проверить баланс', ephemeral=True)
            raise Exception('Недостаточный баланс - ' + str(author.id))

        connection = bd.get_connection()
        cursor = connection.cursor(buffered=True, dictionary=True)
        sql_to_minus_balance = "UPDATE `users` SET coins = coins - {} WHERE discord_id = {}".format(case_price,
                                                                                                    author.id)
        cursor.execute(sql_to_minus_balance)
        connection.commit()

        block_functions.add_cases_count(author.id)

        prize = spin.spin(case_id=case_id)

        await interaction.send(f'**{interaction.user.name}:** Достаю кейс со склада...', delete_after=60,
                               ephemeral=True)
        time.sleep(3)
        await interaction.send(f'**{interaction.user.name}:** Открываю кейс...', delete_after=60, ephemeral=True)
        time.sleep(5)
        await interaction.send(f'**{interaction.user.name}:** Достаю подарок', delete_after=60, ephemeral=True)
        time.sleep(3)

        if prize[0] is None:
            await interaction.send(
                f'**{interaction.user.name}: **```К сожалению ты ничего не выиграл```\n <a:pleading_face:857354338812297237>')
            raise Exception('Игрок ничего не выиграл - ' + str(author.id))
        else:
            await interaction.send('```Вы выиграли роль - ' + roles.ROLES_NAME[prize[0]] + '```')
            role = interaction.guild.get_role(int(prize[0]))
            await author.add_roles(role)

        await interaction.response.send_message(f"Вы выбрали открыть кейс - {self.values[0]}")


class CaseDropdownView(nextcord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(SelectDropdown())


# <<< case


# >>> casino

class Casino(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            "Казино",
            timeout=5 * 60,
        )

        self.bet = nextcord.ui.TextInput(
            label="Ставка",
            min_length=2,
            max_length=50,
            required=True,
        )
        self.add_item(self.bet)

        self.color = nextcord.ui.TextInput(
            label="Цвет (красный/черный/зеленый)",
            min_length=6,
            max_length=7,
            required=True,
        )

        self.add_item(self.color)

        # option1 = nextcord.SelectOption(
        #     label="Красный",
        #     emoji="🟥",
        #     value="красный",
        # )
        #
        # option2 = nextcord.SelectOption(
        #     label="Зеленый",
        #     emoji="🟩",
        #     value="зеленый",
        # )
        #
        # option3 = nextcord.SelectOption(
        #     label="Черный",
        #     emoji="⬛",
        #     value="черный",
        #
        # )
        #
        # self.select = nextcord.ui.Select(
        #     options=[option1, option2, option3],
        #     min_values=1,
        #     max_values=1,
        #     placeholder="Выберите цвет, на который хотите поставить"
        # )
        #
        # self.add_item(self.select)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await block_functions.validate_registration(interaction)

        # print(self.select.options) #TODO: Fix
        # print(self.select.values)
        # color = self.select.values[0]
        coins_count = self.bet.value
        color = self.color.value.lower()
        connection = bd.get_connection()
        cursor = connection.cursor(buffered=True, dictionary=True)
        sql_to_check_author_balance = f"SELECT coins FROM `users` WHERE discord_id = {interaction.user.id}"
        cursor.execute(sql_to_check_author_balance)
        author_balance = cursor.fetchone()['coins']
        connection.close()
        coins_count = int(coins_count)
        if coins_count == 0 or coins_count < 1:
            await interaction.send('ПИДАРАС ТЫ ЧЕ НАХУЙ ДЕЛАЕШЬ ?', delete_after=30, ephemeral=True)
            raise Exception('b')

        if int(author_balance) < int(coins_count):
            await interaction.send('Недостаточно коинов', ephemeral=True)
            raise Exception('b')

        if color != 'зеленый' and color != 'красный' and color != 'черный':
            await interaction.send('Неверный цвет', ephemeral=True)
            raise Exception('b')

        color_array = ["красный", "черный", "зеленый"]

        random_color = random.choices(color_array, [80, 50, 10])[0]

        if random_color == 'красный':
            embed = nextcord.Embed(color=0xCC0000, title='Зеленский Casino', description='Кручу колесо')
            embed.set_image(url='https://cdn.discordapp.com/attachments/345528162668511242/858744572737224724/red.gif')
            await interaction.send(embed=embed, delete_after=20, ephemeral=True)
        elif random_color == 'черный':
            if random_color == color:
                coins_count = coins_count * 2
            embed = nextcord.Embed(color=0x000000, title='Зеленский Casino', description='Кручу колесо')
            embed.set_image(
                url='https://cdn.discordapp.com/attachments/345528162668511242/858743759184068678/black.gif')
            await interaction.send(embed=embed, delete_after=20, ephemeral=True)
        elif random_color == 'зеленый':
            if random_color == color:
                coins_count = coins_count * 5
            embed = nextcord.Embed(color=0x38761D, title='Зеленский Casino', description='Кручу колесо')
            embed.set_image(
                url='https://cdn.discordapp.com/attachments/345528162668511242/858743281105633290/87802a4cb981ea58.gif')
            await interaction.send(embed=embed, delete_after=20, ephemeral=True)

        time.sleep(5)

        await interaction.send(f"Выпал {random_color} цвет")

        time.sleep(2)

        if str(random_color) == color:
            connection.connect()
            sql_to_add_casino_coins = f"UPDATE `users` SET coins = coins + {coins_count} WHERE discord_id = {interaction.user.id}"
            cursor.execute(sql_to_add_casino_coins)
            connection.commit()
            connection.close()
            await interaction.send('Ты победил! Я начислил тебе коины')
        else:
            connection.connect()
            sql_to_drop_casino_coins = f"UPDATE `users` SET coins = coins - {coins_count} WHERE discord_id = {interaction.user.id}"
            cursor.execute(sql_to_drop_casino_coins)
            connection.commit()
            connection.close()
            await interaction.send('Ты проиграл, я забрал у тебя коины!')


# <<< casino


# >>> creator

async def creator(interaction: nextcord.Interaction):
    await block_functions.validate_registration(interaction)

    embed = nextcord.Embed(color=0x28fc64, title="Создатель", description=myconst.CREATOR)
    return await interaction.send(embed=embed, ephemeral=True)


# <<< creator


# >>> bibametr

async def bibametr(interaction: nextcord.Interaction):
    happy_emoji = '<a:grinning:856976967353499699>'
    sad_emoji = '<a:grimacing:856977482367107132>'
    biba = random.randint(1, 30)
    if biba > 15:
        await interaction.send(str(biba) + ' см ' + happy_emoji)
    else:
        await interaction.send(str(biba) + ' см ' + sad_emoji)


# <<< bibametr


# >>> gay

async def gay(interaction: nextcord.Interaction):
    gay_emoji = '<a:pleading_face:856979480849416252>'
    not_gay_emoji = '<a:face_with_monocle:856979563497783346>'
    num = random.randint(1, 2)
    if num == 1:
        await interaction.send('Ты гей' + ' ' + gay_emoji)
    else:
        await interaction.send('Ты не гей' + ' ' + not_gay_emoji)


# <<< gay


# >>> rickandmorty

async def rickandmorty(
        interaction: nextcord.Interaction,
        character_id):
    embed = nextcord.Embed()
    result = get_single_character(character_id)
    embed.set_image(url=result['image_url'])
    await interaction.send(result['result'], embed=embed)


def get_single_character(character_id):
    url = env.RICK_AND_MORTY_URL + 'character/' + character_id
    response = requests.get(url)
    result = response.json()

    result_string = 'Имя: ' + result['name'] + ', ' + 'Статус: ' + result['status'] + ', ' + 'Расса: ' + result[
        'species'] + ', ' + 'Гендер: ' + result['gender']

    return {'result': result_string, 'image_url': result['image']}

# <<< rickandmorty


# >>> cases

async def cases(interaction: nextcord.Interaction):
    author = interaction.user

    if block_functions.check_for_user_registration(author.id) is False:
        await interaction.send('Ты не зареган', ephemeral=True)

    await interaction.send('Вы открыли - ' + opened_cases_count(author.id) + ' кейсов')


def opened_cases_count(discord_id):
    discord_id = int(discord_id)
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_request = f"SELECT opened_cases_count FROM `users` WHERE discord_id = {discord_id}"
    cursor.execute(sql_request)

    cases_count = cursor.fetchone()

    cursor.close()
    connection.close()

    return str(cases_count['opened_cases_count'])
# <<< cases
