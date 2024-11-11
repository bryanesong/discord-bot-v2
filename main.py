# bot.py

import heapq
import io
import re
import aiohttp
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import time

import random
from discord.ext import commands
from SECRET import SECRETS,profound_phrases


import os

import discord
from dotenv import load_dotenv

load_dotenv()
# DISCORD_TOKEN = os.getenv()
# print('discord_token',DISCORD_TOKEN)
# if not DISCORD_TOKEN:
# 	print('Discord Token is invalid/null.')
# 	exit()
# GUILD = os.getenv('Polish People\'s Republic')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!',intents=intents)


images = []
@bot.command(name='motivationryker')
async def daily_ryker_photo(ctx):
    if len(images) == 0:
        await ctx.send('Motivation Ryker is currently under maintenance.')
        return
    photo_num = random.randint(0,len(images)-1)
    await ctx.send(images[photo_num])

    phrase_num = random.randint(0,len(profound_phrases)-1)
    await ctx.send(profound_phrases[phrase_num]+"\n-Ryker \"Quartapple\" Kang")

@bot.command(name='rphelp')
async def ryker_points_command_list(ctx):
    embedVar = discord.Embed(
        title=f"Ryker Casino Inc. Command List",
        color=0x00ff00
    )
    embedVar.add_field(name='- Earn RP',value = 'Earn RP by tagging @Ryker!',inline=False)
    embedVar.add_field(name='- View Your Current RP Amount',value = '!rp',inline=False)
    embedVar.add_field(name='- Play at Ryker\'s Casino',value = '!rpcasino <amount_to_bet>',inline=False)
    embedVar.add_field(name='- View RP Leaderboard',value = '!rpleader',inline=False)
    embedVar.set_footer(text="Ryker Casino Inc. is not responsible for any losses. Gamble responsibly.")
    await ctx.send(embed=embedVar)

#returns amount of rykerpoints user has
@bot.command(name='rp')
async def getRykerPointAmount(ctx):
    print('REQUESTING ryker points data.')
    user_id = ctx.author.id
    result = getRykerPointsFromDB(user_id)
    embedVar = discord.Embed(
        title=f"{ctx.author.nick}'s RP (Ryker Points)",
        color=0x00ff00
    )
    embedVar.set_thumbnail(url=(ctx.author.avatar))
    embedVar.add_field(name=result,value = '',inline=True)
    await ctx.send(embed=embedVar)

@bot.command(name='rpcasino')
async def ryker_casino(ctx,arg=''):
    
    print('ARGS:',arg,len(arg))
    if len(arg) < 1:
        await ctx.send('Please use this format: !rykercasino <amount_of_ryker_points_to_bet>, ex: "!rykercasino 15" ')
        return
    
    if not arg.isdigit():
        await ctx.send('Invalid ryker points: !rykercasino <amount_of_ryker_points_to_bet>, ex: "!rykercasino 15" ')
        return
    
    current_user_points = getRykerPointsFromDB(ctx.author.id)
    amount_to_bet = int(arg)
    if amount_to_bet > current_user_points:
        await ctx.send('You do not have enough Ryker Points to play.')
        return
    
    all_custom_emojis = await ctx.guild.fetch_emojis()
    #choose 5 emojis from the custom emojis, this number needs to be larger than or equal to num of all custom emojis
    if len(all_custom_emojis) < 5:
        emoji_possibility_number = len(all_custom_emojis)
    else:
        emoji_possibility_number = 5

    random_emoji_selector = random.sample(all_custom_emojis,emoji_possibility_number)
    

    print('random sampler:',random_emoji_selector)
    #print('all custom emojis test:',all_custom_emojis)
    random_slot1_emoji = random_emoji_selector[random.randint(0,len(random_emoji_selector)-1)]
    random_slot2_emoji = random_emoji_selector[random.randint(0,len(random_emoji_selector)-1)]
    random_slot3_emoji = random_emoji_selector[random.randint(0,len(random_emoji_selector)-1)]

    embedVar = discord.Embed(
        title=f"Ryker (Legal) Casino",
        color=0x00ff00
    )
    embedVar.set_thumbnail(url=(ctx.author.avatar))
    embedVar.add_field(name=f"Ryker Slot Machine: [{random_slot1_emoji}]",value = '')
    embedVar.set_footer(text="Ryker Casino Inc. is not responsible for any losses. Gamble responsibly.")
    
    cur_msg = await ctx.send(embed=embedVar)
    time.sleep(1)
    
    #await cur_msg.edit(content=f"Ryker Slot Machine: {random_slot1_emoji} {random_slot2_emoji}")
    embedVar = discord.Embed(
        title=f"Ryker (Legal) Casino",
        color=0x00ff00
    )
    embedVar.set_thumbnail(url=(ctx.author.avatar))
    embedVar.set_footer(text="Ryker Casino Inc. is not responsible for any losses. Gamble responsibly.")
    embedVar.add_field(name=f"Ryker Slot Machine: [{random_slot1_emoji}] [{random_slot2_emoji}]",value = '')
    await cur_msg.edit(embed=embedVar)
    time.sleep(1)

    #await cur_msg.edit(content=f"Ryker Slot Machine: {random_slot1_emoji} {random_slot2_emoji} {random_slot3_emoji}")
    embedVar = discord.Embed(
        title=f"Ryker (Legal) Casino",
        color=0x00ff00
    )
    embedVar.set_thumbnail(url=(ctx.author.avatar))
    embedVar.set_footer(text="Ryker Casino Inc. is not responsible for any losses. Gamble responsibly.")
    embedVar.add_field(name=f"Ryker Slot Machine: [{random_slot1_emoji}] [{random_slot2_emoji}] [{random_slot3_emoji}]",value = '')
    await cur_msg.edit(embed=embedVar)

    if random_slot1_emoji.id == random_slot2_emoji.id == random_slot3_emoji.id:
        addRykerPointsInDB(ctx.author.id,amount_to_bet*2)
        await ctx.send(f'Congratulations! You have won {amount_to_bet*2} Ryker Points. You now have: {current_user_points+(amount_to_bet*2)} Ryker Points.')
    else:
        addRykerPointsInDB(ctx.author.id,-1 * amount_to_bet)
        await ctx.send(f'Better luck next time. You now have {current_user_points-(amount_to_bet)} Ryker Points.')

#view ryker point leaderboard
@bot.command(name='rpleader')
async def ryker_casino(ctx):
    user_id_points = getAllUsersWithRykerPoints()
    if not user_id_points:
        embedVar = discord.Embed(
            title=f"Ryker Points Leaderboard",
            color=0x00ff00
        )
        embedVar.description = "Leaderboard is Empty."
        await ctx.send(embed=embedVar)
        return
    user_id_points_sorted = []
    heapq.heapify(user_id_points_sorted)
    for discord_user_id,points in user_id_points.items():
        heapq.heappush(user_id_points_sorted,(-1*points,discord_user_id))

    embedVar = discord.Embed(
        title=f"Ryker Points Leaderboard",
        color=0x00ff00
    )
    embedVar.description = '' 
    counter = 1
    while user_id_points_sorted:
        cur_user_stats = heapq.heappop(user_id_points_sorted)
        user = bot.get_user(cur_user_stats[1])
        embedVar.description += f"{counter}. {user.display_name} - {cur_user_stats[0]*-1} RP\n"
        counter+=1
        if counter == 6:
            break
    await ctx.send(embed=embedVar)
    return

#ryker user id: 160443396991877121
#mrchen user id (testing purposes): 126788668051554304
@bot.event
async def on_message(message):
    #print('message:',message)
    for mention in message.mentions:
        print('mention_id:',mention.id)
        if mention.id == 160443396991877121 or mention.id == 126788668051554304:
            await message.channel.send('Ryker was mentioned! +5 RP')
            addRykerPointsInDB(message.author.id,5)

    await bot.process_commands(message)
        

'''
NEW FEATURES TODO:
- RykerPoints
    - everytime you tag ryker, you get 5 ryker points
    - if ryker reacts to your message, you get 10 ryker points

'''


#https://raw.githubusercontent.com/bryanesong/dailyrykerphotostorage/refs/heads/main/20231203_100151.jpg
#

# @bot.command(name='help')
# async def daily_ryker_photo(ctx):
#     await ctx.send("Stop asking for help. \n-Ryker \"Quartapple\" Kang")

def addRykerPointsInDB(discord_user_id: str, points_to_be_added: int):
    try:
        uri = SECRETS["mongo_uri"]
        client = MongoClient(uri,
                            username= SECRETS["username"],
                            password=SECRETS["password"])
        database = client["ryker_ecosystem"]
        collection = database["ryker_points"]
        if not discord_user_id:
            raise Exception("Attemped to retrieve from DB with empty id str:",discord_user_id)
        
        if collection.count_documents({'discord_id':discord_user_id}):
            old_values = collection.find_one({'discord_id':discord_user_id})
            print('OLD VALUES:',old_values)
            print('OLD POINTS',old_values['points'])

            result = collection.update_one(
                {
                    'discord_id':discord_user_id
                },
                {
                    "$set":{
                        'discord_id': discord_user_id,
                        'points': (old_values['points']+points_to_be_added)
                    }
                }
            )
            print(f'Found and updated existing entry:({discord_user_id})')
        else:
            result = collection.insert_one({
                'discord_id': discord_user_id,
                'points': points_to_be_added
            })
            print('discord_user_id not found, creating new one')
        print('RESULT',result)
        client.close()

    except Exception as e:
        raise Exception("The following error occurred: ", e)
    
def getRykerPointsFromDB(discord_user_id: str):
    try:
        uri = SECRETS["mongo_uri"]
        client = MongoClient(uri,
                            username= SECRETS["username"],
                            password=SECRETS["password"])
        database = client["ryker_ecosystem"]
        collection = database["ryker_points"]
        if not discord_user_id:
            raise Exception("Attemped to retrieve from DB with empty id str:",discord_user_id)
        

        query = collection.find_one(
            {'discord_id':discord_user_id}
        )
        print('GET query results:',query)
        client.close()
        if query:
            print(f'Found existing entry:({discord_user_id})')
            return query['points']
        else:
            print('discord_user_id not found, creating new one')
            print('ERROR:',query)
            return 0
        
    except Exception as e:
        raise Exception("The following error occurred: ", e)

def getAllUsersWithRykerPoints()->dict:
    try:
        uri = SECRETS["mongo_uri"]
        client = MongoClient(uri,
                            username= SECRETS["username"],
                            password=SECRETS["password"])
        database = client["ryker_ecosystem"]
        collection = database["ryker_points"]

        result = {}
        for entry in collection.find({}):
            if entry['discord_id'] == 730273841221468280:
                #this is BearyBot himself, his score does not count
                continue
            result[entry['discord_id']] = entry['points']
        return result
    except Exception as e:
        raise Exception("The following error occurred: ", e)
    

def getAllPossibleRykerPhotos():
    driver = webdriver.Firefox()
    driver.get('https://github.com/bryanesong/dailyrykerphotostorage')
    html_source = driver.page_source
    if not html_source:
        print('ERROR: Cannot get page info.')
        driver.quit()
        exit()
    
    soup = BeautifulSoup(html_source,"html.parser")

    t = soup.find("table",attrs={"aria-labelledby":"folders-and-files"})
    if not t:
        print('Could not find photos table on github.')
        exit()

    photos_list = t.find_all("tr")
    
    for photo in photos_list[1:len(photos_list)-1]:
        temp = photo.find("a",attrs={"class":"Link--primary"})
        print('temp',temp)
        if temp:
            print("PHOTO LINE ",temp['href'])
            image_id = temp['href'].split("/")[-1]
            print("image_id",image_id)
            images.append("https://raw.githubusercontent.com/bryanesong/dailyrykerphotostorage/refs/heads/main/"+image_id)
        print("-------------")
    
    print("CURRENT AMOUNT OF RYKER PHOTOS:",len(images))




#getAllPossibleRykerPhotos()
bot.run(SECRETS['discord_token'])