import json
import discord


class Config:
    def __init__(self, configFile):
        self.configFile = json.load(open(configFile))
        self.token = self.configFile["token"]
        self.bots = self.configFile["bots"]
        self.prefix = self.configFile["prefix"]
        self.roles = self.configFile["roles"]
        self.users = self.configFile["users"]
        
    def listBots(self):
        return list(self.bots.keys())

    def getBot(self, bot):
        return self.bots.get(bot)

    def hasPerms(self, ctx):
        for i in self.users:
            if str(ctx.author.id) == i:
                return True
        for j in self.roles:
            role = discord.utils.find(
                lambda r: r.id == j, ctx.message.server.roles)
            if role in ctx.message.author.roles:
                return True
        return False
