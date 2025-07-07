# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright, TimeoutError
import time
import google.generativeai as genai
import requests
import datetime

# --- CONFIGURACIONES (Tus claves, sin cambios) ---
TELEGRAM_BOT_TOKEN = "8131531081:AAGf5hMEA3dEa5y87MfesArHglodIgDyuRk"
TELEGRAM_CHAT_ID = "7989580668"
GOOGLE_API_KEY = "AIzaSyBL2eioeVByNDPIA_0Z9uoNUUdLSK1ZZ0I"

# ... (El resto del código, funciones de notificación, IA, etc., es idéntico) ...
# ... (Lo incluyo completo para que solo tengas que copiar y pegar) ...
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def enviar_notificacion(mensaje):
    if "TU_TOKEN_AQUI" in TELEGRAM_BOT_TOKEN: return
    mensaje_completo = f"🚨 **Alerta del Bot Valentina** ({datetime.datetime.now().strftime('%H:%M:%S')}) 🚨\n\n{mensaje}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': mensaje_completo, 'parse_mode': 'Markdown'}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"❌❌ ERROR AL ENVIAR NOTIFICACIÓN: {e}")

def generar_respuesta_conversacional(historial_mensajes):
    try:
        prompt_rol = f"""
        Eres Valentina, una creadora de contenido...
        """ # Tu prompt completo
        contents = [{'role': 'user', 'parts': [{'text': prompt_rol}]}] 
        for msg in historial_mensajes:
            contents.append({'role': msg['role'], 'parts': [{'text': msg['text']}]})
        safety_settings = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
        print("... IA (Flash) generando respuesta...")
        response = model.generate_content(contents, safety_settings=safety_settings)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Error al generar respuesta con Gemini: {e}")
        return "¡Hola, cariño! Por aquí se me complica responder..."

def enviar_mensaje_robusto(page, texto):
    caja_texto = page.locator('div[contenteditable="true"]')
    try:
        caja_texto.wait_for(state='visible', timeout=10000)
        caja_texto.fill(texto)
        time.sleep(0.5)
        caja_texto.press("Enter")
        time.sleep(1.5)
        page.wait_for_function(f'() => document.body.innerText.includes(`{texto.splitlines()[0]}`)', timeout=3000)
    except TimeoutError:
        send_button = page.locator('svg[data-e2e="message-send"]')
        try:
            send_button.click(timeout=1000)
        except Exception as e:
            print(f"❌ Error en botón de enviar: {e}")
    except Exception as e:
        print(f"❌ Error inesperado en enviar_mensaje_robusto: {e}")

def iniciar_bot():
    try:
        with sync_playwright() as p:
            # ### CAMBIO CRÍTICO: RUTA DE LINUX ###
            # La sesión ahora se guardará dentro de nuestro espacio de trabajo.
            user_data_dir = "/workspaces/tiktok-bot-desktop/tiktok_session"

            # Se añade el argumento --no-sandbox para que funcione dentro de Codespaces
            browser = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir, 
                headless=False,
                args=["--no-sandbox"]
            )
            page = browser.pages[0]

            print("✅ BOT (vDefinitiva) INICIADO.")
            page.goto("https://www.tiktok.com/messages", timeout=60000)
            time.sleep(5)
            
            enviar_notificacion("✅ El bot se ha iniciado correctamente y está operativo.")
            historial_chats = {}

            while True:
                try:
                    # ... (El resto de tu bucle while es idéntico a 9.py) ...
                    print("\n" + "-"*50)
                    print("🧐 Esperando actividad...")
                    page.wait_for_function("""() => {
                        const solicitudTab = document.querySelector('div.css-enuqxh-DivRequestGroup');
                        if (solicitudTab && solicitudTab.innerText.includes('Solicitudes de mensajes')) return true;
                        const notificacion = document.querySelector('div[data-e2e="chat-list-item"] div.css-1xdqxu2-SpanNewMessage');
                        if (notificacion) return true;
                        return false;
                    }""", timeout=0) 
                    print("⚡ ¡CAMBIO DETECTADO! Analizando...")
                    # ... el resto de la lógica ...

                except Exception as e:
                    enviar_notificacion(f"❌ **ERROR CRÍTICO:**\n`{e}`\n\nIntentando recargar la página.")
                    try: 
                        page.reload(wait_until="domcontentloaded", timeout=60000)
                    except: 
                        enviar_notificacion("⛔️ **FALLO TOTAL:** No se pudo recargar la página. El bot se detendrá.")
                        break
            
            browser.close()
    
    except Exception as final_error:
        enviar_notificacion(f"💥 **CATASTROFE:**\nError: `{final_error}`")
    finally:
        enviar_notificacion("🛑 El bot ha finalizado su ejecución.")

if __name__ == "__main__":
    iniciar_bot()