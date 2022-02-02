import sys
import discord
from subprocess import Popen, PIPE
from discord.ext import commands
from configLoader import Config
import subprocess
import docker
import re
from git import Repo

config = Config("config.json")
bot = commands.Bot(command_prefix=config.prefix)
client = docker.from_env()

@bot.command()
async def status(ctx, bot="all"):
    if not config.hasPerms(ctx):
        return
    
    statusstr = "**Status**\n"
    if bot != "all":
        if not config.getBot(bot):
            return await ctx.message.channel.send(embed=discord.Embed(title="Error", description="Bot not found", color=0xff0000))
        for container in client.containers.list():
            if container.image.attrs['RepoTags'][0] == config.getBot(bot)['container'] + ":latest":
                statusstr += container.name + " (" + container.image.attrs['RepoTags'][0]+ "): " + container.status + "\n\n"
    else:
        for container in client.containers.list():
            try: 
                statusstr += container.name + " (" + container.image.attrs['RepoTags'][0]+ "): " + container.status + "\n\n"
            except:
                pass

    if (statusstr == "**Status**\n"):
         return await ctx.message.channel.send(embed=discord.Embed(title="Offline", description="All bots offline", color=0xff0000))

    return await ctx.message.channel.send(embed=discord.Embed(title="Result", description=statusstr, color=0x00ff00))


@bot.command()
async def logs(ctx, bot):

    if not config.hasPerms(ctx):
        return
    if not config.getBot(bot):
        return await ctx.message.channel.send(embed=discord.Embed(title="Error", description="Bot not found", color=0xff0000))

    instances = []
    for container in client.containers.list():
        if container.image.attrs['RepoTags'][0] == config.getBot(bot)['container'] + ":latest":
            instances.append(container)
    
    if len(instances) == 0:
        return await ctx.message.channel.send(embed=discord.Embed(title="Error", description="There are no instances of this bot.", color=0xff0000))
    
    result = instances[0].logs()

    await ctx.message.channel.send(embed=discord.Embed(title="Result", description="```\n" + re.sub('\x1b\[[0-9;]*m', "", result.decode('utf-8'))[-4000:] + "```", color=0x00ff00))


@bot.command()
async def start(ctx, bot):

    if not config.hasPerms(ctx):
        return
    if not config.getBot(bot):
        return await ctx.message.channel.send(embed=discord.Embed(title="Error", description="Bot not found", color=0xff0000))
    instances = 0
    for container in client.containers.list():
        if container.image.attrs['RepoTags'][0] == config.getBot(bot)['container'] + ":latest":
            instances += 1
    if instances > 0:
        return await ctx.message.channel.send(embed=discord.Embed(title="Error", description="There is/are " + str(instances) + " instances already.", color=0xff0000))
    container = client.containers.run(config.getBot(bot)['container'], detach=True, network_mode="host")

    await ctx.message.channel.send(embed=discord.Embed(title="Result", description="**Name**\n" + container.name  + "\n**Status**\n" + container.status, color=0x00ff00))


@bot.command()
async def stop(ctx, bot):
    if not config.hasPerms(ctx):
        return
    if not config.getBot(bot):
        return await ctx.message.channel.send(embed=discord.Embed(title="Error", description="Bot not found", color=0xff0000))

    stopnum = 0
    messageSent = await ctx.message.channel.send(embed=discord.Embed(title="Waiting..", description="Stopping containers", color=0xff0000))
    for container in client.containers.list():
        print(container.image.attrs['RepoTags'][0])
        print(type(container.image))
        print(config.getBot(bot)['container'] + ":latest")
        if container.image.attrs['RepoTags'][0] == config.getBot(bot)['container'] + ":latest":
            container.stop()
            stopnum += 1
    
    

    await messageSent.edit(embed=discord.Embed(title="Result", description="**Containers Stopped**\n" + str(stopnum), color=0x00ff00))


@bot.command()
async def restart(ctx, bot):
    if not config.hasPerms(ctx):
        return
    if not config.getBot(bot):
        return await ctx.message.channel.send(embed=discord.Embed(title="Error", description="Bot not found", color=0xff0000))

    restartnum = 0
    messageSent = await ctx.message.channel.send(embed=discord.Embed(title="Waiting..", description="Restarting containers", color=0xff0000))
    for container in client.containers.list():
        print(container.image.attrs['RepoTags'][0])
        print(type(container.image))
        print(config.getBot(bot)['container'] + ":latest")
        if container.image.attrs['RepoTags'][0] == config.getBot(bot)['container'] + ":latest":
            container.stop()
            client.containers.run(config.getBot(bot)['container'], detach=True , network_mode="host")
            restartnum += 1
    
    

    await messageSent.edit(embed=discord.Embed(title="Result", description="**Containers Restarted**\n" + str(restartnum), color=0x00ff00))


@bot.command()
async def pull(ctx, bot):
    if not config.hasPerms(ctx):
        return
    if not config.getBot(bot):
        return await ctx.message.channel.send(embed=discord.Embed(title="Error", description="Bot not found", color=0xff0000))
    repo = Repo(config.getBot(bot)['path'])

    message = None

    try:
        assert not repo.bare
        message = await ctx.message.channel.send(embed=discord.Embed(title="Working..", description="Pulling from github...", color=0x00ff00))
        pullRes = repo.git.pull()
        await message.edit(embed=discord.Embed(title="Working..", description="Pulled from github ```\n" + pullRes + "```", color=0x00ff00))
    except:
        message = await ctx.message.channel.send(embed=discord.Embed(title="Error", description="Repo not found, attempting container rebuild " + str(sys.exc_info()[0]), color=0xff0000))

    try:
        await message.edit(embed=discord.Embed(title="Working..", description= "Building..", color=0x00ff00))
        buildRes = subprocess.run(config.getBot(bot)['buildscript'], shell=True, capture_output=True, cwd=config.getBot(bot)['path']).stdout
        await message.edit(embed=discord.Embed(title="Done!", description="Rebuilt container, denote restart must be done manually! ```\n" + re.sub('\x1b\[[0-9;]*m', "", buildRes.decode('utf-8'))[-3000:] + "```", color=0x00ff00))
    except:
        await message.edit(embed=discord.Embed(title="Error", description="Container rebuild error: " + str(sys.exc_info()[0]), color=0xff0000))

    #await message.edit(embed=discord.Embed(title="Result", description="Pulled!", color=0x00ff00))

bot.run(config.token)
