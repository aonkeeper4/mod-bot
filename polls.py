# TODO: implement
# i have no idea if this even works

from discord.ext import commands
import discord
from utils import send_embed, wait_for_message
from datetime import datetime, timedelta
import csv
from threading import Thread

POLLS_CHANNEL = "polls"


class PollVote:
    def __init__(self, user_id, value):
        self.user_id = user_id
        self.value = value

    def __str__(self):
        return f"{self.user_id},{self.value}"

    def __repr__(self):
        return self.__str__()


class Poll:
    def __init__(self, name, options, end_time):
        self.name = name
        self.options = options.split(":")
        self.end_time = datetime.strptime(end_time, "%d/%m/%Y %H:%M:%S")
        self.votes = list()
        self.file = f"polls/poll_{self.name}.csv"

    def save(self):
        with open(self.file, "w", newline="") as f:  # save votes
            writer = csv.writer(self.file)
            for vote in self.votes:
                writer.writerow(str(vote))

        with open("polls/polls.csv", "w", newline="") as f:  # save self
            writer = csv.writer(self.file)
            writer.writerow(str(self))

    def load(self):
        with open(self.file, "r") as f:
            reader = csv.reader(self.file)
            next(reader)  # skip header
            for row in reader:
                self.votes.append(PollVote(*row))

    def cast_vote(self, user_id, option):
        if option not in self.options:
            raise ValueError("Option to vote on must exist")
        self.votes.append(PollVote(user_id, option))

    def run(self):
        while True:
            if datetime.now() > self.end_time:
                return

    def start(self):
        run_thread = Thread(target=self.run)
        run_thread.start()

    def __str__(self):
        endtime_f = datetime.strftime(self.end_time, "%d/%m/%Y %H:%M:%S")
        options_str = ":".join(self.options)
        return f"{self.name},{options_str},{endtime_f}"


def setup_polls():
    # csv is not cooperating sadge
    polls = []
    with open("polls/polls.csv", "r") as f:
        polls_reader = csv.reader("polls/polls.csv")
        next(polls_reader)  # skip header
        for row in polls_reader:
            print(row)
            polls.append(Poll(*row))

    return polls


class PollsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def vote(ctx):
        pass
        # do it


# extension setup code
def setup(bot):
    bot.add_cog(PollsCog(bot))
    polls = []  # setup_polls() isnt working
    for poll in polls:
        poll.start()
