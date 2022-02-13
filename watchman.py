import json
import discord
import docker
from discord.ext import commands
import requests

status_dict = {
    "created": ":white_circle: Created",
    "restarting": ":yellow_circle: Restarting",
    "running": ":green_circle: Running",
    "removing": ":red_circle: Removing",
    "paused": ":white_circle: Paused",
    "exited": ":red_circle: Exited",
    "dead": ":red_circle: Dead"
}


class Watchman(commands.Cog):

    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.client = docker.from_env()

    def fetch_container(self, name):
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

    def no_container_embed():
        return discord.Embed(title="Error", description="No container found. Please specify a valid container.",
                             color=0xff0000)

    @commands.command()
    async def status(self, ctx):
        '''
        Get Status of all containers.
        '''
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
    async def start(self, ctx, bot=""):
        '''
        Start a bot.
        '''
        if not self.config.hasPerms(ctx):
            return
        container = self.fetch_container(bot)
        if not container:
            return await ctx.message.channel.send(embed=self.no_container_embed())

        message = await ctx.message.channel.send(embed=self.container_embed(bot, "Start Container", "Starting...", 0x21304a))
        container.start()
        await message.edit(embed=self.container_embed(bot, "Start Container", "Successfully started bot.", 0x00ff00))

    @commands.command()
    async def stop(self, ctx, bot=""):
        '''
        Stop a bot.
        '''
        if not self.config.hasPerms(ctx):
            return
        container = self.fetch_container(bot)
        if not container:
            return await ctx.message.channel.send(embed=self.no_container_embed())

        message = await ctx.message.channel.send(embed=self.container_embed(bot, "Stop Container", "Stopping...", 0x21304a))
        container.stop()
        await message.edit(embed=self.container_embed(bot, "Stop Container", "Successfully stopped bot.", 0x00ff00))

    @commands.command()
    async def kill(self, ctx, bot=""):
        '''
        Ya know sometimes you just gotta.
        '''
        if not self.config.hasPerms(ctx):
            return
        container = self.fetch_container(bot)
        if not container:
            return await ctx.message.channel.send(embed=self.no_container_embed())

        message = await ctx.message.channel.send(embed=self.container_embed(bot, "Kill Container", "Killing...", 0x21304a))
        container.kill()
        await message.edit(embed=self.container_embed(bot, "Kill Container", "Successfully killed bot.", 0x00ff00))

    @commands.command()
    async def restart(self, ctx, bot=""):
        '''
        Restart a bot.
        '''
        if not self.config.hasPerms(ctx):
            return
        container = self.fetch_container(bot)
        if not container:
            return await ctx.message.channel.send(embed=self.no_container_embed())

        message = await ctx.message.channel.send(embed=self.container_embed(bot, "Restart Container", "Restarting...", 0x21304a))
        container.restart()
        await message.edit(embed=self.container_embed(bot, "Restart Container", "Successfully restarted bot.", 0x00ff00))

    @commands.command()
    async def pull(self, ctx, bot=""):
        '''
        Pull a bot (Auto restarts).
        '''
        if not self.config.hasPerms(ctx):
            return
        container = self.fetch_container(bot)
        if not container:
            return await ctx.message.channel.send(embed=self.no_container_embed())

        stack = self.fetch_stack(container.name)
        if stack is None:
            return await ctx.message.channel.send(
                embed=self.container_embed(bot, "Error", "There is no stack for " + container.name + ".", 0xff0000))

        message = await ctx.message.channel.send(embed=self.container_embed(bot, "Pull Container", "Attempting to redeploy "
                                                                            "image...\nThis might take "
                                                                            "a while.", 0x00ff00))
        response = self.redeploy_stack(stack)
        status_message = ":white_check_mark: Successfully built new image"
        if response.status_code != 200:
            status_message = ":x: Error while building image"
            status_message += "\n```" + \
                str(json.dumps(response, indent=4)) + "\n```"
        await message.edit(embed=self.container_embed(bot, "Pull Container", status_message, 0x21304a))
