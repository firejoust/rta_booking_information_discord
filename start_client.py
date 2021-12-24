import json
import discord
import asyncio
from scrape_availability import getTimeslots

# configuration
settings = json.load(open('settings.json'))
centres = json.load(open('centres.json'))
history = []
# globals
client = discord.Client()
channel = None
active = True

# login event
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    print('Make sure to register your message channel with "$register" first!')

# message event
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$register'):
        global channel
        channel = message.channel
        await message.channel.send('Channel registered! Available timeslots will be sent here.')
        print('Channel', channel, 'has been registered.')

    elif message.content.startswith('$stop'):
        global active
        active = False
        await message.channel.send('Shutting down!')
        await client.close()
        print('Client "{0.user}" has been deactivated via $stop command.'.format(client))

# filter re-used timeslots
def refactorTimeslots(location, timeslots):
    refactored = []
    # determine unique timeslots
    for timeslot in timeslots:
        uuid = location + "@" + timeslot
        # append unique timeslot to refactored list
        if not uuid in history:
            refactored.append(timeslot)
    return refactored

# add new timeslots to history
def addHistoryTimeslots(location, timeslots):
    global history
    for timeslot in timeslots:
        uuid = location + "@" + timeslot
        history.append(uuid)

# inform user of new timeslots
async def announceTimeslots(results):
    message = ""
    # append new timeslots to discord message
    for centre in results:
        timeslots = refactorTimeslots(centre['location'], centre['timeslots'])

        # centre has available timeslots
        if len(timeslots) > 0:
            centre_name = centres[centre['location']]
            message += f"\n\n{centre_name}:"

            # concatenate new timeslots to the message
            for timeslot in timeslots:
                message += f"\n- {timeslot}"

        # avoid announcing duplicate timeslots
        addHistoryTimeslots(centre['location'], timeslots)

    # non-blank message indicates new timeslots have been found
    if message != '':
        await channel.send('Timeslots are available!' + message)

async def update():
    while active:
        await asyncio.sleep(settings['refresh_timer'])
        # verify discord channel is registered
        if channel is None:
            continue
        results = await getTimeslots()
        # check that no issues were encountered whilst retrieving timeslots
        if results is None:
            continue
        await announceTimeslots(results)

def init():
    loop = asyncio.get_event_loop()
    loop.create_task(update())
    loop.create_task(client.run(settings['token']))

if __name__ == '__main__':
    init()