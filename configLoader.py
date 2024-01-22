import json
import interactions


class Config:
    def __init__(self, config_file):
        self.config_file = json.load(open(config_file))
        self.token = self.config_file["token"]
        self.bot_group = self.config_file["botGroup"]
        self.bots = self.config_file["bots"]
        self.prefix = self.config_file["prefix"]
        self.roles = self.config_file["roles"]
        self.users = self.config_file["users"]
        self.error_channel = self.config_file["error_channel"]

    def listBots(self):
        return list(self.bots.keys())

    def getBot(self, name):
        return self.bots.get(name)

    def hasPerms(self, ctx):
        for i in self.users:
            if str(ctx.author.id) == i:
                return True
        return False
    async def hasPermsAsync(self, ctx):
        for i in self.users:
            if str(ctx.author.id) == i:
                return True
        return False
