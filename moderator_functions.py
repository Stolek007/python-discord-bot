# from typing import Optional
#
# from discord.ext import commands
# import discord
# import index
# import bd
#
# logs_channel = index.bot.get_channel(981167386487054355)
#
# async def ban_user(ctx: commands.Context, member: Optional[discord.Member], time_to_ban: None, reason: None):
#     if time_to_ban is None or reason is None or member is None:
#         return await ctx.send('?ban <@пользователь> <дни_бана> <причина>')
#
#     if check_for_admin(str(ctx.message.author.id)) == 0:
#         return await ctx.send('Ты не мой модератор')
#
#     if member == ctx.message.author:
#         return await ctx.send('Невозможно забанить самого себя')
#
#     if check_for_admin(member.id) == 0:
#         await member.send(f'Вы были забанены администратором - {ctx.message.author.name}')
#         await discord.Guild.ban(self=ctx.message.author.guild, user=member, reason=reason,
#                                 delete_message_days=int(time_to_ban))
#
#
#
#
# async def unban_user(ctx: commands.Context, member: Optional[discord.Member]):
#     if member is None:
#         return await ctx.send('?unban <@пользователь>')
#
#
# async def mute_user():
#
#
#
#
# async def unmute_user():
#
#
#
# def check_for_user_mute():
#
#
#
# async def clear():
#
#
#
# async def set_admin():
#
#
#
# async def unset_admin():
#
#
#
# def check_for_admin(user_id: str):
#     connection = bd.get_connection()
#     cursor = connection.cursor(buffered=True, dictionary=True)
#     sql_to_check_for_admin = f"SELECT is_admin FROM `users` WHERE discord_id = {user_id}"
#     cursor.execute(sql_to_check_for_admin)
#     result = cursor.fetchone()
#     connection.close()
#
#     if result is None:
#         return 0
#
#     return int(result['is_admin'])