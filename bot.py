import os
from telegram import Bot, ChatPermissions
from datetime import datetime, time
import asyncio
from dotenv import load_dotenv

# Carga las variables de entorno
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

# ⏰ Horario de restricción (2:00 a.m. a 9:00 a.m.)
HORA_INICIO = time(2, 0)
HORA_FIN = time(9, 0)

ultimo_estado = None  # Para evitar mensajes duplicados

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
            if esta_dentro_horario:
                await bot.set_chat_permissions(
                    chat_id=GROUP_ID,
                    permissions=ChatPermissions(
                        can_send_messages=False,
                        can_send_media_messages=False,
                        can_send_other_messages=False,
                        can_add_web_page_previews=False
                    )
                )
                await bot.send_message(GROUP_ID, "🚫") #El grupo ha sido silenciado. Solo los administradores pueden enviar mensajes.
            else:
                await bot.set_chat_permissions(
                    chat_id=GROUP_ID,
                    permissions=ChatPermissions(
                        can_send_messages=True,
                        can_send_media_messages=True,
                        can_send_other_messages=True,
                        can_add_web_page_previews=True
                    )
                )
                await bot.send_message(GROUP_ID, "✅ ") #El grupo ha sido reactivado. Todos pueden enviar mensajes.

            ultimo_estado = nuevo_estado

        await asyncio.sleep(3600)

async def main():
    bot = Bot(BOT_TOKEN)
    await check_and_update_permissions(bot)

if __name__ == '__main__':
    asyncio.run(main())
