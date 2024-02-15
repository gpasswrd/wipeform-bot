import discord
from config import *
from typing import *

message = """
You haven't responded to the wipe roll call yet.
Please select an option in <#1186785720174649414> when you have the time. Thanks.
"""


class Reminder:
    async def __init__(self, client):
        self.client = client

    async def send_reminder_dm(ctx: discord.Interaction, response_list, send_message):
        member_list = ctx.guild.members

        dm_list: List[discord.User]
        dm_list = []

        for member in member_list:
            if MEMBER_ID in [role.id for role in member.roles]:
                if member.id in response_list:
                    continue
                else:
                    dm_list.append(member)

        if dm_list and send_message:
            await ctx.response.send_message(f"Reminders sent to users: {', '.join(  [ f'<@{user.id}>' for user in dm_list]  )}", ephemeral=False)
        elif dm_list:
            await ctx.response.send_message(f"Users who have not responded: {', '.join(  [ f'<@{user.id}>' for user in dm_list]  )} ", ephemeral=False)
        else:
            await ctx.response.send_message("Everyone has already responded.", ephemeral=False)

        if not send_message:
            return

        for member in dm_list:
            await (await member.create_dm()).send(content=message)
            print("reminder sent")
