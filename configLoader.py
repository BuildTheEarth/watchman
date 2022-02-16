import json
import discord


class Config:
    def __init__(self, config_file):
        self.config_file = json.load(open(config_file))
        self.token = self.config_file["token"]
        self.bot_group = self.config_file["botGroup"]
        self.bots = self.config_file["bots"]
        self.prefix = self.config_file["prefix"]
        self.roles = self.config_file["roles"]
        self.users = self.config_file["users"]

    def listBots(self):
        return list(self.bots.keys())

    def getBot(self, name):
        return self.bots.get(name)

    def hasPerms(self, ctx):
        for i in self.users:
            if str(ctx.author.id) == i:
                return True
        for j in self.roles:
            role = discord.utils.find(
                lambda r: r.id == j, ctx.message.guild.roles)
            if role in ctx.message.author.roles:
                return True
        return False
