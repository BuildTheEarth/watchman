import interactions
import docker

status_dict = {
    "created": ":white_circle: Created",
    "restarting": ":yellow_circle: Restarting",
    "running": ":green_circle: Running",
    "removing": ":red_circle: Removing",
    "paused": ":white_circle: Paused",
    "exited": ":red_circle: Exited",
    "dead": ":red_circle: Dead",
    "none": ":white_circle: No container was found!"
}
generic_reason = "This is an extremely confidential bot for confidential purposes, scram."


def no_container_embed():
    return interactions.Embed(title="Error", description="No container found. Please specify a valid container.",
                         color=0xff0000)


class Watchman(interactions.Extension):

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

    def container_embed(self, container, title, description, color):
        embed = interactions.Embed(
            title=title, description=description, color=color)
        embed.set_author(
            name=container, icon_url=self.config.getBot(container)['icon'])
        return embed

    def command_name(self, name):
        return "`" + self.config.prefix + name + "` "
    
    @interactions.extension_listener(name='on_command')
    async def log(self, ctx: interactions.CommandContext):
        print(f'[{ctx.guild.name}] {ctx.author.name} ran \'{ctx.data.options[0].name}\' command.')
    
    @interactions.extension_command(name="wm", description=generic_reason)
    async def parent(self, ctx: interactions.CommandContext):
        if not self.config.hasPerms(ctx):
            embed = interactions.Embed(description="This is an extremely confidential bot for confidential purposes, scram.", color=0x21304a)
            await ctx.send(embeds=[embed], ephemeral=True)
            return interactions.StopCommand
        pass

    @parent.subcommand(name="help", description=generic_reason)
    async def help(self, ctx: interactions.CommandContext):
        # Shows all commands for watchman

        embed = interactions.Embed(title="Watchman Help", description="Commands:", color=0x21304a)
        embed.add_field(name=self.command_name("info"), value="Get system information.", inline=False)
        embed.add_field(name=self.command_name("status"), value="Check the status of the bots.", inline=False)
        embed.add_field(name=self.command_name("start <bot>"), value="Start a bot.", inline=False)
        embed.add_field(name=self.command_name("stop <bot>"), value="Stop a bot.", inline=False)
        embed.add_field(name=self.command_name("kill <bot>"), value="Kill a bot.", inline=False)
        embed.add_field(name=self.command_name("restart <bot>"), value="Start a bot.", inline=False)
        embed.add_field(name=self.command_name("pull <bot>"), value="Pull a new image for the bot.", inline=False)
        return await ctx.send(embeds=[embed])

    @parent.subcommand(name="info", description=generic_reason)
    async def info(self, ctx: interactions.CommandContext):
        # Shows info for watchman host machine

        embed = interactions.Embed(title="Docker Info", description="", color=0x21304a)
        version = self.client.version()
        embed.add_field(name="Platform", value=version['Platform']['Name'], inline=False)
        embed.add_field(name="Version", value=version['Version'], inline=False)
        embed.add_field(name="API Version", value=version['ApiVersion'], inline=False)
        return await ctx.send(embeds=[embed])

    @parent.subcommand(name="status", description=generic_reason)
    async def status(self, ctx: interactions.CommandContext):
        # Displays current status of bot containers
        embed = interactions.Embed(title="Bot Status", description="", color=0x21304a)
        for b in self.config.listBots():
            container = self.fetch_container(b)
            if container:
                desc = status_dict[container.status] + "\n\n"
            else:
                desc = ":white_circle: No container was found!\n\n"
            embed.add_field(name="**" + b + "**", value=desc, inline=False)

        return await ctx.send(embeds=[embed])

    @parent.subcommand(name="start", description=generic_reason)
    @interactions.option()
    async def start(self, ctx: interactions.CommandContext, bot:str):
        # Starts a bot by its container name
        container = self.fetch_container(bot)
        if not container:
            return await ctx.send(embeds=[no_container_embed()])

        message = await ctx.send(
            embeds=[self.container_embed(bot, "Start Container", "Starting...", 0x21304a)])
        container.start()
        await message.edit(embeds=[self.container_embed(bot, "Start Container", "Successfully started bot.", 0x00ff00)])

    @parent.subcommand(name="stop", description=generic_reason)
    @interactions.option()
    async def stop(self, ctx: interactions.CommandContext, bot:str):
        # Stops a bot by its container name
        container = self.fetch_container(bot)
        if not container:
            return await ctx.send(embeds=[no_container_embed()])

        message = await ctx.send(
            embeds=[self.container_embed(bot, "Stop Container", "Stopping...", 0x21304a)])
        container.stop()
        await message.edit(embeds=[self.container_embed(bot, "Stop Container", "Successfully stopped bot.", 0x00ff00)])

    @parent.subcommand(name="kill", description=generic_reason)
    @interactions.option()
    async def kill(self, ctx: interactions.CommandContext, bot:str):
        # Kills a bot by its container name
        container = self.fetch_container(bot)
        if not container:
            return await ctx.send(embeds=[no_container_embed()])

        message = await ctx.send(
            embeds=[self.container_embed(bot, "Kill Container", "Killing...", 0x21304a)])
        container.kill()
        await message.edit(embeds=[self.container_embed(bot, "Kill Container", "Successfully killed bot.", 0x00ff00)])

    @parent.subcommand(name="restart", description=generic_reason)
    @interactions.option()
    async def restart(self, ctx: interactions.CommandContext, bot:str):
        # Restarts a bot by its container name
        container = self.fetch_container(bot)
        if not container:
            return await ctx.send(embeds=[no_container_embed()])

        message = await ctx.send(
            embeds=[self.container_embed(bot, "Restart Container", "Restarting...", 0x21304a)])
        container.restart()
        await message.edit(
            embeds=[self.container_embed(bot, "Restart Container", "Successfully restarted bot.", 0x00ff00)])

    @parent.subcommand(name="pull", description=generic_reason)
    @interactions.option()
    async def pull(self, ctx: interactions.CommandContext, bot:str):
        # Pulls any changes from the registry, and creates a new container
        bot_info = self.config.getBot(bot)
        if bot_info is None:
            return await ctx.send(embeds=[no_container_embed()])

        container = self.fetch_container(bot)
        image = bot_info['image']
        message = await ctx.send(embeds=[self.container_embed(bot, "Pull Container", "Stopping: "
                                                                                                   ":hourglass"
                                                                                                   ":\nPulling: "
                                                                                                   ":black_small_square:\nStarting: :black_small_square:",
                                                                            0x21304a)])
        try:
            if container is not None:
                container.stop()
                container.remove()
            await message.edit(embeds=[self.container_embed(bot, "Pull Container", "Stopping: :white_check_mark"
                                                                                 ":\nPulling: :hourglass:\nStarting: "
                                                                                 ":black_small_square:", 0x21304a)])
            self.client.images.pull(repository=image, tag="latest")
            await message.edit(embeds=[self.container_embed(bot, "Pull Container", "Stopping: :white_check_mark"
                                                                                 ":\nPulling: "
                                                                                 ":white_check_mark:\nStarting: "
                                                                                 ":hourglass:", 0x21304a)])
            volumes = {}
            ports = {}
            restart_policy = {
                "Name": bot_info['restart_policy']
            }
            if bot_info['restart_policy'] == "never": restart_policy = None
            for k in bot_info['volumes']:
                volumes[k] = {
                    "bind": bot_info['volumes'][k],
                    "mode": "rw"
                }
            for k in bot_info['ports']:
                ports[k] = bot_info['ports'][k]
            labels = {
                "io.portainer.accesscontrol.teams": self.config.bot_group
            }
            self.client.containers.run(name=bot, image=image, network=bot_info['network'], volumes=volumes, labels=labels, ports=ports, restart_policy=restart_policy, detach=True)
            await message.edit(embeds=[self.container_embed(bot, "Pull Container", "Stopping: :white_check_mark"
                                                                                 ":\nPulling: "
                                                                                 ":white_check_mark:\nStarting: "
                                                                                 ":white_check_mark:\n\n"
                                                                                 ":white_check_mark: Successfully "
                                                                                 "built new image", 0x21304a)])
        except Exception as err:
            await message.edit(embeds=[self.container_embed(bot, "Pull Container", ":x: Failed to pull new "
                                                                                 "container.\n```" + str(err) +
                                                          "```", 0x21304a)])
            
def setup(client, config):
    Watchman(client, config)