from config import *
from generate_embed import *
from utils import *
from view import MyView
from reminder import Reminder
import discord
from discord.ext import commands
import traceback

openai.api_key = OPENAI_TOKEN


class Bot(commands.Bot):
    def __init__(self):
        self.view: MyView
        self.view = None

        intents = discord.Intents.all()
        super().__init__(command_prefix="!", intents=intents)

    async def on_ready(self):
        await self.tree.sync()
        print(f'Logged in as {self.user}')

        try:
            data = load_pickle("generated_forms/current_form.json")

            self.view = MyView(data["WipeInfo"], data["UserResponses"], (await (await self.fetch_channel(TRACKING_CHANNEL_ID)).fetch_message(data["TrackingMessageID"])), id=data["ViewFormID"], initialized=True)
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)
            print("Failed to load previous form.")

            self.view = MyView()
        self.add_view(self.view)

client = Bot()

@client.tree.command(name="wipe_form", description="Creates a new wipe roll call.")
async def wipeform(ctx: discord.Interaction, server_name: str, server_ip: str, wipe_time: str):

    if not (await check_permissions(ctx)):
        return

    client.view.stop()
    open("generated_forms/current_form.json", "w").close()

    server_name = server_name.capitalize()
    wipe_time = await format_datetime(wipe_time)
    embed = await generate_embed(wipe_time, server_name, server_ip)

    client.view = MyView(
        {"WipeTime": wipe_time, "WipeName": server_name}, initialized=True)
    client.view.id = (await ctx.channel.send(embed=embed, view=client.view)).id

    tracking_channel = client.get_channel(TRACKING_CHANNEL_ID)

    if tracking_channel:
        tracking_embed = discord.Embed(
            title="Roll Call Tracker", description="No one has reacted yet.", color=discord.Color.gold())
        tracking_message = await tracking_channel.send(embed=tracking_embed)
        client.view.tracking_message = tracking_message

    await client.view.update_tracking_embed(ctx.guild)
    await ctx.response.send_message("Success.", ephemeral=True)


@client.tree.command(name="send_reminder", description="Send a reminder to all members who have not responded to the wipe roll call yet.")
async def send_reminder(ctx: discord.Interaction):

    if not (await check_permissions(ctx)):
        return

    if not client.view:
        await ctx.response.send_message("Create a wipe roll call first.", ephemeral=True)
        return

    await Reminder.send_reminder_dm(ctx=ctx, response_list=client.view.user_choices.keys(), send_message=True)


@client.tree.command(name="unresponsive", description="Show a list of all members who have not reacted.")
async def unreacted(ctx: discord.Interaction):
    if not (await check_permissions(ctx)):
        return

    if not client.view:
        await ctx.response.send_message("Create a wipe roll call first.", ephemeral=True)

    print(client.view.user_choices)

    await Reminder.send_reminder_dm(ctx=ctx, response_list=client.view.user_choices.keys(), send_message=False)


@client.tree.command(name="add_response", description="Add a member response manually.")
async def add_response(ctx: discord.Interaction, user: discord.User, response: str):

    if not (await check_permissions(ctx)):
        return

    if not client.view:
        await ctx.response.send_message("Couldn't find a form to add a response to. Please create a form first.", ephemeral=True)
        return

    if response.capitalize() in ["Yes", "No", "Late", "Unsure"]:
        await client.view.manual_callback(ctx, user, response.capitalize())
    else:
        await ctx.response.send_message("Invalid response. Please enter only 'Yes', 'No', 'Late', or 'Unsure'.")

client.run(token=DISCORD_TOKEN)
