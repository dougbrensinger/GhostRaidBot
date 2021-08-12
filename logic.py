#!/usr/local/bin/python3

import discord
from bot_config import legendary, mega, nonlegendary

roles = {
    "legendary": legendary,
    "mega": mega,
    "nonlegendary": nonlegendary,
    "non": nonlegendary,
    "non-legendary": nonlegendary
}

hidden = discord.PermissionOverwrite(view_channel=False)
visibl = discord.PermissionOverwrite(view_channel=True)
defaultOverwrites = dict()


class raidLobby(object):
    async def __init__(self, message):
        self.message = message
        self.invites = 5
        self.raiders = list()
        self.targets = None
        self.monster = list()

        self.channel = None

        self.parse()

    async def parse(self):
        parts = str(self.message.content).split(" ")
        for part in parts:
            try:
                limit = int(part)
                self.invites = limit
                continue
            except ValueError:
                try:
                    self.targets = roles[part]
                    continue
                except KeyError:
                    if part == raidCommand:
                        continue
                    else:
                        self.monster.append(part.capitalize())

    async def findRaidLobby(self, leader):
        pass

    async def createPost(self, leader):
        pass

    async def lobbyCreate(self, leader):
        pass

    async def lobbyJoin(self, leader):
        pass

    async def lobbyLeave(self, leader):
        pass
