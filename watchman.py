import interactions

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


config = Config("config.json")
bot = interactions.Client(token=config.token)
bot.load_extension("bot", None, config)

print(splash)
print("Starting Watchman")
bot.start()
