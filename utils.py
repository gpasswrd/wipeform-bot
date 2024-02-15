import openai
from datetime import datetime
import zoneinfo
from discord import Interaction
import json


async def format_datetime(input_datetime):
    response = openai.chat.completions.create(
        model="ft:gpt-3.5-turbo-1106:personal::8Y36n6UT",
        messages=[
            {"role": "system", "content": f"Convert the following to the format 'YYYY-MM-DD HH:MM:SS'. If you cannot convert to a date, fill in a random date or make an estimate. Do not write anything other than a formatted date.\n The current date is {datetime.now()}"},
            {"role": "user", "content": input_datetime}
        ])

    print(response.choices)
    formatted_string = response.choices[0].message.content
    return datetime.strptime(formatted_string.strip(), "%Y-%m-%d %H:%M:%S").replace(tzinfo=zoneinfo.ZoneInfo("America/New_York"))


async def check_permissions(ctx: Interaction):
    if ctx.permissions.manage_channels == False:
        await ctx.response.send_message("Insufficient permissions.", ephemeral=True)
        return False
    return True


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)


def store_pickle(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, cls=DateTimeEncoder)


def load_pickle(file_path):

    try:
        with open(file_path, "r") as file:
            loaded_data = json.load(file)
            print(loaded_data)
            wipe_info = loaded_data["WipeInfo"]
            if loaded_data and isinstance(wipe_info["WipeTime"], str):
                try:
                    wipe_info["WipeTime"] = datetime.fromisoformat(
                        wipe_info["WipeTime"])
                except ValueError:
                    print("failed load_pickle()")
                    pass

            loaded_data["UserResponses"] = {int(
                userID): response for userID, response in loaded_data["UserResponses"].items()}
            print(loaded_data)

            return loaded_data

    except Exception as e:
        print(e.with_traceback())
        return {}
