# TODO: add more modules (user management, auto-role, reaction roles, music?, ...)

from discord.ext import commands
import discord
import keep_alive
from utils import send_embed
import os

client = commands.Bot(command_prefix='$')

# load extensions
client.load_extension("suggestions")
client.load_extension("polls")

@client.event
async def on_ready():
    print('Bot is ready!')

@client.event
async def on_command_error(ctx, err):
    if isinstance(err, commands.errors.MissingRequiredArgument):
        await send_embed(ctx, 'Error', 'Error - missing required argument in command', discord.Colour.red())
    elif isinstance(err, commands.errors.CommandNotFound):
        command_name = str(err)[9:-14]
        await send_embed(ctx, 'Error', f'Error - unrecognised command: {command_name}', discord.Colour.red())
    else:
        raise err

keep_alive.keep_alive()

client.run(os.environ['token'])