from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, app_commands
from discord.ext import commands
from random import randint

#Load token from .env file
load_dotenv()
TOKEN: Final[str] = os.getenv("DISCORD_TOKEN")
print(TOKEN)

#Initialise discord bot settings
intents: Intents = Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

#Initialise variables for scene register
scene_counts  = []
scene_channels = []
scene_messages = []
scenes_register_message : Message = None


#Return a register of all scene names and their current scene numbers
def display_register() -> str:
    scene_names = list(map(lambda x: x.name, scene_channels))
    display_text = ""
    for i in range(len(scene_names)):
        display_text += f"{scene_names[i]}: {scene_counts[i]} \n"
    
    return display_text

#Edit previously sent register message
async def refresh_register () -> None:
    print (scenes_register_message)
    if scenes_register_message != None:
        await scenes_register_message.edit(content=display_register())

#Sync commands when bot run
@bot.event
async def on_ready() -> None:
    print (f'{bot.user} is now running!')
    await bot.tree.sync()


#Tick over a scene in a channel to the next one
@bot.hybrid_command()
async def scene(ctx: commands.Context):
    sceneNo = 1
    sceneIndex = 0
    if ctx.channel in scene_channels:
        sceneIndex = scene_channels.index(ctx.channel)
        scene_counts[sceneIndex] += 1
        sceneNo = scene_counts[sceneIndex]
        await scene_messages[sceneIndex].unpin()
    else:
        scene_channels.append(ctx.channel)
        scene_counts.append(1)
        scene_messages.append(ctx.message)
        sceneIndex = len(scene_counts) - 1
    
    scene_messages[sceneIndex] = await ctx.send(f"# Scene {sceneNo}")
    await scene_messages[sceneIndex].pin()
    await refresh_register()

#Create a scene register in a specified channel
@bot.hybrid_command()
async def create_scene_register (ctx: commands.Context):
    global scenes_register_message
    scenes_register_message = await ctx.send (display_register())
    print (scenes_register_message)

#Run conflict between two mentioned names (as strings, this could possibly be changed to enforce them as users? That might be helpful as a TODO if you want to add conflict validation)
@bot.hybrid_command()
async def run_conflict (ctx: commands.Context, person1: str, person2: str) -> None:
    combatants = [person1, person2]
    victory_int = randint(0,1)
    await ctx.send(f"**{combatants[victory_int]}** won the conflict against **{combatants[1-victory_int]}**")

#Main function
def main() -> None:
    bot.run(token=TOKEN)

#Main
if __name__ == "__main__":
    main()
