import discord
from subprocess import Popen, PIPE
from discord.ext import commands
from configLoader import Config
import subprocess
config = Config("config.json")
bot = commands.Bot(command_prefix=config.prefix)


@bot.command()
async def status(ctx, bot="all"):
    if bot != "all":
        if not config.getBot(bot):
            return await ctx.message.channel.send(embed=discord.Embed(title="Error", description="Bot not found", color=0xff0000))
        cmdarray = ['pm2', 'show', bot]
    else:
        cmdarray = ['pm2', 'status']
    if not config.hasPerms(ctx):
        return
    result = subprocess.check_output(" ".join(cmdarray), shell=True)

    return await ctx.message.channel.send(embed=discord.Embed(title="Result", description="```\n" + result.decode('utf-8') + "```", color=0x00ff00))


@bot.command()
async def logs(ctx, bot):

    if not config.hasPerms(ctx):
        return
    if not config.getBot(bot):
        return await ctx.message.channel.send(embed=discord.Embed(title="Error", description="Bot not found", color=0xff0000))
    result = subprocess.check_output(" ".join(['pm2', 'logs', bot, "--nostream", "--lines", "5000"]), shell=True)

    await ctx.message.channel.send(embed=discord.Embed(title="Result", description="```\n" + result.decode('utf-8')[-4000:] + "```", color=0x00ff00))


@bot.command()
async def start(ctx, bot):

    if not config.hasPerms(ctx):
        return
    if not config.getBot(bot):
        return await ctx.message.channel.send(embed=discord.Embed(title="Error", description="Bot not found", color=0xff0000))
    result = subprocess.check_output(" ".join(['pm2', 'start', bot]), shell=True)

    await ctx.message.channel.send(embed=discord.Embed(title="Result", description="```\n" + result.decode('utf-8') + "```", color=0x00ff00))


@bot.command()
async def stop(ctx, bot):
    if not config.hasPerms(ctx):
        return
    if not config.getBot(bot):
        return await ctx.message.channel.send(embed=discord.Embed(title="Error", description="Bot not found", color=0xff0000))
    result = subprocess.check_output(" ".join(['pm2', 'stop', bot]), shell=True)

    await ctx.message.channel.send(embed=discord.Embed(title="Result", description="```\n" + result.decode('utf-8') + "```", color=0x00ff00))


@bot.command()
async def restart(ctx, bot):
    if not config.hasPerms(ctx):
        return
    if not config.getBot(bot):
        return await ctx.message.channel.send(embed=discord.Embed(title="Error", description="Bot not found", color=0xff0000))
    result = subprocess.check_output(" ".join(['pm2', 'restart', bot]), shell=True)

    await ctx.message.channel.send(embed=discord.Embed(title="Result", description="```\n" + result.decode('utf-8') + "```", color=0x00ff00))


@bot.command()
async def pull(ctx, bot, commit="latest"):
    if commit == "latest":
        cmdargs = ['pm2', 'pull', bot]
    else:
        cmdargs = ['pm2', 'pull', bot, commit]
    if not config.hasPerms(ctx):
        return
    if not config.getBot(bot):
        return await ctx.message.channel.send(embed=discord.Embed(title="Error", description="Bot not found", color=0xff0000))
    result = subprocess.check_output(" ".join(cmdargs), shell=True)

    await ctx.message.channel.send(embed=discord.Embed(title="Result", description="```\n" + result.decode('utf-8') + "```", color=0x00ff00))

bot.run(config.token)
