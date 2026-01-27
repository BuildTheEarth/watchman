import interactions
import docker
import interactions
from config_loader import Config

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

base = interactions.SlashCommand(name="wm", description=generic_reason)
config = Config("config.json")
bot_option = interactions.slash_str_option("bot", True, False, None, None, None, "container")

def no_container_embed():
    return interactions.Embed(title="Error", description="No container found. Please specify a valid container.",
                         color=0xff0000)

def no_perms_embed():
    return interactions.Embed(title="Error", description="No permissions for this container. Please specify a container you have permissions for.",
                         color=0xff0000)   

class Watchman(interactions.Extension):

    def __init__(self, bot):
        self.bot = bot
        self.client = docker.from_env()

    def fetch_container(self, name):
        if name is None:
            return None
        for container in self.client.containers.list(all=True):
            if container.name == name and name in config.list_bots():
                return container
        return None

    def container_embed(self, container, title, description, color):
        embed = interactions.Embed(
            title=title, description=description, color=color)
        embed.set_author(
            name=container, icon_url=config.get_bot(container)['icon'])
        return embed

    def command_name(self, name):
        return "`" + config.prefix + name + "` "

    @interactions.listen(interactions.api.events.Error)
    async def on_error(self, error: interactions.api.events.Error):
        embed = interactions.Embed(title="Watchman Error", description=f"```\n{error.source}\n{error.error}\n```", color=0xFF0000)
        await bot.fetch_channel(config.error_channel).send(embeds=[embed])
        
    @interactions.listen(interactions.api.events.InteractionCreate)
    async def on_interaction_create(self, ctx: interactions.api.events.InteractionCreate):
        embed = interactions.Embed(description=f'[{ctx.guild.name}] {ctx.author.name} ran \'{ctx.data.options[0].name}\' command.', color=0xFF0000)
        await bot.fetch_channel(config.error_channel).send(embeds=[embed])

    @base.subcommand(sub_cmd_name="help", sub_cmd_description=generic_reason)
    @interactions.check(config.has_perms_async)
    async def help(self, ctx: interactions.SlashContext):
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

    @base.subcommand(sub_cmd_name="info", sub_cmd_description=generic_reason)
    @interactions.check(config.has_perms_async)
    async def info(self, ctx: interactions.SlashContext):
        # Shows info for watchman host machine
        embed = interactions.Embed(title="Docker Info", description="", color=0x21304a)
        version = self.client.version()
        embed.add_field(name="Platform", value=version['Platform']['Name'], inline=False)
        embed.add_field(name="Version", value=version['Version'], inline=False)
        embed.add_field(name="API Version", value=version['ApiVersion'], inline=False)
        return await ctx.send(embeds=[embed])

    @base.subcommand(sub_cmd_name="status", sub_cmd_description=generic_reason)
    @interactions.check(config.has_perms_async)
    async def status(self, ctx: interactions.SlashContext):
        # Displays current status of bot containers
        embed = interactions.Embed(title="Container Status", description="", color=0x21304a)
        for b in config.list_bots():
            container = self.fetch_container(b)
            if container:
                desc = status_dict[container.status] + "\n\n"
            else:
                desc = ":white_circle: No container was found!\n\n"
            embed.add_field(name="**" + b + "**", value=desc, inline=False)

        return await ctx.send(embeds=[embed])

    @base.subcommand(sub_cmd_name="start", sub_cmd_description=generic_reason)
    @interactions.check(config.has_perms_async)
    async def start(self, ctx: interactions.SlashContext, bot: bot_option):
        # Starts a bot by its container name
        bot_info = config.get_bot(bot)
        container = self.fetch_container(bot)
        if not container or not bot_info:
            return await ctx.send(embeds=[no_container_embed()])

        if not config.check_bot_specific_perms(ctx, bot_info):
            return await ctx.send(embeds=[no_perms_embed()])

        message = await ctx.send(
            embeds=[self.container_embed(bot, "Start Container", "Starting...", 0x21304a)])
        container.start()
        await message.edit(embeds=[self.container_embed(bot, "Start Container", "Successfully started container.", 0x00ff00)])

    @base.subcommand(sub_cmd_name="stop", sub_cmd_description=generic_reason)
    @interactions.check(config.has_perms_async)
    async def stop(self, ctx: interactions.SlashContext, bot: bot_option):
        # Stops a bot by its container name
        bot_info = config.get_bot(bot)
        container = self.fetch_container(bot)
        if not container or not bot_info:
            return await ctx.send(embeds=[no_container_embed()])

        if not config.check_bot_specific_perms(ctx, bot_info):
            return await ctx.send(embeds=[no_perms_embed()])

        message = await ctx.send(
            embeds=[self.container_embed(bot, "Stop Container", "Stopping...", 0x21304a)])
        container.stop()
        await message.edit(embeds=[self.container_embed(bot, "Stop Container", "Successfully stopped container.", 0x00ff00)])

    @base.subcommand(sub_cmd_name="kill", sub_cmd_description=generic_reason)
    @interactions.check(config.has_perms_async)
    async def kill(self, ctx: interactions.SlashContext, bot: bot_option):
        # Kills a bot by its container name
        bot_info = config.get_bot(bot)
        container = self.fetch_container(bot)
        if not container or not bot_info:
            return await ctx.send(embeds=[no_container_embed()])

        if not config.check_bot_specific_perms(ctx, bot_info):
            return await ctx.send(embeds=[no_perms_embed()])

        message = await ctx.send(
            embeds=[self.container_embed(bot, "Kill Container", "Killing...", 0x21304a)])
        container.kill()
        await message.edit(embeds=[self.container_embed(bot, "Kill Container", "Successfully killed container.", 0x00ff00)])

    @base.subcommand(sub_cmd_name="restart", sub_cmd_description=generic_reason)
    @interactions.check(config.has_perms_async)
    async def restart(self, ctx: interactions.SlashContext, bot: bot_option):
        # Restarts a bot by its container name
        bot_info = config.get_bot(bot)
        container = self.fetch_container(bot)
        if not container or not bot_info:
            return await ctx.send(embeds=[no_container_embed()])

        if not config.check_bot_specific_perms(ctx, bot_info):
            return await ctx.send(embeds=[no_perms_embed()])

        message = await ctx.send(
            embeds=[self.container_embed(bot, "Restart Container", "Restarting...", 0x21304a)])
        container.restart()
        await message.edit(
            embeds=[self.container_embed(bot, "Restart Container", "Successfully restarted bot.", 0x00ff00)])

    @base.subcommand(sub_cmd_name="pull", sub_cmd_description=generic_reason)
    @interactions.check(config.has_perms_async)
    async def pull(self, ctx: interactions.SlashContext, bot: bot_option):
        # Pulls any changes from the registry, and creates a new container
        bot_info = config.get_bot(bot)
        if not bot_info:
            return await ctx.send(embeds=[no_container_embed()])
        
        if not config.check_bot_specific_perms(ctx, bot_info):
            return await ctx.send(embeds=[no_perms_embed()])

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
            real_tag = bot_info['tag'] if "tag" in bot_info else "latest"
            print(bot_info)
            print(real_tag)
            self.client.images.pull(repository=image, tag=real_tag)
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
                "io.portainer.accesscontrol.teams": config.bot_group
            }
            self.client.containers.run(name=bot, image=image+":"+real_tag, network=bot_info['network'], volumes=volumes, labels=labels, ports=ports, restart_policy=restart_policy, detach=True)
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
            
def setup(client):
    Watchman(client)
