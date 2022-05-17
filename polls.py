from discord.ext import commands
import discord
from utils import send_embed, wait_for_message
from datetime import datetime, timedelta

POLLS_CHANNEL = "polls"

class PollVote:
    def __init__(self, user, value):
        self.user = user
        self.value = value

    def __str__(self):
        return f"{self.user.id},{self.value}"

    def __repr__(self):
        return self.__str__()

class Poll:
    def __init__(self, name, options, duration=timedelta(days=1)):
        self.name = name
        self.options = options
        self.duration = duration
        self.votes = list()
        self.file = f"poll_{self.name}.csv"

    def save(self):
        pass

    def cast_vote(self):
        pass

class PollsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def poll(ctx):
        pass

# extension setup code
def setup(bot):
    bot.add_cog(PollsCog(bot))