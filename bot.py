import os
import asyncio
from datetime import datetime, time, timedelta
from dotenv import load_dotenv
from telegram import Bot, ChatPermissions
from telegram.error import TelegramError

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID"))

HORA_INICIO = time(2, 0)
HORA_FIN = time(9, 0)
ultimo_estado = None

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

def hora_a_datetime(hora: time) -> datetime:
    ahora = datetime.now()
    return datetime.combine(ahora.date(), hora)

def tiempo_para_proximo_cambio() -> int:
    ahora = datetime.now()
    inicio = hora_a_datetime(HORA_INICIO)
    fin = hora_a_datetime(HORA_FIN)

    if inicio > fin:
        # Horario pasa por la medianoche (ej: 23:00 a 06:00)
        if ahora < fin:
            inicio -= timedelta(days=1)
        else:
            fin += timedelta(days=1)

    if ahora < inicio:
        return int((inicio - ahora).total_seconds())
    elif ahora < fin:
        return int((fin - ahora).total_seconds())
    else:
        return int((inicio + timedelta(days=1) - ahora).total_seconds())

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

        # Ajusta el tiempo de espera dinámicamente
        segundos = tiempo_para_proximo_cambio()
        espera = 60 if segundos <= 300 else min(3600, segundos // 2)  # Espera menos si está cerca
        await asyncio.sleep(espera)

async def main():
    bot = Bot(BOT_TOKEN)
    await check_and_update_permissions(bot)

if __name__ == "__main__":
    asyncio.run(main())
