from typing import Final
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, app_commands
from discord.ext import commands
from random import randint, random
import time

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
    display_text = "# Current Scene Numbers: \n"
    for i in range(len(scene_names)):
        display_text += f"**{scene_names[i]}**: Scene **{scene_counts[i]}** \n"
    
    return display_text

#Edit previously sent register message
async def refresh_register () -> None:
    global scenes_register_message
    print (scenes_register_message)
    if scenes_register_message != None:
        try:
            await scenes_register_message.edit(content=display_register())
        except Exception:
            correct_channel = scenes_register_message.channel
            await scenes_register_message.delete()
            scenes_register_message = await correct_channel.send(display_register())
            
#Sync commands when bot run
@bot.event
async def on_ready() -> None:
    print (f'{bot.user} is now running!')
    await bot.tree.sync()


#Tick over a scene in a channel to the next one
@bot.hybrid_command(name="scene", description="Start a new Scene in this channel")
async def scene(ctx: commands.Context):
    crew = ctx.guild.get_role(1259434112784007292)
    gm = ctx.guild.get_role(1259434112784007293)
    if crew in ctx.author.roles or gm in ctx.author.roles:
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
    else:
        await ctx.send("You do not have the permissions to do that!")

@bot.hybrid_command(name="get_help", description="Request for help, adjudication, or clarification")
async def get_help(ctx: commands.Context, message: str):
    crew_channel = await bot.fetch_channel(1259434115875213323) # replace with crew channel ID
    at_user = ctx.author.mention
    crew = ctx.guild.get_role(1259434112784007292)  # replace with actual crew role ID in live server
    at_crew = crew.mention
    await ctx.reply(
        f"Your response has been sent to the game team, {at_user}. "
        f"The game team are checking and will get back to you soon. "
        f"\nThe message you sent: \n> _{message}_"
    )
    await crew_channel.send(
        f"{at_crew} you got a request from username '**{ctx.author.name}**', "
        f"server nickname at time of sending '**{ctx.author.nick}**'. "
        f"\nMessage sent from: {ctx.channel.jump_url}"
        f"\nMessage sent: \n> _{message}_"
    ) 

#Create a scene register in a specified channel
@bot.hybrid_command(name="create_scene_register", description="Create a Scene register in this channel")
async def create_scene_register (ctx: commands.Context):
    crew = ctx.guild.get_role(1259434112784007292)
    gm = ctx.guild.get_role(1259434112784007293)
    if crew in ctx.author.roles or gm in ctx.author.roles:
        global scenes_register_message
        scenes_register_message = await ctx.send (display_register())
        print (scenes_register_message)
    else:
        await ctx.send("You do not have the permissions to do that!")

#Run conflict between two mentioned names (as strings, this could possibly be changed to enforce them as users? That might be helpful as a TODO if you want to add conflict validation)
@bot.hybrid_command(name="run_conflict", description="Run a conflict between person 1 and person 2")
async def run_conflict (ctx: commands.Context, person1: str, person2: str) -> None:
    combatants = [person1, person2]
    victory_int = randint(0,1)
    await ctx.send(f"**{combatants[victory_int]}** won the conflict against **{combatants[1-victory_int]}**")

@bot.hybrid_command(name="use_charge", description="Flips a coin to test whether you run out of charges")
async def use_charge (ctx: commands.Context) -> None:
    outcome = ["You've run out of charges on this!", "You've still got charges left!"]
    await ctx.send (outcome[randint(0,1)])

@bot.hybrid_command(name="bombonomicon", description="Bombonomicon")
async def use_charge (ctx: commands.Context, target:str) -> None:
    if ctx.author.id == 315019410337300483:
        outcome = [f"The Bombonomicon explodes **{target}**!", "The Bombonomicon explodes **Bimbrundo** himself!"]
        await ctx.send (outcome[randint(0,1)])
    else:
        await ctx.send ("You don't own that Item!")

@bot.hybrid_command(name="disintegrate", description="Disintegrating pistol")
async def use_charge (ctx: commands.Context) -> None:
    if ctx.author.id == 723282487157063801:
        randomval = random()
        print(randomval)
        outcome = "The disintegrating ray is ready to fire!" if randomval < 0.75 else "The disintegrating ray has disintegrated!"
        await ctx.send (outcome)
    else:
        await ctx.send ("You don't own that Item!")

@bot.hybrid_command(name="gamble", description="Roll the dice")
async def use_charge (ctx: commands.Context, rigged: bool) -> None:
    randomval = randint(1,38) if not rigged else randint(1,1000)
    print(randomval)
    outcome = f"The roulette wheel has come up with **{randomval}** (out of 38)."

    roulette_msg = await ctx.send(f"The roulette wheel is spinning... \n {randint(1,38)} out of 38")
    time.sleep(0.2)
    for i in range(0,8):
        await roulette_msg.edit(content=f"The roulette wheel is spinning... \n {randint(1,38)} out of 38")
        time.sleep(0.2)
    await roulette_msg.edit(content=outcome)

@bot.hybrid_command(name="craft_request", description="Request to do crafting")
async def craft_request(ctx: commands.Context, components: str, craft_plan: str):
    crew_channel = await bot.fetch_channel(1259434115875213324)
    at_user = ctx.author.mention
    gm_role = ctx.guild.get_role(1259434112784007293)
    at_gm = gm_role.mention
    await ctx.reply(
        f"Your response has been sent to the game team, {at_user}. "
        f"The game team are checking and will get back to you soon. "
        f"\nComponent(s) listed: _{components}_"
        f"\nThe crafting plan sent: \n> _{craft_plan}_"
    )
    await crew_channel.send(
        f"{at_gm} you got a request from username '**{ctx.author.name}**', "
        f"server nickname at time of sending '**{ctx.author.nick}**'. "
        f"\nMessage sent from: {ctx.channel.jump_url}"
        f"\nComponent(s) listed: _{components}_"
        f"\nCrafting plan sent: \n> _{craft_plan}_"
    )

#Main function
def main() -> None:
    bot.run(token=TOKEN)

#Main
if __name__ == "__main__":
    main()
