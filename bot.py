import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

API_KEY_FOOTBALL = os.getenv("API_KEY_FOOTBALL")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

HEADERS = {
    'X-RapidAPI-Key': API_KEY_FOOTBALL,
    'X-RapidAPI-Host': 'api-football-v1.p.rapidapi.com'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Fala, Thiago! Envie /analisar time1 time2")

def buscar_fixtures(time_nome):
    url = "https://api-football-v1.p.rapidapi.com/v3/teams"
    response = requests.get(url, headers=HEADERS, params={"search": time_nome})
    data = response.json()
    if data["response"]:
        return data["response"][0]["team"]["id"]
    return None

def buscar_partida(time1_id, time2_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/headtohead"
    params = {"h2h": f"{time1_id}-{time2_id}"}
    response = requests.get(url, headers=HEADERS, params=params)
    return response.json()

async def analisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) < 2:
            await update.message.reply_text("⚠️ Use: /analisar time1 time2")
            return

        time1 = context.args[0]
        time2 = context.args[1]

        id1 = buscar_fixtures(time1)
        id2 = buscar_fixtures(time2)

        if not id1 or not id2:
            await update.message.reply_text("❌ Não encontrei um dos times.")
            return

        dados = buscar_partida(id1, id2)
        if not dados["response"]:
            await update.message.reply_text("❌ Sem partidas recentes.")
            return

        jogo = dados["response"][0]
        home = jogo["teams"]["home"]["name"]
        away = jogo["teams"]["away"]["name"]
        data = jogo["fixture"]["date"]
        placar = f'{jogo["goals"]["home"]} x {jogo["goals"]["away"]}'

        texto = f"📊 Último confronto:\n{home} vs {away}\n"
        texto += f"📅 Data: {data[:10]} | Placar: {placar}"

        await update.message.reply_text(texto)
    except Exception as e:
        await update.message.reply_text(f"Erro: {e}")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("analisar", analisar))

print("🤖 Bot rodando...")
app.run_polling()
