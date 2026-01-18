import discord
import os
import asyncio
import sys

CONFIG_FILE = "config.txt"

def cargar_config():
    config = {}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    config[k] = v

    token = config.get("TOKEN")
    g_id = config.get("GUILD_ID")
    v_id = config.get("VOICE_ID")

    if not token or not g_id or not str(g_id).isdigit():
        token = input("INTRODUCE TU TOKEN DE USUARIO: ").strip()
        g_id = input("ID DEL SERVIDOR: ").strip()
        v_id = input("ID DEL CANAL DE VOZ: ").strip()
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(f"TOKEN={token}\nGUILD_ID={g_id}\nVOICE_ID={v_id}")

    return token.strip(), int(g_id), int(v_id)

class UserSelfBot(discord.Client):
    def __init__(self, g_id, v_id):
        # Inicialización sin 'intents' explícitos para evitar el AttributeError que tenías
        super().__init__()
        self.target_g = g_id
        self.target_v = v_id
        self.vc = None 

    async def on_ready(self):
        print(f"\n✅ CUENTA DE USUARIO ACTIVA: {self.user}")
        
        # --- BARRA DE CARGA ANIMADA ---
        espera = 5 
        print(f"🚀 Iniciando protocolos de voz para cuenta personal...")
        for i in range(espera + 1):
            porcentaje = int((i / espera) * 100)
            lleno = "█" * (i * 4)
            vacio = "░" * ((espera - i) * 4)
            sys.stdout.write(f"\rProgreso: |{lleno}{vacio}| {porcentaje}%")
            sys.stdout.flush()
            await asyncio.sleep(1)
        print("\n")
        # ------------------------------

        canal = self.get_channel(self.target_v)
        if not canal:
            try:
                canal = await self.fetch_channel(self.target_v)
            except:
                pass

        if canal:
            try:
                # Conectar y ensordecer (self_deaf)
                self.vc = await canal.connect(self_deaf=True)
                print(f"🎧 ÉXITO: Tu cuenta ya está en '{canal.name}'")
            except Exception as e:
                print(f"❌ ERROR DE VOZ: {e}")
        else:
            print("❌ ERROR: Canal no encontrado. Revisa los IDs.")

    async def close(self):
        if self.vc and self.vc.is_connected():
            print("\n👋 Cerrando sesión y saliendo del canal...")
            await self.vc.disconnect(force=True)
        await super().close()

async def main():
    token, g_id, v_id = cargar_config()
    client = UserSelfBot(g_id, v_id)
    try:
        # Aquí NO ponemos bot=False para evitar el error 'unexpected keyword argument'
        # discord.py-self ya sabe que es una cuenta de usuario.
        await client.start(token)
    except discord.LoginFailure:
        print("\n❌ EL TOKEN ES INCORRECTO. Revisa el config.txt")
    except Exception as e:
        print(f"\n❌ ERROR GENERAL: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
