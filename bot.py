import discord
from discord.ext import commands
import sqlite3
import time
import asyncio
import colorama
from colorama import Fore, Back, Style
colorama.init()

db = sqlite3.connect('ssp_stats\\ssp_stats.db')
sql = db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS stats(user BIGINT, wins BIGINT, loses BIGINT, games BIGINT)""")
db.commit()

bot = commands.Bot(command_prefix='!', intents = discord.Intents.all())

@bot.command()
async def ssp_top(ctx):
	print('Пользователь '+Back.GREEN+Fore.WHITE+f'{ctx.message.author}'+Style.RESET_ALL+' вызвал команду '+Back.GREEN+Fore.WHITE+'ssp_top'+Style.RESET_ALL)
	global db, sql
	top = []
	top_wins = []
	for stats in sql.execute("SELECT user, wins FROM stats ORDER BY wins DESC LIMIT 3"):
		top.append(await bot.fetch_user(stats[0]))
		top_wins.append(stats[1])

	if len(top) <= 0:
		await ctx.send(f'{ctx.message.author.mention}, в базе данных нет игроков 😦')

	if len(top) > 0:
		embed = discord.Embed(title=f"**ТОП ИГРОКОВ SSP**", color=discord.Colour.gold(), timestamp=ctx.message.created_at)
		embed.set_thumbnail(url=top[0].avatar_url)
		
	if len(top) == 1:
		embed.add_field(name=f'1. {top[0].name} ', value=f'*Количество побед: {top_wins[0]}*', inline=False)
	if len(top) == 2:
		embed.add_field(name=f'1. {top[0].name} ', value=f'*Количество побед: {top_wins[0]}*', inline=False)
		embed.add_field(name=f'2. {top[1].name} ', value=f'*Количество побед: {top_wins[1]}*', inline=False)
	if len(top) > 2:
		embed.add_field(name=f'1. {top[0].name} ', value=f'*Количество побед: {top_wins[0]}*', inline=False)
		embed.add_field(name=f'2. {top[1].name} ', value=f'*Количество побед: {top_wins[1]}*', inline=False)
		embed.add_field(name=f'3. {top[2].name} ', value=f'*Количество побед: {top_wins[2]}*', inline=False)	
	
	if len(top) > 0:
		await ctx.send(embed = embed)


@bot.command()
async def stats(ctx):
	try:
		await ctx.message.delete()
	except:
		pass
	print('Пользователь '+Back.GREEN+Fore.WHITE+f'{ctx.message.author}'+Style.RESET_ALL+' вызвал команду '+Back.GREEN+Fore.WHITE+'stats'+Style.RESET_ALL)
	global db, sql
	author = ctx.message.author
	sql.execute(f"SELECT user FROM stats WHERE user = '{author.id}'")
	if sql.fetchone() is None:
		await author.send('**У вас еще нет статистики!**\nСыграйте хотя бы одну игру, чтобы получить статистику. *(Игры с ботом не считаются)*')

	else:	
		for stats in sql.execute(f"SELECT wins, loses, games FROM stats WHERE user = '{author.id}'"):
			wins = stats[0]
			loses = stats[1]
			games = stats[2]
			winrate = (wins / games) * 100
			winrate = float('{:.2f}'.format(winrate))

		msg = f'**Статистика игр SSP по вашему запросу:**\n\n**Общее количество игр:** {games}\n**Победы:** {wins}\n**Поражения:** {loses}\n**Процент побед:** {winrate}%'
		await author.send(msg)



async def write_stats(winner: int, looser: int, tie: bool):
	global db, sql
	sql.execute(f"SELECT user FROM stats WHERE user = '{winner}'")
	if sql.fetchone() is None:
		if tie == True:
			sql.execute(f"INSERT INTO stats VALUES ({winner}, 1, 0, 1)")
		else:
			sql.execute(f"INSERT INTO stats VALUES ({winner}, 0, 0, 1)")
		db.commit()
	else:
		if tie == True:
			sql.execute(f"UPDATE stats SET wins = wins + 1, games = games + 1 WHERE user = ({winner})")
		else:
			sql.execute(f"UPDATE stats SET games = games + 1 WHERE user = ({winner})")
		db.commit()

	sql.execute(f"SELECT user FROM stats WHERE user = '{looser}'")
	if sql.fetchone() is None:
		if tie == True:
			sql.execute(f"INSERT INTO stats VALUES ({looser}, 0, 1, 1)")
		else:
			sql.execute(f"INSERT INTO stats VALUES ({looser}, 0, 0, 1)")
		db.commit()
	else:
		if tie == True:
			sql.execute(f"UPDATE stats SET loses = loses + 1, games = games + 1 WHERE user = ({looser})")
		else:
			sql.execute(f"UPDATE stats SET games = games + 1 WHERE user = ({looser})")
		db.commit()

stone = '✊'
scissors = '✌'
paper = '✋'

array = ['✊', '✌', '✋']

@bot.command()
async def ssp(ctx, user: discord.User, arg: int = 1):


	print('Пользователь '+Back.GREEN+Fore.WHITE+f'{ctx.message.author}'+Style.RESET_ALL+' вызвал команду '+Back.GREEN+Fore.WHITE+'ssp'+Style.RESET_ALL)

	guild = bot.get_guild(752821563455176824)

	player1 = ctx.message.author
	player2 = await bot.fetch_user(user.id)

	if arg > 0:

		if player1 != player2:

			await ctx.send(f'Игра {stone}-{scissors}-{paper} между {player1.mention} и {player2.mention}! Ожидание выбора игроков...')

			if player2 != bot.user:

				await player1.send(f'**Укажите номер жеста для игры с {player2.mention}:**\n\n1) {stone}\n2) {scissors}\n3) {paper}\n\nИли введите **"-"** чтобы отказаться от игры')
				await player2.send(f'**{player1.mention} предлагает вам сыграть в {stone}-{scissors}-{paper} {arg} раз(а)! Укажите номер жеста для начала игры:**\n\n1) {stone}\n2) {scissors}\n3) {paper}\n\nИли введите **"-"** чтобы отказаться от игры')

				def check(msg):
					if msg.channel.type == discord.ChannelType.private:
						if (msg.author == player1):
							players.remove(player1)
							return msg
						elif (msg.author == player2):
							players.remove(player2)
							return msg

				def check2(msg):
					if msg.channel.type == discord.ChannelType.private:
						if (msg.author in players):
							return msg


				count = arg

				while count > 0:

					players = []
					players.append(player1)
					players.append(player2)

					gesture1 = None
					gesture2 = None
					winner = None
					looser = None
					first = stone
					second = stone

					time.sleep(1)
					gesture1 = await bot.wait_for('message', check=check)
					if gesture1.content == '-':
						count = 0
						await ctx.send(f'*Игры не будет(\n{gesture1.author.mention} отказался от игры.*')
						break

					gesture2 = await bot.wait_for('message', check=check2)
					if gesture2.content == '-':
						count = 0
						await ctx.send(f'*Игры не будет(\n{gesture2.author.mention} отказался от игры.*')
						break

					for i in range(0,3):
						if gesture1.content == str(i+1):
							first = array[i]

						if gesture2.content == str(i+1):
							second = array[i]

					if (first == paper and second == stone) or (first == stone and second == scissors) or (first == scissors and second == paper):
						winner = gesture1.author
						looser = gesture2.author

					elif (first == paper and second == scissors) or (first == scissors and second == stone) or (first == stone and second == paper):
						winner = gesture2.author
						looser = gesture1.author

					elif first == second:
						winner = None

					if count != 0:
						if winner != None:
							await ctx.send(f'Игрок {gesture1.author.mention} выбрал {first}\nИгрок {gesture2.author.mention} выбрал {second}\n**Победитель: {winner.mention}**')
							asyncio.run_coroutine_threadsafe(write_stats(winner.id, looser.id, True), bot.loop)
						else:
							await ctx.send(f'Игрок {gesture1.author.mention} выбрал {first}\nИгрок {gesture2.author.mention} выбрал {second}\n**Ничья!**')
							asyncio.run_coroutine_threadsafe(write_stats(gesture1.author.id, gesture2.author.id, False), bot.loop)
					count -= 1

			else:

				await player1.send(f'**Укажите номер жеста для игры с {player2.mention}:**\n\n1) {stone}\n2) {scissors}\n3) {paper}\n\nИли введите **"-"** чтобы отказаться от игры')

				count = arg

				def check3(msg):
					if msg.channel.type == discord.ChannelType.private:
						if (msg.author == player1):
							return msg

				while count > 0:

					gesture1 = None
					gesture2 = None
					winner = None
					first = stone
					second = random.choice(array)

					time.sleep(1)
					gesture1 = await bot.wait_for('message', check=check3)

					for i in range(0,3):
						if gesture1.content == str(i+1):
							first = array[i]

					if gesture1.content == '-':
						count = 0
						await ctx.send(f'*Игры не будет(\n{gesture1.author.mention} отказался от игры.*')

					elif (first == paper and second == stone) or (first == stone and second == scissors) or (first == scissors and second == paper):
						winner = gesture1.author

					elif (first == paper and second == scissors) or (first == scissors and second == stone) or (first == stone and second == paper):
						winner = bot.user

					elif first == second:
						winner = None

					if count != 0:
						if winner != None:
							await ctx.send(f'Игрок {gesture1.author.mention} выбрал {first}\nИгрок {bot.user.mention} выбрал {second}\n**Победитель: {winner.mention}**')
						else:
							await ctx.send(f'Игрок {gesture1.author.mention} выбрал {first}\nИгрок {bot.user.mention} выбрал {second}\n**Ничья!**')

					count -= 1
		else:
			await ctx.send(f'{player1.mention}, с собой играть нельзя! 😡')
	else:
		await ctx.send(f'{player1.mention}, количество игр должно быть больше нуля!')


import bottoken
bot.run(bottoken.TOKEN)
