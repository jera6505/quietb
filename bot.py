import os
import asyncio
from datetime import datetime, time
from dotenv import load_dotenv
from telegram import Bot, ChatPermissions
from telegram.error import TelegramError

# Carga variables de entorno (.env)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

# Horario de restricción (2:00 a.m. a 9:00 a.m.)
HORA_INICIO = time(3, 0)
HORA_FIN = time(10, 0)

# Estado anterior para evitar mensajes duplicados
ultimo_estado = None

# Permisos: modo silencioso (solo admins pueden enviar mensajes)
silent_permissions = ChatPermissions(
    can_send_messages=False,
    can_send_audios=False,
    can_send_documents=False,
    can_send_photos=False,
    can_send_videos=False,
    can_send_video_notes=False,
    can_send_voice_notes=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False
)

# Permisos: modo normal (todos pueden enviar mensajes)
active_permissions = ChatPermissions(
    can_send_messages=True,
    can_send_audios=False,
    can_send_documents=True,
    can_send_photos=True,
    can_send_videos=True,
    can_send_video_notes=False,
    can_send_voice_notes=False,
    can_send_polls=False,
    can_send_other_messages=True,
    can_add_web_page_previews=False
)

async def check_and_update_permissions(bot: Bot):
    global ultimo_estado
    while True:
        ahora = datetime.now().time()

        esta_dentro_horario = (
            HORA_INICIO <= ahora or ahora <= HORA_FIN if HORA_INICIO > HORA_FIN
            else HORA_INICIO <= ahora <= HORA_FIN
        )

        nuevo_estado = "bloqueado" if esta_dentro_horario else "permitido"

        if nuevo_estado != ultimo_estado:
            try:
                permisos = silent_permissions if nuevo_estado == "bloqueado" else active_permissions
                await bot.set_chat_permissions(chat_id=GROUP_ID, permissions=permisos)

                mensaje = "🚫 El grupo ha sido silenciado." if nuevo_estado == "bloqueado" else \
                          "✅ El grupo ha sido reactivado."
                await bot.send_message(chat_id=GROUP_ID, text=mensaje)

                print(f"[{datetime.now()}] Estado actualizado: {nuevo_estado.upper()}")
                ultimo_estado = nuevo_estado
            except TelegramError as e:
                print(f"❌ Error al actualizar permisos: {e}")

        await asyncio.sleep(60)

async def main():
    bot = Bot(BOT_TOKEN)
    await check_and_update_permissions(bot)

if __name__ == "__main__":
    asyncio.run(main())
