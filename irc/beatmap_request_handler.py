import asyncio
import irc
import re
import requests
import json

# https://old.ppy.sh/p/irc
BANCHO_IRC_USERNAME = ""
BANCHO_IRC_PASSWORD = ""

# https://old.ppy.sh/p/api
OSU_API_KEY = ""

# https://twitchapps.com/tmi/
TWITCH_IRC_USERNAME = ""
TWITCH_IRC_PASSWORD = ""


loop = asyncio.get_event_loop()

bancho_client = irc.Client(irc.Endpoint(host="cho.ppy.sh", port=6667, ssl=False))
bancho_credentials = irc.Credentials(username=BANCHO_IRC_USERNAME, password=BANCHO_IRC_PASSWORD)

twitch_client = irc.Client(irc.Endpoint(host="irc.chat.twitch.tv", port=6697, ssl=True))
twitch_credentials = irc.Credentials(username=TWITCH_IRC_USERNAME, password=TWITCH_IRC_PASSWORD)

def connect(client) -> None:
    loop.create_task(client.connect())


def login(client, credentials) -> None:
    client.send(irc.Pass(credentials.password))
    client.send(irc.Nick(credentials.username))


@bancho_client.on("CONNECT")
async def on_bancho_connect() -> None:
    login(bancho_client, bancho_credentials)


@bancho_client.on("PING")
def on_bancho_ping(ping: irc.Ping) -> None:
    pong = irc.Pong(ping.message)
    bancho_client.send(pong)


@bancho_client.on("PRIVMSG")
def on_bancho_privmsg(privmsg: irc.Privmsg) -> None:
    print(
        f"Bancho | User: {privmsg.user} | Target: {privmsg.target} | Message: {privmsg.message}"
    )


@bancho_client.on("CONNECTION_CLOSED")
def on_bancho_connection_closed() -> None:
    print("LOST CONNECTION")
    connect(bancho_client)


@twitch_client.on("CONNECT")
async def on_twitch_connect() -> None:
    login(twitch_client, twitch_credentials)
    twitch_client.send(irc.Join(channel=TWITCH_IRC_USERNAME))


@twitch_client.on("PRIVMSG")
def on_twitch_privmsg(privmsg: irc.Privmsg) -> None:
    print(
        f"Twitch | User: {privmsg.user} | Target: {privmsg.target} | Message: {privmsg.message}"
    )
    undetermined_link = re.match("^https:\/\/osu.ppy.sh\/beatmapsets", privmsg.message)
    if (undetermined_link):
        if (re.search("#osu", privmsg.message)):
            is_b_link = True
            is_s_link = False
        else:
            is_b_link = False
            is_s_link = True

    else:
        is_b_link = bool(re.match("(^https:\/\/osu.ppy.sh\/b\/)|(^https:\/\/old.ppy.sh\/b\/)|(^https:\/\/osu.ppy.sh\/beatmaps)", privmsg.message))
        is_s_link = bool(re.match("(^https:\/\/osu.ppy.sh\/s\/)|(^https:\/\/old.ppy.sh\/s\/)", privmsg.message))

    if (is_b_link | is_s_link):
        beatmapmessage = privmsg.user + " > [" 
        is_beatmap_id = re.search("\d+$", privmsg.message)
        if(is_beatmap_id): 
            beatmap_id = is_beatmap_id.group(0)
            param = '&b=' if is_b_link else '&s='
            beatmap_info = json.loads(requests.get('https://osu.ppy.sh/api/get_beatmaps?k=' + OSU_API_KEY + param + beatmap_id).text)
            metadata_string = beatmap_info[0]["artist"] + " - " + beatmap_info[0]["title"] + " (" + beatmap_info[0]["version"] + ")"
            beatmapmessage += "https://osu.ppy.sh/b/" + beatmap_info[0]["beatmap_id"] + " " + metadata_string + "]" 
            bancho_client.send(irc.Privmsg(target=BANCHO_IRC_USERNAME, message=beatmapmessage))
            twitch_client.send(irc.Privmsg(target="#" + TWITCH_IRC_USERNAME, message=metadata_string))




@twitch_client.on("PING")
def on_twitch_ping(ping: irc.Ping) -> None:
    pong = irc.Pong(ping.message)
    twitch_client.send(pong)


connect(bancho_client)
connect(twitch_client)
loop.run_forever()