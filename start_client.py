import discord
import asyncio
import json

client = discord.Client()
channel = None
settings = None

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    print('Make sure to register your message channel with "$register" first!')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$register'):
        global channel
        channel = message.channel
        print("Channel", channel, "has been registered.")
        await message.channel.send('Channel registered! Available timeslots will be sent here.')

async def update():
    while True:
        await asyncio.sleep(settings["refresh_timer"])

def init():
    global settings
    settings = json.load(open("settings.json"))

    loop = asyncio.get_event_loop()
    loop.create_task(update())
    loop.create_task(client.run(settings["token"]))

if __name__ == "__main__":
    init()