import json
import interactions


class Config:
    def __init__(self, config_file):
        self.config_file = json.load(open(config_file, encoding="utf-8-sig"))
        self.token = self.config_file["token"]
        self.bot_group = self.config_file["botGroup"]
        self.bots = self.config_file["bots"]
        self.prefix = self.config_file["prefix"]
        self.roles = self.config_file["roles"]
        self.users = set(self.config_file["users"]) #This is largely unnecessary, but S P E E D
        self.error_channel = self.config_file["error_channel"]

    def list_bots(self):
        return list(self.bots.keys())

    def get_bot(self, name):
        return self.bots.get(name)

    def has_perms_base(self, ctx):
        return str(ctx.author.id) in self.users
    
    def has_perms_container(self, ctx):
        for bot in self.bots:
            if 'users' in bot:
                return str(ctx.author.id) in bot.users
        return False

    async def has_perms_async(self, ctx):
        return has_perms_base(ctx) or has_perms_container(ctx)

    def check_bot_specific_perms(self, ctx, bot_info):
        if self.has_perms_base(ctx):
            return True
        elif 'users' in bot_info:
            if str(ctx.author.id) in bot_info.users:
                return True
        return False