
from watchman import Watchman
from helpCommand import PrettyHelp
from configLoader import Config
from discord.ext import commands
splash = """
 __          __   _       _                           
 \ \        / /  | |     | |                          
  \ \  /\  / /_ _| |_ ___| |__  _ __ ___   __ _ _ __  
   \ \/  \/ / _` | __/ __| '_ \| '_ ` _ \ / _` | '_ \ 
    \  /\  / (_| | || (__| | | | | | | | | (_| | | | |
     \/  \/ \__,_|\__\___|_| |_|_| |_| |_|\__,_|_| |_|
      A minimal bot manager for BuildTheEarth™                                                                                                    
"""


config = Config("config.json")
bot = commands.Bot(command_prefix=config.prefix,
                   help_command=PrettyHelp(config))
bot.add_cog(Watchman(bot, config))


print(splash)
print("Logging into Portainer!")
config.login_portainer()
print("Successfully logged into Portainer!")
print("Starting Watchman")
bot.run(config.token)
