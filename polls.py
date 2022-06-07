# TODO: implement

from discord.ext import commands
import discord
from utils import send_embed, wait_for_message
from datetime import datetime, timedelta
import csv
from threading import Thread

POLLS_CHANNEL = "polls"
polls = []

class PollVote:
    def __init__(self, user, value):
        self.user = user
        self.value = value

    def __str__(self):
        return f"{self.user.id},{self.value}"

    def __repr__(self):
        return self.__str__()

class Poll:
    def __init__(self, name, options, end_date=None):
        self.name = name
        self.options = options
        if end_date is None:
            self.end_date = datetime.now()+timedelta(days=1)
        else:
            pass # strptime
        self.votes = list()
        self.file = f"polls/poll_{self.name}.csv"

    def save(self):
        with open(self.file, "w", newline="") as f: # save votes
            writer = csv.writer(self.file)
            for vote in self.votes:
                writer.writerow(str(vote))

        with open("polls/polls.csv", "w", newline="") as f: # save self
            pass
            
                
    def load(self):
        with open(self.file, "r") as f:
            reader = csv.reader(self.file)
            next(reader) # skip header
            for row in reader:
                self.votes.append(PollVote(*row))

    def cast_vote(self):
        pass

    def start(self):
        # create thread and start it
        pass

    def end(self):
        pass

def setup_polls():
    with open("polls/polls.csv", "r") as f:
        polls_reader = csv.reader("polls/polls.csv")
        next(polls_reader) # skip header
        for row in reader:
            polls.append(Poll(*row))

class PollsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def poll(ctx):
        pass

# extension setup code
def setup(bot):
    bot.add_cog(PollsCog(bot))
    for poll in polls:
        polls.start()