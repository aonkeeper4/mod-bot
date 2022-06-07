# TODO: organise (docstrings, type hinting)
# TODO: use sql database instead of replit db

from discord.ext import commands
import discord
import asyncio
from replit import db
import secrets
import random
import string
from datetime import datetime, timedelta
from utils import send_embed, wait_for_message
import functools

ADMIN_CHANNEL = 'suggestions-inbox' # TODO: command to change/setup this

class Suggestion: # yes
    def __init__(self, title, body, created_at=datetime.now().strftime("%d/%m/%Y %H:%M:%S"), s_id=None, position=0, tags=[]): # no more kwargs
        self.suggestion_count = db.get('_SUGGESTION_COUNT', 0)
        self.title = title
        self.body = body
        self.id = s_id if s_id is not None else 's'+secrets.token_hex(4) # suggestion id
        self.created_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.position = position
        self.tags = tags

    def add(self): # adds suggestion to the database
        if self.position == 0:
            self.suggestion_count += 1
            self.position = self.suggestion_count # 'Suggestion #' text in the title

        db[self.id] = repr(self)
        db['_SUGGESTION_COUNT'] = self.suggestion_count

    def to_embed(self, *, insert=False, colour=discord.Colour.dark_teal()):
        tag_string = ', '.join(self.tags[1:]) if self.tags > [''] else 'None'
        embed = discord.Embed(title=('Inspect - ' if insert else '')+'Suggestion #'+str(self.position), colour=colour)
        embed.add_field(name=self.title, value=self.body)
        embed.set_footer(text=f'{self.id} | Created at {self.created_at} | Tags: {tag_string}')
        return embed

    def __str__(self):
        return f'Suggestion {self.id} Created at {self.created_at}'

    def __repr__(self):
        tags_str = ':'.join(self.tags)
        return f'Suggestion({self.title}, {self.body}, {self.created_at}, {self.id}, {self.position}, {tags_str})'

    @staticmethod
    def from_string(string):
        args = [arg.strip() for arg in string[11:-1].split(',')]
        args[2] = datetime.strptime(args[2], '%d/%m/%Y %H:%M:%S') if args[2] > '' else datetime.now().strftime("%d/%m/%Y %H:%M:%S") # gets created_at from string. this was painful
        args[5] = args[5].split(':')
        return Suggestion(*args) # woo list unpacking

    def __contains__(self, other): # for search feature
        return (other in self.title) or (other == self.id) or (other in self.body)

    def add_tag(self, tag):
        self.tags.append(tag)
        db[self.id] = repr(self)

def get_filter_vars(s_filter): # TODO: get rid of all of the Suggestion.from_string
        filter_str = '' # stuff for the search feature
        if s_filter is None:
            s_filterfunc = lambda kv: True
            filter_str = 'All'
        else:
            queries = s_filter.split("; ")
            funcs = []
            for q in queries:
                kw, args = q.split(": ")
                args_list = [kw] + args.split(", ")
                if args_list[0] == "tags": # use match statement?
                    tags = args_list[1:]
                    f = lambda kv: any(tag in Suggestion.from_string(kv[1]).tags for tag in tags)
                elif args_list[0] == "created-after":
                    date = args_list[1]
                    if date[-1] in "ymwdh":
                        timescale = date[-1]
                        base_dates_dict = {"y": timedelta(days=365), "m": timedelta(days=30), "w": timedelta(weeks=1), "d": timedelta(days=1), "h": timedelta(hours=1)}
                        total_date_time = base_dates_dict[timescale]*int(date[:-1])
                    else:
                        total_date_time = datetime.strptime(date, "%d/%m/%Y")
                    f = lambda kv: datetime.now()-total_date_time <= datetime.strptime(Suggestion.from_string(kv[1]).created_at, "%d/%m/%Y %H:%M:%S")
                elif args_list[0] == "created-before":
                    date = args_list[1]
                    if date[-1] in "ymwdh":
                        timescale = date[-1]
                        base_dates_dict = {"y": timedelta(days=365), "m": timedelta(days=30), "w": timedelta(weeks=1), "d": timedelta(days=1), "h": timedelta(hours=1)}
                        total_date_time = base_dates_dict[timescale]*int(date[:-1])
                    else:
                        total_date_time = datetime.strptime(date, "%d/%m/%Y")
                    f = lambda kv: datetime.now()-total_date_time >= datetime.strptime(Suggestion.from_string(kv[1]).created_at, "%d/%m/%Y %H:%M:%S")
                elif args_list[0] == "contains":
                    search = args_list[1]
                    f = lambda kv: any(word in Suggestion.from_string(kv[1]) for word in search.split())
                funcs.append(f)
            filter_str = f"'{s_filter}'"
            s_filterfunc = lambda kv: all(func(kv) for func in funcs)
        return s_filterfunc, filter_str

def safe_suggestion_lookup(coro): # finally, a good use for decorators
    @functools.wraps(coro) # __name__ gets fixed
    async def _wrapper(*args, **kwargs):
        try:
            return await coro(*args, **kwargs)
        except KeyError:
            await send_embed(ctx, 'Error', 'Error - invalid suggestion id', discord.Colour.red())
            return

    return _wrapper

class SuggestionsCog(commands.Cog): # cog to hold all suggestions-related commands
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help=f'Creates a new suggestion and sends it to the #{ADMIN_CHANNEL} channel.')
    async def suggest(self, ctx):
        await send_embed(ctx, 'Suggestion title', 'Please type your suggestion title', discord.Colour.dark_teal())
        title = await wait_for_message(ctx, lambda msg: msg.author == ctx.message.author and len(msg.content) <= 30)
        await send_embed(ctx, 'Suggestion body', 'Please type the rest of your suggestion', discord.Colour.dark_teal())
        body = await wait_for_message(ctx, lambda msg: msg.author == ctx.message.author)
        suggestion = Suggestion(title.content, body.content)
        embed = suggestion.to_embed()
        admin_channel = discord.utils.get(ctx.message.guild.channels, name=ADMIN_CHANNEL)
        await admin_channel.send(embed=embed)
        await send_embed(ctx, 'Suggestion sent', 'Suggestion created successfully! It has been sent to the admins for them to review.', discord.Colour.dark_teal())
    
    @commands.command(aliases=['list'], help='View all suggestions - can be used with a filter')
    async def _list(self, ctx, *, s_filter=None):
        s_filterfunc, filter_str = get_filter_vars(s_filter)
        async with ctx.typing():
            def check(kv):
                print(kv)
                is_suggestion = kv[0].startswith("s")
                search_filter = s_filterfunc(kv)
                print(is_suggestion, search_filter)
                return is_suggestion and search_filter
            all_suggestions = list(filter(check, db.items())) # TODO: use generators
            if len(all_suggestions) == 0:
                await send_embed(ctx, f'Suggestions - {filter_str}', '```Nothing was found by that query.```', discord.Colour.gold()) 
                return
            suggestion_pages = []
            for i in range(0, len(all_suggestions), 6):
                try: suggestion_pages.append(all_suggestions[i:i+6])
                except IndexError: suggestion_pages.append(all_suggestions[i:i+len(all_suggestions)%6]) # suggesstion numbers for menu
            suggestion_strs = []
            for suggestion_page in suggestion_pages:
                suggestion_str = '{0:^18}|{1:^31}\n'.format('ID', 'Title')
                suggestion_str += '-'*18+'+'+'-'*31+'\n'
                suggestion_str += '\n'.join(['{0:^18}|{1:^31}'.format(s_id, Suggestion.from_string(s).title) for s_id, s in suggestion_page]) # display suggestion previews
                suggestion_strs.append(suggestion_str)
            current_page = 0
        async def setup_msg(ctx, current_page, msg=None):
            emoji_list = ['◀']*(current_page>0) + ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣'][:len(suggestion_pages[current_page])] + ['▶']*(current_page<len(suggestion_pages)-1) # gets emojis for menu
            msg = await send_embed(ctx, f'Suggestions - {filter_str} ({len(all_suggestions)} results)', f'```{suggestion_strs[current_page]}```', discord.Colour.gold(), True, f'Page {current_page+1}/{len(suggestion_pages)}'+'\u3000'*30, edit=msg) # actually display the page
            for emoji in emoji_list: # add menu
                await msg.add_reaction(emoji)
            return msg, emoji_list
        msg, emoji_list = await setup_msg(ctx, current_page)
        async def wait_for_reactions(ctx, current_page, msg, emoji_list): # recursive function so the menu is useful
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60, check=lambda reaction, user: user == ctx.message.author and str(reaction.emoji) in emoji_list) # TODO: use action bars?
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                return
            if reaction.emoji == '◀': # dec page
                current_page -= 1
                await msg.clear_reactions()
                msg, emoji_list = await setup_msg(ctx, current_page, msg)
                await wait_for_reactions(ctx, current_page, msg, emoji_list)
            elif reaction.emoji == '▶': # inc page
                current_page += 1
                await msg.clear_reactions()
                msg, emoji_list = await setup_msg(ctx, current_page, msg)
                await wait_for_reactions(ctx, current_page, msg, emoji_list)
            else: # number button pressed
                # add back button?
                n_emoji_list = emoji_list[(current_page>0):] if current_page < len(suggestion_pages) else emoji_list[(current_page>0):-1]
                number = n_emoji_list.index(reaction.emoji) # no more ord magic
                embed = Suggestion.from_string(suggestion_pages[current_page][number][1]).to_embed(insert=True, colour=discord.Colour.gold())
                await msg.clear_reactions()
                await msg.edit(embed=embed)
                return
        await wait_for_reactions(ctx, current_page, msg, emoji_list)
    
    @commands.command(help='Clears all suggestions')
    async def clear(self, ctx):
        for key in db:
            del db[key]
        await send_embed(ctx, 'Cleared', 'Cleared all suggestions! :boom:', discord.Colour.dark_red())
        
    @commands.command(help='Deletes a suggestion by id')
    @safe_suggestion_lookup
    async def delete(self, ctx, s_id):
        del db[s_id]
        await send_embed(ctx, 'Suggestion deleted', 'Deleted suggestion ' + s_id, discord.Colour.green())

    @commands.command(help='Adds a tag to a suggestion by id')
    @safe_suggestion_lookup
    async def tag(self, ctx, s_id, tag):
        tagged_suggestion = Suggestion.from_string(db[s_id]).add_tag(tag) # garbage collection
        tagged_suggestion.add()
        await send_embed(ctx, 'Tag added', f'Tag {tag} added to suggestion {s_id}', discord.Colour.green())

    @commands.command(help='Inspects a suggestion by id')
    @safe_suggestion_lookup
    async def inspect(self, ctx, s_id):
        embed = Suggestion.from_string(db[s_id]).to_embed(insert=True, colour=discord.Colour.teal())
        await ctx.send(embed=embed)
    
    @commands.command(help='Populates suggestions database with random suggestions. This does not send the suggestions to the admins as it is a debug command.')
    async def populate(self, ctx, number=25):
        if number > 100:
            await send_embed(ctx, 'Error', 'Error - too many suggestions to populate', discord.Colour.red())
            return
        async with ctx.typing():
            for i in range(number):
                title = ''.join([random.choice(string.ascii_lowercase) for i in range(10)])
                body = ''.join([random.choice(string.ascii_lowercase) for i in range(100)])
                suggestion = Suggestion(title, body) # garbage collection
                suggestion.add()
        await send_embed(ctx, 'Suggestions populated', f'The suggestions database was populated with {number} suggestions', discord.Colour.blue())

# extension setup code
def setup(bot):
    bot.add_cog(SuggestionsCog(bot))