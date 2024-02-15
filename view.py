import discord
from sheets import *
from utils import *
from config import *

current_active_view = None


class MyView(discord.ui.View):
    def __init__(self, wipe_info: dict = None, user_choices: dict = {}, tracking_message: discord.Message = None, initialized: bool = False, id: int = None):
        super().__init__(timeout=None)

        self.user_choices = user_choices
        self.tracking_message = tracking_message
        self.wipe_info = wipe_info
        self.initialized = initialized
        self.id = id

    @staticmethod
    async def send_error(interaction: discord.Interaction):
        message = f"Failed to add response. Ask a lead to regenerate the form."
        await interaction.response.send_message(message, ephemeral=True)
        return

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success, custom_id="Yes")
    async def yes_button_callback(self, interaction: discord.Interaction, button):
        await self.button_callback("Yes", interaction)

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger, custom_id="No")
    async def no_button_callback(self, interaction: discord.Interaction, button):
        await self.button_callback("No", interaction)

    @discord.ui.button(label="Late", style=discord.ButtonStyle.primary, custom_id="Late")
    async def late_button_callback(self, interaction: discord.Interaction, button):
        await self.button_callback("Late", interaction)

    @discord.ui.button(label="Unsure", style=discord.ButtonStyle.secondary, custom_id="Unsure")
    async def unsure_button_callback(self, interaction: discord.Interaction, button):
        await self.button_callback("Unsure", interaction)

    async def button_callback(self, button_label=None, interaction: discord.Interaction = None):

        if not self.initialized:
            print("Error: Not Initialized")
            await self.send_error(interaction)
            return

        if not (self.id == interaction.message.id):
            print("Error: Interaction ID mismatch")
            # await self.send_error(interaction)
            return

        user_id = interaction.user.id
        self.user_choices[user_id] = button_label  # Update to the new choice

        if (await self.update_tracking_embed(interaction.guild)):
            message = f"Your response {button_label} has been recorded. Thank you."
            if button_label == "No":
                message = message + \
                    "\nEven though you selected No, feel free to still join us whenever you're available."

            await interaction.response.send_message(message, ephemeral=True)

        else:
            await self.send_error(interaction)

    async def manual_callback(self, interaction: discord.Interaction, user: discord.User, button_label):
        print(user)
        self.user_choices[user.id] = button_label
        if (await self.update_tracking_embed(interaction.guild)):
            await interaction.response.send_message(f"Added {button_label} as response for user {user.display_name}", ephemeral=True)
        else:
            await interaction.response.send_message(f"Failed to add response. Please regenerate the form.", ephemeral=True)

    async def update_tracking_embed(self, guild: discord.Guild):
        if not self.wipe_info:
            return False

        embed = discord.Embed(title="Roll Call Tracker",
                              description=f"For {self.wipe_info['WipeName']} at <t:{int(self.wipe_info['WipeTime'].timestamp())}:F>", color=discord.Color.gold())
        for label in ["Yes", "No", "Late", "Unsure"]:
            user_names = []
            for uid, choice in self.user_choices.items():
                if choice == label:
                    member = guild.get_member(uid)
                    if member:
                        user_names.append(member.display_name)
            embed.add_field(name=label, value='\n'.join(
                user_names) or 'No one yet', inline=True)

        data = {
            "WipeInfo": self.wipe_info,
            "UserResponses": self.user_choices,
            "TrackingMessageID": self.tracking_message.id,
            "ViewFormID": self.id
        }

        store_pickle(data, f"generated_forms/current_form.json")
        print(self.user_choices)

        if self.tracking_message:
            try:
                # await update_google_sheet(self)
                await self.tracking_message.edit(embed=embed)
            except Exception as e:
                print(e)
                return False

        return True
