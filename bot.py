import json
import discord
import docker
import requests
from discord.ext import commands

from configLoader import Config

config = Config("config.json")
bot = commands.Bot(command_prefix=config.prefix)
client = docker.from_env()

splash = """
 __          __   _       _                           
 \ \        / /  | |     | |                          
  \ \  /\  / /_ _| |_ ___| |__  _ __ ___   __ _ _ __  
   \ \/  \/ / _` | __/ __| '_ \| '_ ` _ \ / _` | '_ \ 
    \  /\  / (_| | || (__| | | | | | | | | (_| | | | |
     \/  \/ \__,_|\__\___|_| |_|_| |_| |_|\__,_|_| |_|
                                                                                                          
"""

status_dict = {
    "created": ":white_circle: Created",
    "restarting": ":yellow_circle: Restarting",
    "running": ":green_circle: Running",
    "removing": ":red_circle: Removing",
    "paused": ":white_circle: Paused",
    "exited": ":red_circle: Exited",
    "dead": ":red_circle: Dead"
}


def fetch_container(name):
    for container in client.containers.list(all=True):
        if container.name == name and name in config.listBots():
            return container
    return None


def fetch_stack(name):
    r = requests.get(
        config.portainer_endpoint + "/stacks",
        headers={"Authorization": "Bearer {}".format(config.portainer_token)},
        verify=False
    )
    for swarm in r.json():
        if swarm['Name'] == name:
            return swarm
    return None


def redeploy_stack(stack):
    body = {
        "env": stack['Env'],
        "repositoryAuthentication": False,
        "repositoryPassword": "",
        "repositoryReferenceName": "refs/heads/main",
        "repositoryUsername": "",
        "environmentId": 1
    }
    r = requests.put(
        config.portainer_endpoint + "/stacks/{}/git/redeploy?endpointId={}".format(stack['Id'], stack['EndpointId']),
        data=json.dumps(body),
        headers={"Authorization": "Bearer {}".format(config.portainer_token)},
        verify=False
    )
    return r


def container_embed(container, title, description, color):
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_author(name=container, icon_url=config.getBot(container)['image'])
    return embed


def no_container_embed():
    return discord.Embed(title="Error", description="No container found. Please specify a valid container.",
                         color=0xff0000)


@bot.command()
async def status(ctx):
    if not config.hasPerms(ctx):
        return

    statusstr = ""
    for b in config.listBots():
        statusstr += "**" + b + "**\n"
        container = fetch_container(b)
        if container:
            statusstr += status_dict[container.status] + "\n\n"
        else:
            statusstr += ":white_circle: No container was found!\n\n"

    return await ctx.message.channel.send(
        embed=discord.Embed(title="Bot Status", description=statusstr, color=0x00ff00))


@bot.command()
async def start(ctx, bot=""):
    if not config.hasPerms(ctx):
        return
    container = fetch_container(bot)
    if not container:
        return await ctx.message.channel.send(embed=no_container_embed())

    message = await ctx.message.channel.send(embed=container_embed(bot, "Start Container", "Starting...", 0x21304a))
    container.start()
    await message.edit(embed=container_embed(bot, "Start Container", "Successfully started bot.", 0x00ff00))


@bot.command()
async def stop(ctx, bot=""):
    if not config.hasPerms(ctx):
        return
    container = fetch_container(bot)
    if not container:
        return await ctx.message.channel.send(embed=no_container_embed())

    message = await ctx.message.channel.send(embed=container_embed(bot, "Stop Container", "Stopping...", 0x21304a))
    container.stop()
    await message.edit(embed=container_embed(bot, "Stop Container", "Successfully stopped bot.", 0x00ff00))


@bot.command()
async def kill(ctx, bot=""):
    if not config.hasPerms(ctx):
        return
    container = fetch_container(bot)
    if not container:
        return await ctx.message.channel.send(embed=no_container_embed())

    message = await ctx.message.channel.send(embed=container_embed(bot, "Kill Container", "Killing...", 0x21304a))
    container.kill()
    await message.edit(embed=container_embed(bot, "Kill Container", "Successfully killed bot.", 0x00ff00))


@bot.command()
async def restart(ctx, bot=""):
    if not config.hasPerms(ctx):
        return
    container = fetch_container(bot)
    if not container:
        return await ctx.message.channel.send(embed=no_container_embed())

    message = await ctx.message.channel.send(embed=container_embed(bot, "Restart Container", "Restarting...", 0x21304a))
    container.restart()
    await message.edit(embed=container_embed(bot, "Restart Container", "Successfully restarted bot.", 0x00ff00))


@bot.command()
async def pull(ctx, bot=""):
    if not config.hasPerms(ctx):
        return
    container = fetch_container(bot)
    if not container:
        return await ctx.message.channel.send(embed=no_container_embed())

    stack = fetch_stack(container.name)
    if stack is None:
        return await ctx.message.channel.send(
            embed=container_embed(bot, "Error", "There is no stack for " + container.name + ".", 0xff0000))

    message = await ctx.message.channel.send(embed=container_embed(bot, "Pull Container", "Attempting to redeploy "
                                                                                          "image...\nThis might take "
                                                                                          "a while.", 0x00ff00))
    response = redeploy_stack(stack)
    status_message = ":white_check_mark: Successfully built new image"
    if response.status_code != 200:
        status_message = ":x: Error while building image"
        status_message += "\n```" + str(json.dumps(response, indent=4)) + "\n```"
    await message.edit(embed=container_embed(bot, "Pull Container", status_message, 0x21304a))


print(splash)
print("Logging into Portainer!")
config.login_portainer()
print("Successfully logged into Portainer!")
print("Starting Watchman")
bot.run(config.token)
