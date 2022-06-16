from discord.ext import commands
import discord


async def send_embed(ctx,
                     title,
                     body,
                     colour,
                     r=False,
                     footer='',
                     edit=None):  # helper function cus embeds are pain
    embed = discord.Embed(title=title, description=body, colour=colour)
    embed.set_footer(text=footer)
    if edit is None:
        msg = await ctx.send(embed=embed)
    else:
        msg = edit
        await edit.edit(embed=embed)
    return msg if r else None


async def wait_for_message(ctx,
                           check,
                           timeout=60):  # another helper function weeee
    try:
        message = await client.wait_for('message',
                                        timeout=timeout,
                                        check=check)
    except asyncio.TimeoutError:
        await send_embed(ctx, 'Error', 'Error')
        return
    else:
        return message
