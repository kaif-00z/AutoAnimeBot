import asyncio
import random
import sys
from traceback import format_exc

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import CreateChannelRequest
from telethon.tl.functions.contacts import UnblockRequest

DATA = {}
ENV = """
API_ID={20793620}
API_HASH={a712d2b8486f26c4dee5127cc9ae0615}
BOT_TOKEN={8008501123:AAFm3TFfH49r4mXdBrfr5cTvODAXeuLz0lM}
SESSION={1BVtsOJIBu6BoHFHPYasRYs4ycsDtl1nci76oms2kQQJdVBrvJtmlgXjZ_903flvsCgc-HV-5si9Jztn-1OcHxTnZaAhbbFSG2D4vDPg62fLVnNcc2vvGn40MqN52qWhFiIZ8ZUI3SvJbwwWGwpxn2dF76rze7SNck65J5CEsj7HFpAD3URgmKxdP-U4ou1Woci69BMS3FYcf-QMEdJwdgjn1aTTHIFmLCNUtv7g_KabKMZZ1AxLaCgtROwwoSc7qDfh6ncbmGtn8WHc3rzQgXUvX624It_ymWgiElO70XI2E63F_GYu8OIo4G9TJjHxGvVBTVt9oI2BOMo9EdiJ5K1kih1a6TXg=}
MAIN_CHANNEL={-1002583222869}
LOG_CHANNEL={-1002534308280}
CLOUD_CHANNEL={-1002663628298}
BACKUP_CHANNEL={-1002569202945}
MONGO_SRV={mongodb+srv://suihioobb:NSIF6uo4u40vLZXE@cluster0.s2utuuh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0}
OWNER={7700556123}
FORCESUB_CHANNEL={-1002323219195}
FORCESUB_CHANNEL_LINK={https://t.me/Weoo_Animes}
"""


async def generate_session_string():
    api_id = int(input("Enter your API_ID: "))
    api_hash = input("Enter your API_HASH: ")
    if api_id and api_hash:
        async with TelegramClient(StringSession(), api_id, api_hash) as client:
            DATA["api_id"] = api_id
            DATA["api_hash"] = api_hash
            DATA["session"] = str(client.session.save())
            return (str(client.session.save()), api_id, api_hash)
    print("API_ID and HASH Not Found!")
    sys.exit(1)


def get_mongo():
    srv = input("Enter your Mongo SRV: ")
    if srv.strip():
        DATA["mongo_srv"] = srv
        return True
    DATA["mongo_srv"] = ""
    return False


def get_forcesub():
    fsub_id = input(
        "Enter ID of Channel Where You Want ForceSub\nNOTE: Bot Is Admin In That Channel: "
    )
    fsub_link = input("Enter Invite Link From Which Subs Will Join The FSUB Channel: ")
    if fsub_id and fsub_link:
        DATA["fsub_id"] = fsub_id
        DATA["fsub_link"] = fsub_link
        return True
    DATA["fsub_link"] = ""
    DATA["fsub_id"] = ""
    return False


async def create_channel(client, title):
    try:
        r = await client(
            CreateChannelRequest(
                title=title,
                about="Made By https://github.com/kaif-00z/AutoAnimeBot",
                megagroup=False,
            )
        )

        created_chat_id = r.chats[0].id
        return f"-100{created_chat_id}"
    except BaseException:
        print("Unable to Create Channel...")
        sys.exit(1)


def generate_env():
    txt = ENV.format(
        DATA["api_id"],
        DATA["api_hash"],
        DATA["bot_token"],
        DATA["session"],
        DATA["Ongoing Anime 2024"],
        DATA["Ongoing Anime Logs"],
        DATA["Ongoing Anime Samples And SS"],
        DATA["Ongoing Anime Backup"],
        DATA["mongo_srv"],
        DATA["owner_id"],
        DATA["fsub_id"],
        DATA["fsub_link"],
    )
    with open(".env", "w") as f:
        f.write(txt.strip())
    print("Succesfully Generated .env File Don't Forget To Save It! For Future Uses.")


async def auto_maker():
    string_session, api_id, api_hash = await generate_session_string()
    print(string_session)
    async with TelegramClient(
        StringSession(string_session), api_id, api_hash
    ) as client:
        print("Creating Bot Account...")
        who = await client.get_me()
        DATA["owner_id"] = who.id
        name = who.first_name + "'s Auto Anime Bot"
        if who.username:
            username = who.username + "_anime_bot"
        else:
            username = "ongoing_anime_" + (str(who.id))[5:] + "_bot"
        bf = "@BotFather"
        await client(UnblockRequest(bf))
        await client.send_message(bf, "/cancel")
        await asyncio.sleep(1)
        await client.send_message(bf, "/newbot")
        await asyncio.sleep(1)
        isdone = (await client.get_messages(bf, limit=1))[0].text
        if isdone.startswith("That I cannot do.") or "20 bots" in isdone:
            print(
                "You Already Made 20 Bots In Your Current Account. You Have To Deleted One Bot To Run This Script."
            )
            sys.exit(1)
        await client.send_message(bf, name)
        await asyncio.sleep(1)
        isdone = (await client.get_messages(bf, limit=1))[0].text
        if not isdone.startswith("Good."):
            print(
                "Please make a Bot from @BotFather and add it's token in BOT_TOKEN, as an env var and restart me."
            )
            sys.exit(1)
        await client.send_message(bf, username)
        await asyncio.sleep(1)
        isdone = (await client.get_messages(bf, limit=1))[0].text
        await client.send_read_acknowledge("botfather")
        if isdone.startswith("Sorry,"):
            ran = random.randint(1, 100)
            username = "ongoing_anime_" + (str(who.id))[6:] + str(ran) + "_bot"
            await client.send_message(bf, username)
            await asyncio.sleep(1)
            isdone = (await client.get_messages(bf, limit=1))[0].text
        if isdone.startswith("Done!"):
            bot_token = isdone.split("`")[1]
            DATA["bot_token"] = bot_token
            print("Succesfully Created Bot Account...")
        print("Creating Channels...")
        for ch_name in [
            "Ongoing Anime Logs",
            "Ongoing Anime 2024",
            "Ongoing Anime Samples And SS",
            "Ongoing Anime Backup",
        ]:
            try:
                chat_id = await create_channel(client, ch_name)
                await asyncio.sleep(3)
                await client.edit_admin(
                    int(chat_id),
                    username,
                    post_messages=True,
                    edit_messages=True,
                    delete_messages=True,
                    ban_users=True,
                    pin_messages=True,
                    add_admins=True,
                )
                DATA[ch_name] = chat_id
            except BaseException:
                print("Error While Creating Channel And Promoting Bot..")
                print(format_exc())
                sys.exit(1)
        print("Succesfully Created Channel...")
        print("Now If You Wana Skip Upcoming Inputs You Can Just Press Enter!!")
        db = get_mongo()
        if not db:
            print("Generating .env Without Mongo SRV. Now You Have To Add it Manually!")
        fsub = get_forcesub()
        if not fsub:
            print(
                "Generating .env Without FSUB Configs. Now You May Have To Add it Manually!"
            )
            print("NOTE: Fsub config is optional!!!")
        generate_env()


asyncio.run(auto_maker())
