from datetime import datetime
import discord
import config

async def generate_embed(date:datetime, server_name:str, server_ip:str) -> discord.Embed:
    print(date.timestamp())
    data = {
        "id": 10674342,
        "title": "Wipe Roll Call",
        "description": "**Yes:** You will be available at server wipe.\n**No:** You will __not__ be available at server wipe and might __not__ be playing later.\n**Late:** You will __not__ be available at server wipe, but will be playing later.\n**Unsure:** You don't know yet. You can update your status anytime.",
        "color": 10582,
        "fields": [
            {
                "id": 229391369,
                "name": "Wipe Information",
                "value": f"**Name:** {server_name}\n**Server IP:** {server_ip}\n**Date:** <t:{int(date.timestamp())}:F>\n**Server Wipes:** <t:{int(date.timestamp())}:R>"
            },
            {
                "id": 51300238,
                "name": "",
                "value": f"<@&{config.MEMBER_ID}>",
                "inline": False
            }
        ],
        "timestamp": date.today().timestamp()
    }

    embed = discord.Embed(title=data["title"], description=data["description"], color=data["color"])
    embed.timestamp = datetime.fromtimestamp(data["timestamp"])

    for field in data["fields"]:
        embed.add_field(name=field["name"], value=field["value"].format(server_name=server_name, server_ip=server_ip, date=date), inline=field.get("inline", True))
    
    return embed
