import nextcord
import bd
import datetime
import block_functions
import time
import random


# <<< giveaway

class Giveaway(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            "Розыгрыш",
            timeout=5 * 60,
        )

        self.tokenCounts = nextcord.ui.TextInput(
            label="Укажите размер розыгрыша",
            min_length=1,
            max_length=5,
            required=True,
        )
        self.add_item(self.tokenCounts)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        coins_count = self.tokenCounts.value

        if block_functions.check_for_admin(str(interaction.user.id)) == 1:
            await interaction.response.send_message(f'Розыгрываем {coins_count} коинов')
        else:
            await interaction.send('У вас нет доступа ?', ephemeral=True)
            raise Exception('ю')

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

        await interaction.send(embed=embed)

        time.sleep(5)

        embed = nextcord.Embed(color=0x702687, title="Победитель!",
                               description=f'Победил: <@' + random_user["discord_id"] + '>')

        connection.connect()
        sql_to_add_user_coins = f"UPDATE `users` SET coins = coins + %s WHERE discord_id = %s"
        cursor.execute(sql_to_add_user_coins, (int(coins_count), random_user["discord_id"]))
        connection.commit()
        connection.close()

        await interaction.send(embed=embed)

# >>> giveaway
