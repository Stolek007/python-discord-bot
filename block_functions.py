import nextcord
import bd
import datetime
import time


# >>> registration

class Registration(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            "Регистрация",
            timeout=2 * 60,
        )

        self.name = nextcord.ui.TextInput(
            label="Ник, для регистрации в боте",
            min_length=2,
            max_length=50,
            required=True,
        )

        self.add_item(self.name)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        author = interaction.user

        if author.bot:
            await interaction.send('Ты бот, я не могу тебя зарегать')
            raise Exception('Bot asked for registration')

        connection = bd.get_connection()
        cursor = connection.cursor(dictionary=True, buffered=True)

        user = cursor.execute('SELECT * FROM `users` WHERE discord_id = %s', (str(author.id),))

        if check_for_user_registration(str(author.id)) is False:
            now = datetime.datetime.utcnow()
            sql_to_create_user = f"INSERT INTO `users` (`discord_id`, `coins`, `opened_cases_count`, `is_admin`, `discord_name`) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql_to_create_user, (str(author.id), 0, 0, 0, self.name.value))
            connection.commit()
            cursor.close()
        else:
            await interaction.send('Я тебя помню, ты уже зареган', ephemeral=True)
            raise Exception('Юзер уже зареган')

        response = f'Я запомнил тебя под именем - {self.name.value}. Приятного пользования <a:grinning:856976842158112788>'
        await interaction.send(response, ephemeral=True)


# <<< registration


# <<< help

class HelpButtonView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @nextcord.ui.button(label="Зарегистрироваться", style=nextcord.ButtonStyle.green)
    async def registration_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        modal = Registration()
        await interaction.response.send_modal(modal)


# >>> help


# >>> balance
async def balance(ctx):
    if check_for_user_registration(str(ctx.user.id)) is False:
        return await ctx.send('Ты не зареган - /help')

    connection = bd.get_connection()
    cursor = connection.cursor()
    sql_to_check_user_balance = "SELECT coins FROM users WHERE discord_id = {}".format(ctx.user.id)
    cursor.execute(sql_to_check_user_balance)
    coins = cursor.fetchone()
    embed = nextcord.Embed(color=0x4ad420, title=f'Баланс {ctx.user.name}',
                           description='**' + str(coins[0]) + ' коинов**')
    return await ctx.send(embed=embed)


# <<< balance


# >>> pay
async def pay(interaction, member, coins_to_pay):
    current_coins_count = int(coins_to_pay)

    sql_to_check_valid_coins = f"SELECT coins FROM `users` WHERE discord_id = {interaction.user.id}"
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
        return await interaction.send('Недостаточно баланса для перевода (комиссия = 10 коинов)', ephemeral=True)

    connection.connect()
    cursor.execute(sql_to_add_coins, (current_coins_count, member.id))
    cursor.execute(sql_to_drop_coins, (current_coins_count + 10, interaction.user.id))
    connection.commit()
    connection.close()

    embed = nextcord.Embed(color=0x28fc64, title='Перевод коинов',
                           description='Перевод успешно выполнен. Коммисия за перевод - **10 коинов**')

    return await interaction.send(embed=embed, ephemeral=True)


# <<< pay

# >>> update

class UpdateName(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            "Изменение имени",
            timeout=5 * 60,
        )

        self.name = nextcord.ui.TextInput(
            label="Твой новый ник",
            min_length=2,
            max_length=50,
        )
        self.add_item(self.name)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        author = interaction.user

        if check_for_user_registration(author.id) is False:
            return await interaction.response.send_message('Ты не зареган')

        connection = bd.get_connection()
        cursor = connection.cursor(buffered=True, dictionary=True)
        cursor.execute("UPDATE `users` SET discord_name = %s WHERE discord_id = %s",
                       (self.name.value, str(interaction.user.id)))
        connection.commit()
        cursor.close()
        connection.close()

        await interaction.send(f"Ваше имя изменено на {self.name.value}", ephemeral=True)


# <<< update

# Block functions
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


def check_if_user_has_money(user_id: str, bal: int):
    connection = bd.get_connection()
    cursor = connection.cursor(buffered=True, dictionary=True)
    sql_to_check_registered = "SELECT * FROM `users` WHERE discord_id = {}".format(int(user_id))
    cursor.execute(sql_to_check_registered)

    user = cursor.fetchone()

    if user is None:
        return False

    if user['coins'] >= bal:
        return True
    else:
        return False


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


async def validate_registration(interaction: nextcord.Interaction):
    if check_for_user_registration(interaction.user.id) is False:
        await interaction.send('Необходима регистрация - /help')
        raise Exception()
