import discord
from discord.ext import commands
from discord.utils import get
from discord.errors import Forbidden
from dotenv import load_dotenv
from traceback import format_exc
import os
import json
from json import JSONDecodeError
import random
import requests
import pywizlight as pwl
import asyncio
import time
from webcolors import CSS3_NAMES_TO_HEX

status = "around with the lights!"
versionnum = "Alpha 0.2"
updatetime = "2024/05/08 06:55"
changes = "**(Alpha 0.2)** Hex codes now possible"
path = os.getcwd()
print(f"Lightbot v{versionnum}")
print(updatetime)
print("I'm havin fun!")
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
#TOKEN = os.getenv('TEST_TOKEN')
intents=discord.Intents.default()
intents.message_content=True
client = commands.Bot(intents=intents)
css_colors = CSS3_NAMES_TO_HEX

async def get_lights():
    bulbs = await pwl.discovery.discover_lights(broadcast_space="192.168.1.255")
    return bulbs

#Load list of guilds
with open(f'{path}\\guilds.txt',"r+") as file:
    try:
        text = file.read()
        if len(text) > 1:
            guilds = text.split("\n")
            for serverID in guilds:
                serverID = int(serverID)
        else:
            print("Error! Guilds not loaded!")
            guilds = []
    except IndexError:
        print("Error! Guilds not loaded!")
    file.close()

#Load list of guilds
with open(f'{path}\\bulbs.txt',"r+") as file:
    bulbs = []
    try:
        text = file.read()
        if len(text) > 1:
            bulb_ips = text.split("STOPIP")[0].split("\n")
            bulb_ports = text.split("STOPIP")[1].split("STOPPORT")[0].split("\n")
            bulb_macs = text.split("STOPPORT")[1].split("STOPMAC")[0].split("\n")
            for index, ip in enumerate(bulb_ips):
                if ip == '':
                    bulb_ips.pop(index)
            for index, port in enumerate(bulb_ports):
                if port == '':
                    bulb_ports.pop(index)
            for index, mac in enumerate(bulb_macs):
                if mac == '':
                    bulb_macs.pop(index)
        else:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            try:
                bulbs = asyncio.run(get_lights())
            except RuntimeError:
                pass
            bulb_list = ""
            for bulb in bulbs:
                bulb_list += f"{bulb.ip}\n"
            bulb_list += "STOPIP\n"
            for bulb in bulbs:
                bulb_list += f"{bulb.port}\n"
            bulb_list += "STOPPORT\n"
            for bulb in bulbs:
                bulb_list += f"{bulb.mac}\n"
            bulb_list += "STOPMAC\nALLDONE"
            file.write(bulb_list)
    except IndexError:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        try:
            bulbs = asyncio.run(get_lights())
        except RuntimeError:
            pass
        bulb_list = ""
        for bulb in bulbs:
            bulb_list += f"{bulb.ip}\n"
        bulb_list += "STOPIP\n"
        for bulb in bulbs:
            bulb_list += f"{bulb.port}\n"
        bulb_list += "STOPPORT\n"
        for bulb in bulbs:
            bulb_list += f"{bulb.mac}\n"
        bulb_list += "STOPMAC\nALLDONE"
        file.write(bulb_list)
    print("Bulb list loaded!")
    file.close()

number_choices = ["all"]
for x in range(len(bulb_ips)):
    number_choices.append(f"Light {x+1}")

@client.slash_command(description="Turn on a light!", guild_ids=guilds)
async def turn_on(ctx: discord.Interaction, light: discord.Option(str, choices=number_choices), color, brightness): 
    await ctx.response.defer()
    # if ctx.author.id in [120396380073099264, 1189313967831646278, 737489390238040144]:
    if light == "all":
        for ip in bulb_ips:
            try:
                target_light = pwl.wizlight(ip)
            except IndexError:
                await ctx.respond("Error: invalid light number given!")
            try:
                brightness = int(brightness)
            except ValueError:
                await ctx.respond("Error: non-number given as brightness parameter!")
            if brightness > 255:
                brightness = 255
            try:
                hex = css_colors[str(color)].lstrip('#')
            except KeyError:
                await ctx.respond("Error: Invalid color! Do /colorlist to view a list of all valid colors!")
            rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
            
            await target_light.turn_on(pwl.PilotBuilder(brightness=brightness, rgb=rgb))
            
    else:
        try:
            light_index = int(light.split(" ")[1])-1
        except ValueError:
            await ctx.respond("Error: non-number given as light parameter!")
        try:
            target_light = pwl.wizlight(bulb_ips[light_index])
        except IndexError:
            await ctx.respond("Error: invalid light number given!")
        try:
            brightness = int(brightness)
        except ValueError:
            await ctx.respond("Error: non-number given as brightness parameter!")
        if brightness > 255:
            brightness = 255
        try:
            hex = css_colors[str(color)].lstrip('#')
        except KeyError:
            await ctx.respond("Error: Invalid color! Do /colorlist to view a list of all valid colors!")
        rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
        
        await target_light.turn_on(pwl.PilotBuilder(brightness=brightness, rgb=rgb))
    await ctx.respond("Done!")
    """ else:
        await ctx.respond("Error: user not authorized") """

@client.slash_command(description="Turn off a light or all lights!", guild_ids=guilds)
async def turn_off(ctx: discord.Interaction, light: discord.Option(str, choices=number_choices)): 
    await ctx.response.defer()
    # if ctx.author.id in [120396380073099264, 1189313967831646278, 737489390238040144]:
    if light == "all":
        for ip in bulb_ips:
            try:
                target_light = pwl.wizlight(ip)
            except IndexError:
                await ctx.respond("Error: invalid light number given!")
            await target_light.turn_off()
            
    else:
        try:
            light_index = int(light.split(" ")[1])-1
        except ValueError:
            await ctx.respond("Error: non-number given as light parameter!")
        try:
            target_light = pwl.wizlight(bulb_ips[light_index])
        except IndexError:
            await ctx.respond("Error: invalid light number given!")
        await target_light.turn_off()
    await ctx.respond("Done!")
    """ else:
        await ctx.respond("Error: user not authorized") """
    

@client.slash_command(description="Change the brightness of a light!", guild_ids=guilds)
async def change_brightness(ctx: discord.Interaction, light: discord.Option(str, choices=number_choices), brightness): 
    await ctx.response.defer()
    # if ctx.author.id in [120396380073099264, 1189313967831646278, 737489390238040144]:
    if light == "all":
        for ip in bulb_ips:
            try:
                target_light = pwl.wizlight(ip)
            except IndexError:
                await ctx.respond("Error: invalid light number given!")
            try:
                brightness = int(brightness)
            except ValueError:
                await ctx.respond("Error: non-number given as brightness parameter!")
            if brightness > 255:
                brightness = 255
            await target_light.turn_on(pwl.PilotBuilder(brightness=brightness))
    else:
        try:
            light_index = int(light.split(" ")[1])-1
        except ValueError:
            await ctx.respond("Error: non-number given as light parameter!")
        try:
            target_light = pwl.wizlight(bulb_ips[light_index])
        except IndexError:
            await ctx.respond("Error: invalid light number given!")
        try:
            brightness = int(brightness)
        except ValueError:
            await ctx.respond("Error: non-number given as brightness parameter!")
        if brightness > 255:
            brightness = 255
        await target_light.turn_on(pwl.PilotBuilder(brightness=brightness))
    await ctx.respond("Done!")
    """ else:
        await ctx.respond("Error: user not authorized") """

@client.slash_command(description="Change the color of a light!", guild_ids=guilds)
async def change_color(ctx: discord.Interaction, light: discord.Option(str, choices=number_choices), color): 
    await ctx.response.defer()
    #if ctx.author.id in [120396380073099264, 1189313967831646278, 737489390238040144]:
    if light == "all":
        for ip in bulb_ips:
            try:
                target_light = pwl.wizlight(ip)
            except IndexError:
                await ctx.respond("Error: invalid light number given!")
            if str(color)[0] == "#":
                hex = str(color).lstrip('#')
            else:
                try:
                    hex = css_colors[str(color)].lstrip('#')
                except KeyError:
                    await ctx.respond("Error: Invalid color! Enter a hex code starting with '#', or do /colorlist to view a list of all valid colors!")
                    return
            rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
            await target_light.turn_on(pwl.PilotBuilder(rgb=rgb))
    else:
        try:
            light_index = int(light.split(" ")[1])-1
        except ValueError:
            await ctx.respond("Error: non-number given as light parameter!")
        try:
            target_light = pwl.wizlight(bulb_ips[light_index])
        except IndexError:
            await ctx.respond("Error: invalid light number given!")
        if str(color)[0] == "#":
            hex = str(color).lstrip('#')
        else:
            try:
                hex = css_colors[str(color)].lstrip('#')
            except KeyError:
                await ctx.respond("Error: Invalid color! Enter a hex code starting with '#', or do /colorlist to view a list of all valid colors!")
                return
        rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
        await target_light.turn_on(pwl.PilotBuilder(rgb=rgb))
    await ctx.respond("Done!")
    '''else:
        await ctx.respond("Error: user not authorized")'''

@client.slash_command(description="Change the brightness of a light!", guild_ids=guilds)
async def colorlist(ctx: discord.Interaction): 
    await ctx.respond("Here's a list of all valid colors for this bot:\nhttps://pastebin.com/KazLAXJX")

#Changes bot's status and announces (to me) that it's online
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=f"{status}"))
    #global report 
    #report = client.get_channel(1213349040050409512)
    print('Bot is online!')

client.run(TOKEN)