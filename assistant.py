from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from config import *

app = Client(
    "assistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

pytgcalls = PyTgCalls(app)

# ─────────────────────
# STATES
boost_mode = False
volume_level = 100

# ─────────────────────
# FFmpeg logic
def get_ffmpeg():
    global boost_mode, volume_level

    if boost_mode:
        return "-af volume=1.25, equalizer=f=120:width_type=o:width=2:g=2, equalizer=f=3000:width_type=o:width=2:g=1"

    return f"-af volume={volume_level/100}"

# ─────────────────────
# /sit → VC join
@app.on_message(filters.command("sit") & filters.user(OWNER_ID))
async def sit(_, msg):
    try:
        await pytgcalls.join_group_call(
            msg.chat.id,
            AudioPiped("silence.mp3")
        )
        await msg.reply("🎧 VC me join ho gaya (silent mode)")
    except Exception as e:
        await msg.reply(f"Error: {e}")

# ─────────────────────
# /play → reply audio play
@app.on_message(filters.command("play") & filters.user(OWNER_ID))
async def play(_, msg):
    if not msg.reply_to_message:
        return await msg.reply("Reply to audio/recording!")

    file = await msg.reply_to_message.download()

    stream = AudioPiped(
        file,
        ffmpeg_parameters=get_ffmpeg()
    )

    await pytgcalls.change_stream(msg.chat.id, stream)
    await msg.reply("▶️ Playing in VC")

# ─────────────────────
# /boost toggle
@app.on_message(filters.command("boost") & filters.user(OWNER_ID))
async def boost(_, msg):
    global boost_mode
    boost_mode = not boost_mode
    await msg.reply(f"⚡ Boost mode: {boost_mode}")

# ─────────────────────
# /volume set
@app.on_message(filters.command("volume") & filters.user(OWNER_ID))
async def volume(_, msg):
    global volume_level

    try:
        volume_level = int(msg.text.split()[1])
        await msg.reply(f"🔊 Volume set: {volume_level}")
    except:
        await msg.reply("Use: /volume 50")

# ─────────────────────
# /mute
@app.on_message(filters.command("mute") & filters.user(OWNER_ID))
async def mute(_, msg):
    await pytgcalls.pause_stream(msg.chat.id)
    await msg.reply("🔇 Muted")

# ─────────────────────
# /unmute
@app.on_message(filters.command("unmute") & filters.user(OWNER_ID))
async def unmute(_, msg):
    await pytgcalls.resume_stream(msg.chat.id)
    await msg.reply("🎤 Unmuted")

# ─────────────────────
# START
app.start()
pytgcalls.start()
print("🚀 VC Assistant Running...")
app.idle()
