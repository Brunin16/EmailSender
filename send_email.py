import os
from dotenv import load_dotenv
load_dotenv()
import smtplib
import logging
import requests
from inspirational_quotes import quote
from datetime import datetime
import asyncio
from googletrans import Translator
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def translate_text(text):
    translator = Translator()
    translated = translator.translate(text, dest='pt')
    return translated.text

def send_email(config,msg):
    with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as smtp:
        smtp.starttls()
        smtp.login(config['user'], config['password'])
        smtp.send_message(msg)
    logging.info(f"Email enviado para {msg['To']} com sucesso!")

def get_quote():
    return quote().get("quote")

def get_audio_freesound(configs):
    key = configs.get("freesound_api_key")
    if not key:
        raise RuntimeError("FREESOUND_API_KEY não definido no ambiente")
    params = {
        "query": "laugh",
        "fields": "previews",
        "page_size": 1,
        "token": key
    }
    resp = requests.get(configs["freesound_search_url"], params=params)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        raise RuntimeError("Nenhum áudio encontrado no Freesound")
    audio_url = results[0]["previews"]["preview-hq-mp3"]
    audio_resp = requests.get(audio_url)
    audio_resp.raise_for_status()
    return audio_resp.content

def get_imgmeme():
    meme_resp = requests.get(os.getenv("MEME_API_URL"))
    meme_resp.raise_for_status()
    meme_url = meme_resp.json()["url"]
    return requests.get(meme_url).content

def get_configs():
    return {
            "user":        os.getenv("USER_EMAIL"),
            "password":    os.getenv("PASS_EMAIL"),
            "smtp_server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port":   int(os.getenv("SMTP_PORT", 587)),
            "freesound_search_url": os.getenv("FREESOUND_SEARCH_URL"),
            "freesound_api_key":   os.getenv("FREESOUND_API_KEY"),
            }

def get_receivers():
    return ["bruedu.cp16@gmail.com"]

def create_MIMEImage(image):
    img = MIMEImage(image)
    img.add_header("Content-Disposition", 'attachment; filename="meme.jpg"')
    return img

def create_mime_audio(audio_bytes, filename="risada.mp3"):
    audio = MIMEAudio(audio_bytes, _subtype="mp3")
    audio.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    return audio

def create_text(texts):
    today = datetime.now().day

    if today < 20:
        remain = 20 - today
        default = f"Faltam {remain} dias para tu me pagar"
    elif today == 20:
        default = "Me paga vagabundo"
    else:
        remain = today - 20
        default = f"Já se passaram {remain} dias desde o dia do pagamento"
    for text in texts:
        default += "\n\n" + text
    return default

def create_message(MIMEs, configs, receiver):
    msg = MIMEMultipart()
    msg["Subject"] = "Agiotagem Virtual"
    msg["From"]    = configs['user']
    msg["To"]      = receiver

    for MIME in MIMEs:
        msg.attach(MIME)
    return msg

async def send_monthly_email():
    config = get_configs()
    
    logging.info("Iniciando o envio do email")

    adtionals = []
    adtionals.append(translate_text(get_quote()))
    body = create_text(adtionals)

    MIMEs = []
    MIMEs.append(create_mime_audio(get_audio_freesound(config)))
    logging.info("Áudio de risada obtido com sucesso")

    MIMEs.append(MIMEText(body, "plain"))
    logging.info("Texto do email criado com sucesso")
    
    MIMEs.append(create_MIMEImage(get_imgmeme()))
    logging.info("Meme obtido com sucesso") 

    for receiver in get_receivers():
        msg = create_message(MIMEs, config, receiver)
        send_email(config,msg)

if __name__ == "__main__":
    asyncio.run(send_monthly_email())
