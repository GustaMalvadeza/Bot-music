import disnake
from disnake.ext import commands
from utils.music.errors import parse_error
from utils.music.interactions import send_message


class ErrorHandler(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener('on_user_command_error')
    @commands.Cog.listener('on_message_command_error')
    @commands.Cog.listener('on_slash_command_error')
    async def on_interaction_command_error(self, inter: disnake.ApplicationCommandInteraction, error: Exception):

        embed = disnake.Embed(color=disnake.Colour.red())

        error_txt = parse_error(inter, error)

        if error_txt:
            embed.description = error_txt
            return await send_message(inter, embed=embed)

        embed.description = f"**Ocorreu um erro no comando:**\n" \
                            f"```py\n{str(repr(error))[:2020].replace(self.bot.http.token, 'mytoken')}```"

        await send_message(inter, embed=embed)


    @commands.Cog.listener("on_command_error")
    async def on_legacy_command_error(self, ctx: commands.Context, error: Exception):

        embed = disnake.Embed(color=disnake.Colour.red())

        error_txt = parse_error(ctx, error)

        if error_txt:
            embed.description = error_txt
            return await ctx.reply(embed=embed)

        if isinstance(error, commands.CommandNotFound):
            return

        embed.description = f"**Ocorreu um erro no comando:**\n" \
                            f"```py\n{str(repr(error))[:2020].replace(self.bot.http.token, 'mytoken')}```"

        await ctx.reply(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))