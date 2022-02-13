import json
import discord
import docker
from discord.ext import commands
import requests

from configLoader import Config

splash = """
 __          __   _       _                           
 \ \        / /  | |     | |                          
  \ \  /\  / /_ _| |_ ___| |__  _ __ ___   __ _ _ __  
   \ \/  \/ / _` | __/ __| '_ \| '_ ` _ \ / _` | '_ \ 
    \  /\  / (_| | || (__| | | | | | | | | (_| | | | |
     \/  \/ \__,_|\__\___|_| |_|_| |_| |_|\__,_|_| |_|
      A minimal bot manager for BuildTheEarth™                                                                                                    
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


def no_container_embed():
    return discord.Embed(title="Error", description="No container found. Please specify a valid container.",
                         color=0xff0000)


class Watchman(commands.Cog):

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.client = docker.from_env()

    def fetch_container(self, name):
        if name is None:
            return None
        for container in self.client.containers.list(all=True):
            if container.name == name and name in self.config.listBots():
                return container
        return None

    def fetch_stack(self, name):
        r = requests.get(
            self.config.portainer_endpoint + "/stacks",
            headers={"Authorization": "Bearer {}".format(
                self.config.portainer_token)},
            verify=False
        )
        for swarm in r.json():
            if swarm['Name'] == name:
                return swarm
        return None

    def redeploy_stack(self, stack):
        body = {
            "env": stack['Env'],
            "repositoryAuthentication": False,
            "repositoryPassword": "",
            "repositoryReferenceName": "refs/heads/main",
            "repositoryUsername": "",
            "environmentId": 1
        }
        r = requests.put(
            self.config.portainer_endpoint +
            "/stacks/{}/git/redeploy?endpointId={}".format(
                stack['Id'], stack['EndpointId']),
            data=json.dumps(body),
            headers={"Authorization": "Bearer {}".format(
                self.config.portainer_token)},
            verify=False
        )
        return r

    def container_embed(self, container, title, description, color):
        embed = discord.Embed(
            title=title, description=description, color=color)
        embed.set_author(
            name=container, icon_url=self.config.getBot(container)['image'])
        return embed

    def command_name(self, name):
        return "`" + self.config.prefix + name + "` "

    @commands.Cog.listener(name='on_command')
    async def log(self, ctx):
        print(f'[{ctx.guild.name}] {ctx.author} ran \'{ctx.command}\' command.')

    @commands.command()
    async def help(self, ctx):
        # Shows all commands for watchman
        embed = discord.Embed(title="Watchman Help", description="Commands:", color=0x21304a)
        embed.add_field(name=self.command_name("info"), value="Get system information.", inline=False)
        embed.add_field(name=self.command_name("status"), value="Check the status of the bots.", inline=False)
        embed.add_field(name=self.command_name("start <bot>"), value="Start a bot.", inline=False)
        embed.add_field(name=self.command_name("stop <bot>"), value="Stop a bot.", inline=False)
        embed.add_field(name=self.command_name("kill <bot>"), value="Kill a bot.", inline=False)
        embed.add_field(name=self.command_name("restart <bot>"), value="Start a bot.", inline=False)
        embed.add_field(name=self.command_name("pull <bot>"), value="Pull a new image for the bot.", inline=False)
        return await ctx.message.channel.send(embed=embed)

    @commands.command()
    async def status(self, ctx):
        # Displays current status of bot containers
        if not self.config.hasPerms(ctx):
            return

        statusstr = ""
        for b in self.config.listBots():
            statusstr += "**" + b + "**\n"
            container = self.fetch_container(b)
            if container:
                statusstr += status_dict[container.status] + "\n\n"
            else:
                statusstr += ":white_circle: No container was found!\n\n"

        return await ctx.message.channel.send(
            embed=discord.Embed(title="Bot Status", description=statusstr, color=0x00ff00))

    @commands.command()
    async def start(self, ctx, bot):
        # Starts a bot by its container name
        if not self.config.hasPerms(ctx):
            return
        container = self.fetch_container(bot)
        if not container:
            return await ctx.message.channel.send(embed=no_container_embed())

        message = await ctx.message.channel.send(
            embed=self.container_embed(bot, "Start Container", "Starting...", 0x21304a))
        container.start()
        await message.edit(embed=self.container_embed(bot, "Start Container", "Successfully started bot.", 0x00ff00))

    @commands.command()
    async def stop(self, ctx, bot):
        # Stops a bot by its container name
        if not self.config.hasPerms(ctx):
            return
        container = self.fetch_container(bot)
        if not container:
            return await ctx.message.channel.send(embed=no_container_embed())

        message = await ctx.message.channel.send(
            embed=self.container_embed(bot, "Stop Container", "Stopping...", 0x21304a))
        container.stop()
        await message.edit(embed=self.container_embed(bot, "Stop Container", "Successfully stopped bot.", 0x00ff00))

    @commands.command()
    async def kill(self, ctx, bot):
        # Kills a bot by its container name
        if not self.config.hasPerms(ctx):
            return
        container = self.fetch_container(bot)
        if not container:
            return await ctx.message.channel.send(embed=no_container_embed())

        message = await ctx.message.channel.send(
            embed=self.container_embed(bot, "Kill Container", "Killing...", 0x21304a))
        container.kill()
        await message.edit(embed=self.container_embed(bot, "Kill Container", "Successfully killed bot.", 0x00ff00))

    @commands.command()
    async def restart(self, ctx, bot):
        # Restarts a bot by its container name
        if not self.config.hasPerms(ctx):
            return
        container = self.fetch_container(bot)
        if not container:
            return await ctx.message.channel.send(embed=no_container_embed())

        message = await ctx.message.channel.send(
            embed=self.container_embed(bot, "Restart Container", "Restarting...", 0x21304a))
        container.restart()
        await message.edit(
            embed=self.container_embed(bot, "Restart Container", "Successfully restarted bot.", 0x00ff00))

    @commands.command()
    async def pull(self, ctx, bot):
        # Pulls any changes from the portainer stack, then force-rebuilds using docker-compose
        if not self.config.hasPerms(ctx):
            return
        container = self.fetch_container(bot)
        if not container:
            return await ctx.message.channel.send(embed=no_container_embed())

        self.config.login_portainer()
        stack = self.fetch_stack(container.name)
        if stack is None:
            return await ctx.message.channel.send(
                embed=self.container_embed(bot, "Error", "There is no stack for " + container.name + ".", 0xff0000))

        message = await ctx.message.channel.send(
            embed=self.container_embed(bot, "Pull Container", "Attempting to redeploy "
                                                              "image...\nThis might take "
                                                              "a while.", 0x00ff00))
        response = self.redeploy_stack(stack)
        status_message = ":white_check_mark: Successfully built new image"
        if response.status_code != 200:
            status_message = ":x: Error while building image"
            status_message += "\n```" + \
                              str(json.dumps(response, indent=4)) + "\n```"
        await message.edit(embed=self.container_embed(bot, "Pull Container", status_message, 0x21304a))


config = Config("config.json")
bot = commands.Bot(command_prefix=config.prefix)
bot.remove_command("help")
bot.add_cog(Watchman(bot, config))

print(splash)
print("Starting Watchman")
bot.run(config.token)
