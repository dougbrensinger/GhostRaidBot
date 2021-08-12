#!/usr/local/bin/python3

import os

import discord
from bot_config import *
from logic import *

client = discord.Client()
dToken = os.environ.get('TOKEN')
activeRaids = dict()


@client.event
async def on_ready():
    print('RaidBot ready, Logged in as {0.user}.'.format(client))


@client.event
async def on_message(message):
    author = message.author
    if author == client.user:
        return
    elif message.content.startswith(raidCommand):
        msg = raidLobby(message)
        if author in activeRaids:
            content = author.name + " already is raiding, !close it."
            await message.channel.send(content)
        else:
            if msg.invites > 10:
                content = "Unable to create raids with more than 10 invites"
                await message.channel.send(content=content)
            else:
                inv = msg.invites
                content = "%s raiding with %d invites" % (author.mention, inv)
                if len(msg.monster) > 0:
                    content += " against %s" % (" ".join(msg.monster))
                if msg.targets:
                    content += "\n   <@&%d>" % msg.targets
                content += "\n vvv Tap to Join (%d Invites Remaining)" % inv
                reply = await message.channel.send(content)
                await reply.add_reaction(emoji)
                await reply.add_reaction(leave)
                # Creating the channel
                srv = message.guild
                leader = message.author.name
                chanName = "raid-" + leader
                default = message.guild.default_role
                defaultOverwrites[default] = hidden
                defaultOverwrites[message.guild.me] = visibl
                defaultOverwrites[message.author] = visibl

                msg.channel = await srv.create_text_channel(
                    chanName, overwrites=defaultOverwrites,
                    topic='Auto Raid Channel - Leader is %s' % leader,
                    reason='This is a private room!')
                print("DEBUG | We made a channel:", msg.channel)
                activeRaids[author] = (msg, reply)

        try:
            await message.delete()
        except discord.errors.Forbidden:
            print("DEBUG | We don't have permissions to manage chan messages.")

    elif message.content.startswith(closeCommand):
        if author not in activeRaids:
            content = "%s isn't hosting a raid." % author.name
            await message.delete()
            await message.channel.send(content)
        else:
            raid = activeRaids[author]
            chan = raid[0].channel
            try:
                await raid[1].delete()
                await message.delete()
            except discord.errors.Forbidden:
                print("DEBUG | Couldn't delete the message, deleted early?")
            try:
                await chan.delete()
                del activeRaids[author]
            except discord.errors.Forbidden:
                await channel.send("Permission Error, delete manually.")

    elif message.content.startswith(readyCommand):
        if author not in activeRaids:
            content = "%s isn't hosting a raid." % author.name
            await message.delete()
            await message.channel.send(content)
        else:
            raid = activeRaids[author]
            invites = raid[0].raiders
            if len(invites) > 0:
                names = list()
                pings = list()
                for user in invites:
                    names.append(user.name)
                    pings.append(user.mention)
                copypaste = ",".join(names)
                autopings = " ".join(pings)
                await message.channel.send("Raid Starting! " + autopings)
                await message.channel.send(copypaste)
            else:
                await message.channel.send("No raiders found. Check Logs")
                print("DEBUG | Original Members List - ", chan.members)

@client.event
async def on_reaction_add(reaction, user):
    if reaction.emoji == emoji:
        if user == client.user:
            return
        else:
            leader = reaction.message.mentions[0]
            print("DEBUG | User (%s) reacted to join %s's raid room" % (user, leader))
            if leader in activeRaids:
                channel = activeRaids[leader][0].channel
                raiders = activeRaids[leader][0].raiders
                print("DEBUG | Attempt to join raid, Open Slots:", activeRaids[leader][0].invites)
                if activeRaids[leader][0].invites > 0:
                    if user in raiders:
                        print("DEBUG | Attempted to Join when already in, ignoring")
                        return
                    raiders.append(user)
                    perms = channel.overwrites_for(user)
                    perms.send_messages=True
                    print("DEBUG | Open spot found w/", leader, "so I'm adding them.")
                    await channel.set_permissions(user, overwrite=perms)
                    await channel.send("%s joined the raid room" % user.mention)

                    reply = activeRaids[leader][1]
                    rText = reply.content
                    remain = rText.split("(")
                    newRemain = int(remain[1].split(" ")[0]) - 1
                    if newRemain > 0:
                        newContent = remain[0] + "(" + str(newRemain) + " invites remaining)"
                    else:
                        rText1 = rText.split("vvv")[0]
                        newContent = rText1 + "(Raid Full - 0 Invites Remaining)"
                    await reply.edit(content=newContent)
                    activeRaids[leader][0].invites = newRemain
                else:
                    print("DEBUG | Ignoring attempt to join the full lobby of", leader)
            else:
                print("DEBUG | No raid found for", leader, "ignoring.")
    elif reaction.emoji == leave:
        if user == client.user:
            return
        else:
            leader = reaction.message.mentions[0]
            print("DEBUG | User (%s) reacted to leave %s's raid room" % (user, leader))
            if leader in activeRaids:
                channel = activeRaids[leader][0].channel
                raiders = activeRaids[leader][0].raiders
                if user not in raiders:
                    print("DEBUG | Attempted to leave when not in, ignoring")
                    return
                
                raiders.remove(user)
                perms = channel.overwrites_for(user)
                perms.send_messages=False
                await channel.set_permissions(user, overwrite=perms)
                await channel.send("%s left the raid room" % user.mention)

                reply = activeRaids[leader][1]
                rText = reply.content
                remain = rText.split("(")
                newRemain = int(remain[1].split(" ")[0]) + 1
                if newRemain > 1:
                    newContent = remain[0] + "(" + str(newRemain) + " invites remaining)"
                else:
                    rText1 = rText.split("(")[0]
                    newContent = rText1 + "\n vvv Tap to Join (%d Invites Remaining)" % newRemain
                await reply.edit(content=newContent)
                activeRaids[leader][0].invites = newRemain
            else:
                print("DEBUG | No raid found for", leader, "ignoring.")

""" This isn't working, saving the code for if it does
@client.event
async def on_reaction_remove(reaction, user):
    if user == client.user:
        return
    else:
        leader = reaction.message.mentions[0]
        print("DEBUG | User (%s) reacted to leave %s's raid room" % (user, leader))
        if leader in activeRaids:
            print("DEBUG | Raid found for", leader, " so I'm removing user.")
            autoraid = activeRaids[leader][0]
            overwrites = autoraid.channel.overwrites
            del overwrites[user]
            await channel.edit(overwrites=overwrites)
        else:
            print("DEBUG | No raid found for", leader, "ignoring.")
"""
client.run(dToken)
