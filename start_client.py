import discord
import asyncio
import json
from scrape_availability import retrieveAvailableSlots

client = discord.Client()
channel = None
settings = None
active = True

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
        await message.channel.send('Channel registered! Available timeslots will be sent here.')
        print('Channel', channel, 'has been registered.')
        channel = message.channel

    elif message.content.startswith('$stop'):
        global active
        await message.channel.send('Shutting down!')
        await client.close()
        print('Client "{0.user}" has been deactivated via $stop command.'.format(client))
        active = False

async def update():
    while active:
        if channel != None:
            message = ""
            results = await retrieveAvailableSlots()

            # append new timeslots to discord message
            for center in results:
                if len(center.timeslots) > 0:
                    message += f"{center.location}: {len(center.timeslots)} time(s) available!\n"

            if message != "":
                await channel.send(message)

        await asyncio.sleep(settings['refresh_timer'])

def init():
    global settings
    settings = json.load(open('settings.json'))

    loop = asyncio.get_event_loop()
    loop.create_task(update())
    loop.create_task(client.run(settings['token']))

if __name__ == '__main__':
    init()