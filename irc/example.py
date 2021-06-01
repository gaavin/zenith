import asyncio
import irc

# https://old.ppy.sh/p/irc
BANCHO_IRC_USERNAME = ""
BANCHO_IRC_PASSWORD = ""

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
    bancho_client.send(irc.Join(channel="osu"))


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
    twitch_client.send(irc.Join(channel="gav_asdf"))


@twitch_client.on("PRIVMSG")
def on_twitch_privmsg(privmsg: irc.Privmsg) -> None:
    print(
        f"Twitch | User: {privmsg.user} | Target: {privmsg.target} | Message: {privmsg.message}"
    )


@twitch_client.on("PING")
def on_twitch_ping(ping: irc.Ping) -> None:
    pong = irc.Pong(ping.message)
    twitch_client.send(pong)


connect(bancho_client)
connect(twitch_client)
loop.run_forever()