import json
import discord
import requests

class Config:
    def __init__(self, config_file):
        self.portainer_token = None
        self.config_file = json.load(open(config_file))
        self.token = self.config_file["token"]
        self.portainer_endpoint = self.config_file["portainerEndpoint"] + "/api"
        self.portainer_username = self.config_file["portainerUsername"]
        self.portainer_password = self.config_file["portainerPassword"]
        self.bots = self.config_file["bots"]
        self.prefix = self.config_file["prefix"]
        self.roles = self.config_file["roles"]
        self.users = self.config_file["users"]

    def login_portainer(self):
        r = requests.post(
            self.portainer_endpoint + "/auth",
            data=json.dumps({"username": self.portainer_username, "password": self.portainer_password}),
            verify=False
        )
        self.portainer_token = r.json().get("jwt")

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
