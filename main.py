import disnake
from disnake.ext import commands

bot = commands.Bot(command_prefix='префикс', intents=disnake.Intents.all())
bot.load_extension("ticket_system.py")

bot.run("MTIzNDkxMDkxNjE5ODQwMDEyMg.G4wdED.bHKBvjnTuNQBuNiCm0o-XaYve7z9FmU9DXbfrA")
