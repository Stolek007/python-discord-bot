# Логика для начисления поинтов

import bd

connection = bd.get_connection()
cursor = connection.cursor(dictionary=True)
sql = "SELECT * FROM users"
cursor.execute(sql)
users = cursor.fetchone()
print(users['discord_id'])
