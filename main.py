import sqlite3
import threading
import random
import string
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import g4f


# ─── Health Server ───────────────────────────────────────────────────────────────

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self, format, *args):
        pass

def run_health_server():
    server = HTTPServer(("0.0.0.0", 5000), HealthHandler)
    server.serve_forever()

threading.Thread(target=run_health_server, daemon=True).start()


# ─── Config ──────────────────────────────────────────────────────────────────────

TOKEN = "8211756949:AAGmxd3Kl-Jl3ogDFkH0N9k-ZE8e5kFvsTc"
OWNER_ID = 2095983359
DB_PATH = "luna_bot.db"
DLC_CHANNEL = "https://t.me/+rKV7fxZ7X_cwNmFi"
PRIVATE_COST = 150
REF_BONUS = 15


# ─── Languages ───────────────────────────────────────────────────────────────────

LANGUAGES = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
    "pt": "🇧🇷 Português",
    "es": "🇪🇸 Español",
    "tr": "🇹🇷 Türkçe",
    "de": "🇩🇪 Deutsch",
}

TR = {
    "welcome": {
        "ru": "👋 Добро пожаловать, путник\n\n🪄 Этот бот поможет тебе в получении самых лучших DLC от LUNA CLIENT!\n\nДля управления ботом используйте кнопки в этом сообщении:",
        "en": "👋 Welcome, traveler\n\n🪄 This bot will help you get the best DLC from LUNA CLIENT!\n\nUse the buttons below to navigate:",
        "pt": "👋 Bem-vindo, viajante\n\n🪄 Este bot vai te ajudar a obter os melhores DLCs do LUNA CLIENT!\n\nUse os botões abaixo para navegar:",
        "es": "👋 Bienvenido, viajero\n\n🪄 ¡Este bot te ayudará a obtener los mejores DLC de LUNA CLIENT!\n\nUsa los botones de abajo para navegar:",
        "tr": "👋 Hoş geldin, yolcu\n\n🪄 Bu bot sana LUNA CLIENT'ın en iyi DLC'lerini almana yardımcı olacak!\n\nGezinmek için aşağıdaki düğmeleri kullan:",
        "de": "👋 Willkommen, Reisender\n\n🪄 Dieser Bot hilft dir, die besten DLCs von LUNA CLIENT zu erhalten!\n\nNutze die Schaltflächen unten zur Navigation:",
    },
    "btn_get_dlc":      {"ru": "📥 Получить DLC",         "en": "📥 Get DLC",          "pt": "📥 Obter DLC",       "es": "📥 Obtener DLC",    "tr": "📥 DLC Al",              "de": "📥 DLC erhalten"},
    "btn_profile":      {"ru": "👤 Профиль",               "en": "👤 Profile",          "pt": "👤 Perfil",          "es": "👤 Perfil",          "tr": "👤 Profil",              "de": "👤 Profil"},
    "btn_faq":          {"ru": "❓ FAQ (Помощь)",           "en": "❓ FAQ (Help)",        "pt": "❓ FAQ (Ajuda)",     "es": "❓ FAQ (Ayuda)",     "tr": "❓ SSS (Yardım)",        "de": "❓ FAQ (Hilfe)"},
    "btn_panel":        {"ru": "⚙️ Панель управления",     "en": "⚙️ Admin Panel",      "pt": "⚙️ Painel Admin",   "es": "⚙️ Panel Admin",    "tr": "⚙️ Yönetim Paneli",     "de": "⚙️ Verwaltungspanel"},
    "btn_back":         {"ru": "⬅️ Назад",                 "en": "⬅️ Back",             "pt": "⬅️ Voltar",          "es": "⬅️ Atrás",           "tr": "⬅️ Geri",               "de": "⬅️ Zurück"},
    "btn_main_menu":    {"ru": "⬅️ В главное меню",        "en": "⬅️ Main Menu",        "pt": "⬅️ Menu Principal",  "es": "⬅️ Menú Principal",  "tr": "⬅️ Ana Menü",           "de": "⬅️ Hauptmenü"},
    "btn_language":     {"ru": "🌐 Язык",                  "en": "🌐 Language",         "pt": "🌐 Idioma",          "es": "🌐 Idioma",          "tr": "🌐 Dil",                 "de": "🌐 Sprache"},
    "btn_games":        {"ru": "🎮 Мини-игры",             "en": "🎮 Mini-games",       "pt": "🎮 Mini-jogos",      "es": "🎮 Minijuegos",      "tr": "🎮 Mini Oyunlar",        "de": "🎮 Minispiele"},
    "btn_purchases":    {"ru": "🛒 Мои покупки",           "en": "🛒 My Purchases",     "pt": "🛒 Minhas Compras",  "es": "🛒 Mis Compras",     "tr": "🛒 Satın Almalarım",     "de": "🛒 Meine Käufe"},
    "btn_promo":        {"ru": "🎁 Активировать промокод", "en": "🎁 Activate promo",   "pt": "🎁 Ativar promo",    "es": "🎁 Activar promo",   "tr": "🎁 Promosyon kodu",      "de": "🎁 Promo aktivieren"},
    "btn_buy_access":   {"ru": "💳 Купить доступ — 150 🪙","en": "💳 Buy access — 150 🪙","pt": "💳 Acesso — 150 🪙","es": "💳 Acceso — 150 🪙", "tr": "💳 Erişim — 150 🪙",    "de": "💳 Zugang — 150 🪙"},
    "btn_confirm_buy":  {"ru": "✅ Подтвердить",           "en": "✅ Confirm",           "pt": "✅ Confirmar",        "es": "✅ Confirmar",        "tr": "✅ Onayla",              "de": "✅ Bestätigen"},
    "btn_download_apk": {"ru": "📱 Скачать APK (Android)", "en": "📱 Download APK (Android)", "pt": "📱 Baixar APK (Android)", "es": "📱 Descargar APK (Android)", "tr": "📱 APK indir (Android)", "de": "📱 APK herunterladen (Android)"},
    "btn_play_again":   {"ru": "🔄 Играть снова",          "en": "🔄 Play again",       "pt": "🔄 Jogar novamente", "es": "🔄 Jugar de nuevo",  "tr": "🔄 Tekrar oyna",         "de": "🔄 Nochmal spielen"},
    "btn_new_match":    {"ru": "⚔️ Новый матч",            "en": "⚔️ New match",        "pt": "⚔️ Nova partida",    "es": "⚔️ Nuevo partido",   "tr": "⚔️ Yeni maç",           "de": "⚔️ Neues Spiel"},
    "btn_leaderboard":  {"ru": "🏆 Лидеры",                "en": "🏆 Leaderboard",      "pt": "🏆 Líderes",          "es": "🏆 Líderes",          "tr": "🏆 Liderler",            "de": "🏆 Bestenliste"},
    "btn_casino":       {"ru": "🎲 Казино",                 "en": "🎲 Casino",            "pt": "🎲 Cassino",          "es": "🎲 Casino",           "tr": "🎲 Kumarhane",           "de": "🎲 Casino"},
    "btn_spin":         {"ru": "🎰 Крутить барабан",        "en": "🎰 Spin",              "pt": "🎰 Girar",            "es": "🎰 Girar",            "tr": "🎰 Çevir",              "de": "🎰 Drehen"},
    "btn_coin_heads":   {"ru": "👑 Орёл",                   "en": "👑 Heads",             "pt": "👑 Cara",             "es": "👑 Cara",             "tr": "👑 Yazı",               "de": "👑 Kopf"},
    "btn_coin_tails":   {"ru": "🌀 Решка",                  "en": "🌀 Tails",             "pt": "🌀 Coroa",            "es": "🌀 Cruz",             "tr": "🌀 Tura",               "de": "🌀 Zahl"},
    "spin_title": {
        "ru": "🎰 <b>Ежедневный спин</b>\n\nКрути барабан раз в 24 часа и получай коины!\n\nТвой баланс: <b>{coins} 🪙</b>",
        "en": "🎰 <b>Daily Spin</b>\n\nSpin once every 24 hours and earn coins!\n\nYour balance: <b>{coins} 🪙</b>",
        "pt": "🎰 <b>Giro Diário</b>\n\nGire uma vez a cada 24 horas e ganhe moedas!\n\nSeu saldo: <b>{coins} 🪙</b>",
        "es": "🎰 <b>Giro Diario</b>\n\n¡Gira una vez cada 24 horas y gana monedas!\n\nTu saldo: <b>{coins} 🪙</b>",
        "tr": "🎰 <b>Günlük Çevirme</b>\n\n24 saatte bir çevir ve coin kazan!\n\nBakiyen: <b>{coins} 🪙</b>",
        "de": "🎰 <b>Täglicher Spin</b>\n\nDrehe einmal alle 24 Stunden und verdiene Coins!\n\nDein Guthaben: <b>{coins} 🪙</b>",
    },
    "spin_result": {
        "ru": "🎰 Барабан крутится...\n\n{reel}\n\n✨ Ты выиграл <b>+{coins} 🪙</b>!\nТвой баланс: <b>{total} 🪙</b>",
        "en": "🎰 Spinning...\n\n{reel}\n\n✨ You won <b>+{coins} 🪙</b>!\nYour balance: <b>{total} 🪙</b>",
        "pt": "🎰 Girando...\n\n{reel}\n\n✨ Você ganhou <b>+{coins} 🪙</b>!\nSeu saldo: <b>{total} 🪙</b>",
        "es": "🎰 Girando...\n\n{reel}\n\n✨ ¡Ganaste <b>+{coins} 🪙</b>!\nTu saldo: <b>{total} 🪙</b>",
        "tr": "🎰 Çevriliyor...\n\n{reel}\n\n✨ <b>+{coins} 🪙</b> kazandın!\nBakiyen: <b>{total} 🪙</b>",
        "de": "🎰 Dreht...\n\n{reel}\n\n✨ Du hast <b>+{coins} 🪙</b> gewonnen!\nDein Guthaben: <b>{total} 🪙</b>",
    },
    "spin_cooldown": {
        "ru": "⏳ Спин уже использован!\n\nСледующий спин через: <b>{hours}ч {mins}м</b>",
        "en": "⏳ Already spun!\n\nNext spin in: <b>{hours}h {mins}m</b>",
        "pt": "⏳ Já girou!\n\nPróximo giro em: <b>{hours}h {mins}m</b>",
        "es": "⏳ ¡Ya giraste!\n\nPróximo giro en: <b>{hours}h {mins}m</b>",
        "tr": "⏳ Zaten çevirdin!\n\nSonraki çevirme: <b>{hours}s {mins}d</b>",
        "de": "⏳ Bereits gedreht!\n\nNächster Spin in: <b>{hours}h {mins}m</b>",
    },
    "coin_title": {
        "ru": "🪙 <b>Угадай монету</b>\n\nОрёл или решка? Угадай и получи <b>+3 🪙</b>!\n\nТвой баланс: <b>{coins} 🪙</b>",
        "en": "🪙 <b>Coin Flip</b>\n\nHeads or tails? Guess right and earn <b>+3 🪙</b>!\n\nYour balance: <b>{coins} 🪙</b>",
        "pt": "🪙 <b>Cara ou Coroa</b>\n\nAdivinhe e ganhe <b>+3 🪙</b>!\n\nSeu saldo: <b>{coins} 🪙</b>",
        "es": "🪙 <b>Cara o Cruz</b>\n\n¡Adivina y gana <b>+3 🪙</b>!\n\nTu saldo: <b>{coins} 🪙</b>",
        "tr": "🪙 <b>Yazı Tura</b>\n\nDoğru tahmin et ve <b>+3 🪙</b> kazan!\n\nBakiyen: <b>{coins} 🪙</b>",
        "de": "🪙 <b>Münzwurf</b>\n\nKopf oder Zahl? Rate richtig und verdiene <b>+3 🪙</b>!\n\nDein Guthaben: <b>{coins} 🪙</b>",
    },
    "coin_win": {
        "ru": "🎉 {icon} — Правильно!\n\n<b>+3 🪙</b> зачислено!\nТвой баланс: <b>{total} 🪙</b>",
        "en": "🎉 {icon} — Correct!\n\n<b>+3 🪙</b> earned!\nYour balance: <b>{total} 🪙</b>",
        "pt": "🎉 {icon} — Correto!\n\n<b>+3 🪙</b> adicionado!\nSeu saldo: <b>{total} 🪙</b>",
        "es": "🎉 {icon} — ¡Correcto!\n\n<b>+3 🪙</b> ganado!\nTu saldo: <b>{total} 🪙</b>",
        "tr": "🎉 {icon} — Doğru!\n\n<b>+3 🪙</b> kazandın!\nBakiyen: <b>{total} 🪙</b>",
        "de": "🎉 {icon} — Richtig!\n\n<b>+3 🪙</b> verdient!\nDein Guthaben: <b>{total} 🪙</b>",
    },
    "coin_lose": {
        "ru": "😔 {icon} — Неверно!\n\nНе повезло, попробуй ещё раз!\nТвой баланс: <b>{total} 🪙</b>",
        "en": "😔 {icon} — Wrong!\n\nBad luck, try again!\nYour balance: <b>{total} 🪙</b>",
        "pt": "😔 {icon} — Errado!\n\nMá sorte, tente de novo!\nSeu saldo: <b>{total} 🪙</b>",
        "es": "😔 {icon} — ¡Incorrecto!\n\n¡Mala suerte, inténtalo de nuevo!\nTu saldo: <b>{total} 🪙</b>",
        "tr": "😔 {icon} — Yanlış!\n\nŞansın yok, tekrar dene!\nBakiyen: <b>{total} 🪙</b>",
        "de": "😔 {icon} — Falsch!\n\nPech, versuche es nochmal!\nDein Guthaben: <b>{total} 🪙</b>",
    },
    # Leaderboard
    "leaderboard_title": {
        "ru": "🏆 <b>Таблица лидеров</b>\n\nТоп игроков по количеству коинов:\n\n{rows}\n\n💡 Зарабатывай коины через рефералов, промокоды и игры!",
        "en": "🏆 <b>Leaderboard</b>\n\nTop players by coins:\n\n{rows}\n\n💡 Earn coins via referrals, promo codes and games!",
        "pt": "🏆 <b>Tabela de Líderes</b>\n\nMelhores jogadores por moedas:\n\n{rows}\n\n💡 Ganhe moedas por referências, promos e jogos!",
        "es": "🏆 <b>Tabla de Líderes</b>\n\nMejores jugadores por monedas:\n\n{rows}\n\n💡 ¡Gana monedas con referidos, promos y juegos!",
        "tr": "🏆 <b>Liderler Tablosu</b>\n\nEn fazla coini olan oyuncular:\n\n{rows}\n\n💡 Referanslar, promosyonlar ve oyunlarla coin kazan!",
        "de": "🏆 <b>Bestenliste</b>\n\nTop-Spieler nach Coins:\n\n{rows}\n\n💡 Verdiene Coins durch Empfehlungen, Promo-Codes und Spiele!",
    },
    "your_rank": {
        "ru": "📍 Твоё место: <b>#{rank}</b> | <b>{coins} 🪙</b>",
        "en": "📍 Your rank: <b>#{rank}</b> | <b>{coins} 🪙</b>",
        "pt": "📍 Sua posição: <b>#{rank}</b> | <b>{coins} 🪙</b>",
        "es": "📍 Tu posición: <b>#{rank}</b> | <b>{coins} 🪙</b>",
        "tr": "📍 Sıralaман: <b>#{rank}</b> | <b>{coins} 🪙</b>",
        "de": "📍 Dein Rang: <b>#{rank}</b> | <b>{coins} 🪙</b>",
    },
    # Casino
    "casino_menu": {
        "ru": (
            "🎲 <b>Казино LUNA</b>\n\n"
            "Поставь свои коины и испытай удачу!\n\n"
            "📊 <b>Таблица выплат:</b>\n"
            "🔥 Сгорело всё — <b>×0</b> (20%)\n"
            "📉 Потерял половину — <b>×0.5</b> (22%)\n"
            "😐 Деньги при себе — <b>×1</b> (20%)\n"
            "💰 Удвоил — <b>×2</b> (20%)\n"
            "🚀 Пятёрка — <b>×5</b> (12%)\n"
            "💫 Десятка — <b>×10</b> (5.5%)\n"
            "👑 ДЖЕКПОТ — <b>×100</b> (0.5%)\n\n"
            "Твой баланс: <b>{coins} 🪙</b>\n\n"
            "Напиши количество коинов для ставки:"
        ),
        "en": (
            "🎲 <b>LUNA Casino</b>\n\n"
            "Bet your coins and test your luck!\n\n"
            "📊 <b>Payout table:</b>\n"
            "🔥 Lost all — <b>×0</b> (20%)\n"
            "📉 Lost half — <b>×0.5</b> (22%)\n"
            "😐 Break even — <b>×1</b> (20%)\n"
            "💰 Doubled — <b>×2</b> (20%)\n"
            "🚀 Five times — <b>×5</b> (12%)\n"
            "💫 Ten times — <b>×10</b> (5.5%)\n"
            "👑 JACKPOT — <b>×100</b> (0.5%)\n\n"
            "Your balance: <b>{coins} 🪙</b>\n\n"
            "Type the amount of coins to bet:"
        ),
        "pt": (
            "🎲 <b>Cassino LUNA</b>\n\n"
            "Aposte suas moedas e teste sua sorte!\n\n"
            "📊 <b>Tabela de pagamentos:</b>\n"
            "🔥 Perdeu tudo — <b>×0</b> (20%)\n"
            "📉 Perdeu metade — <b>×0.5</b> (22%)\n"
            "😐 Empatou — <b>×1</b> (20%)\n"
            "💰 Dobrou — <b>×2</b> (20%)\n"
            "🚀 Cinco vezes — <b>×5</b> (12%)\n"
            "💫 Dez vezes — <b>×10</b> (5.5%)\n"
            "👑 JACKPOT — <b>×100</b> (0.5%)\n\n"
            "Seu saldo: <b>{coins} 🪙</b>\n\nDigite a aposta:"
        ),
        "es": (
            "🎲 <b>Casino LUNA</b>\n\n"
            "¡Apuesta tus monedas y prueba tu suerte!\n\n"
            "📊 <b>Tabla de pagos:</b>\n"
            "🔥 Perdiste todo — <b>×0</b> (20%)\n"
            "📉 Perdiste la mitad — <b>×0.5</b> (22%)\n"
            "😐 Empate — <b>×1</b> (20%)\n"
            "💰 Duplicaste — <b>×2</b> (20%)\n"
            "🚀 Cinco veces — <b>×5</b> (12%)\n"
            "💫 Diez veces — <b>×10</b> (5.5%)\n"
            "👑 JACKPOT — <b>×100</b> (0.5%)\n\n"
            "Tu saldo: <b>{coins} 🪙</b>\n\nEscribe la cantidad a apostar:"
        ),
        "tr": (
            "🎲 <b>LUNA Kumarhane</b>\n\n"
            "Coinlerini yatır ve şansını dene!\n\n"
            "📊 <b>Ödeme tablosu:</b>\n"
            "🔥 Hepsini kaybettin — <b>×0</b> (20%)\n"
            "📉 Yarısını kaybettin — <b>×0.5</b> (22%)\n"
            "😐 Başa baş — <b>×1</b> (20%)\n"
            "💰 İki katı — <b>×2</b> (20%)\n"
            "🚀 Beş katı — <b>×5</b> (12%)\n"
            "💫 On katı — <b>×10</b> (5.5%)\n"
            "👑 JACKPOT — <b>×100</b> (0.5%)\n\n"
            "Bakiyen: <b>{coins} 🪙</b>\n\nBahis miktarını yaz:"
        ),
        "de": (
            "🎲 <b>LUNA Casino</b>\n\n"
            "Setze deine Coins und teste dein Glück!\n\n"
            "📊 <b>Auszahlungstabelle:</b>\n"
            "🔥 Alles verloren — <b>×0</b> (20%)\n"
            "📉 Hälfte verloren — <b>×0.5</b> (22%)\n"
            "😐 Break-even — <b>×1</b> (20%)\n"
            "💰 Verdoppelt — <b>×2</b> (20%)\n"
            "🚀 Fünffach — <b>×5</b> (12%)\n"
            "💫 Zehnfach — <b>×10</b> (5.5%)\n"
            "👑 JACKPOT — <b>×100</b> (0.5%)\n\n"
            "Guthaben: <b>{coins} 🪙</b>\n\nGib den Einsatz ein:"
        ),
    },
    "casino_no_coins": {
        "ru": "❌ Недостаточно коинов!\n\nМинимальная ставка — <b>1 🪙</b>. У тебя <b>{coins} 🪙</b>.",
        "en": "❌ Not enough coins!\n\nMinimum bet — <b>1 🪙</b>. You have <b>{coins} 🪙</b>.",
        "pt": "❌ Moedas insuficientes!\n\nAposta mínima — <b>1 🪙</b>. Você tem <b>{coins} 🪙</b>.",
        "es": "❌ ¡Monedas insuficientes!\n\nApuesta mínima — <b>1 🪙</b>. Tienes <b>{coins} 🪙</b>.",
        "tr": "❌ Yeterli coin yok!\n\nMinimum bahis — <b>1 🪙</b>. Sende <b>{coins} 🪙</b> var.",
        "de": "❌ Nicht genug Coins!\n\nMindest-Einsatz — <b>1 🪙</b>. Du hast <b>{coins} 🪙</b>.",
    },
    "casino_result": {
        "ru": "🎲 <b>Результат казино</b>\n\nСтавка: <b>{bet} 🪙</b>\nИсход: {outcome_icon} <b>{outcome_name}</b>\nВыплата: <b>{payout} 🪙</b>\n\n{verdict}\n\nТвой баланс: <b>{total} 🪙</b>",
        "en": "🎲 <b>Casino Result</b>\n\nBet: <b>{bet} 🪙</b>\nOutcome: {outcome_icon} <b>{outcome_name}</b>\nPayout: <b>{payout} 🪙</b>\n\n{verdict}\n\nYour balance: <b>{total} 🪙</b>",
        "pt": "🎲 <b>Resultado do Cassino</b>\n\nAposta: <b>{bet} 🪙</b>\nResultado: {outcome_icon} <b>{outcome_name}</b>\nPagamento: <b>{payout} 🪙</b>\n\n{verdict}\n\nSeu saldo: <b>{total} 🪙</b>",
        "es": "🎲 <b>Resultado del Casino</b>\n\nApuesta: <b>{bet} 🪙</b>\nResultado: {outcome_icon} <b>{outcome_name}</b>\nPago: <b>{payout} 🪙</b>\n\n{verdict}\n\nTu saldo: <b>{total} 🪙</b>",
        "tr": "🎲 <b>Kumarhane Sonucu</b>\n\nBahis: <b>{bet} 🪙</b>\nSonuç: {outcome_icon} <b>{outcome_name}</b>\nÖdeme: <b>{payout} 🪙</b>\n\n{verdict}\n\nBakiyen: <b>{total} 🪙</b>",
        "de": "🎲 <b>Casino-Ergebnis</b>\n\nEinsatz: <b>{bet} 🪙</b>\nErgebnis: {outcome_icon} <b>{outcome_name}</b>\nAuszahlung: <b>{payout} 🪙</b>\n\n{verdict}\n\nGuthaben: <b>{total} 🪙</b>",
    },
    # DLC
    "dlc_no_access": {
        "ru": (
            "📥 <b>Получить DLC — Fwd Assault</b>\n\n"
            "🔒 У тебя нет доступа к приватному каналу.\n\n"
            "💰 Купи доступ за <b>150 🪙 коинов</b> и получи:\n"
            "  • Приватный чит для Android (APK)\n"
            "  • Ранние обновления и эксклюзивные функции\n\n"
            "Твой баланс: <b>{coins} 🪙</b>\n\n"
            "📎 Получай коины через реферальную систему или промокоды!"
        ),
        "en": (
            "📥 <b>Get DLC — Fwd Assault</b>\n\n"
            "🔒 You don't have access to the private channel.\n\n"
            "💰 Buy access for <b>150 🪙 coins</b> and get:\n"
            "  • Private cheat for Android (APK)\n"
            "  • Early updates & exclusive features\n\n"
            "Your balance: <b>{coins} 🪙</b>\n\n"
            "📎 Earn coins through the referral system or promo codes!"
        ),
        "pt": (
            "📥 <b>Obter DLC — Fwd Assault</b>\n\n"
            "🔒 Você não tem acesso ao canal privado.\n\n"
            "💰 Compre acesso por <b>150 🪙 moedas</b>:\n"
            "  • Cheat privado para Android (APK)\n"
            "  • Atualizações antecipadas e funções exclusivas\n\n"
            "Seu saldo: <b>{coins} 🪙</b>"
        ),
        "es": (
            "📥 <b>Obtener DLC — Fwd Assault</b>\n\n"
            "🔒 No tienes acceso al canal privado.\n\n"
            "💰 Compra acceso por <b>150 🪙 monedas</b>:\n"
            "  • Cheat privado para Android (APK)\n"
            "  • Actualizaciones tempranas y funciones exclusivas\n\n"
            "Tu saldo: <b>{coins} 🪙</b>"
        ),
        "tr": (
            "📥 <b>DLC Al — Fwd Assault</b>\n\n"
            "🔒 Özel kanala erişimin yok.\n\n"
            "💰 <b>150 🪙 coin</b> için erişim satın al:\n"
            "  • Android için özel hile (APK)\n"
            "  • Erken güncellemeler ve özel özellikler\n\n"
            "Bakiyen: <b>{coins} 🪙</b>"
        ),
        "de": (
            "📥 <b>DLC erhalten — Fwd Assault</b>\n\n"
            "🔒 Du hast keinen Zugang zum privaten Kanal.\n\n"
            "💰 Kaufe Zugang für <b>150 🪙 Coins</b>:\n"
            "  • Privater Cheat für Android (APK)\n"
            "  • Frühe Updates & exklusive Funktionen\n\n"
            "Dein Guthaben: <b>{coins} 🪙</b>"
        ),
    },
    "dlc_has_access": {
        "ru": "📥 <b>DLC — Fwd Assault</b>\n\n✅ У тебя есть доступ к приватному каналу!\n\n📱 Скачай APK для Android по кнопке ниже:",
        "en": "📥 <b>DLC — Fwd Assault</b>\n\n✅ You have access to the private channel!\n\n📱 Download APK for Android:",
        "pt": "📥 <b>DLC — Fwd Assault</b>\n\n✅ Você tem acesso ao canal privado!\n\n📱 Baixe o APK para Android:",
        "es": "📥 <b>DLC — Fwd Assault</b>\n\n✅ ¡Tienes acceso al canal privado!\n\n📱 Descarga el APK para Android:",
        "tr": "📥 <b>DLC — Fwd Assault</b>\n\n✅ Özel kanala erişimin var!\n\n📱 Android için APK indir:",
        "de": "📥 <b>DLC — Fwd Assault</b>\n\n✅ Du hast Zugang zum privaten Kanal!\n\n📱 APK für Android herunterladen:",
    },
    "buy_confirm_text": {
        "ru": "💳 <b>Подтверждение покупки</b>\n\n🛒 Товар: Доступ к приватному каналу\n💰 Стоимость: <b>150 🪙</b>\n\nТвой баланс: <b>{coins} 🪙</b>\nПосле покупки: <b>{after} 🪙</b>\n\nПодтвердить?",
        "en": "💳 <b>Purchase confirmation</b>\n\n🛒 Item: Private channel access\n💰 Cost: <b>150 🪙</b>\n\nYour balance: <b>{coins} 🪙</b>\nAfter purchase: <b>{after} 🪙</b>\n\nConfirm?",
        "pt": "💳 <b>Confirmação de compra</b>\n\n🛒 Item: Acesso ao canal privado\n💰 Custo: <b>150 🪙</b>\n\nSeu saldo: <b>{coins} 🪙</b>\nApós a compra: <b>{after} 🪙</b>\n\nConfirmar?",
        "es": "💳 <b>Confirmación de compra</b>\n\n🛒 Artículo: Acceso al canal privado\n💰 Costo: <b>150 🪙</b>\n\nTu saldo: <b>{coins} 🪙</b>\nDespués: <b>{after} 🪙</b>\n\n¿Confirmar?",
        "tr": "💳 <b>Satın alma onayı</b>\n\n🛒 Ürün: Özel kanal erişimi\n💰 Maliyet: <b>150 🪙</b>\n\nBakiyen: <b>{coins} 🪙</b>\nSonrası: <b>{after} 🪙</b>\n\nOnayla?",
        "de": "💳 <b>Kaufbestätigung</b>\n\n🛒 Artikel: Privatkanal-Zugang\n💰 Kosten: <b>150 🪙</b>\n\nGuthaben: <b>{coins} 🪙</b>\nNach Kauf: <b>{after} 🪙</b>\n\nBestätigen?",
    },
    "buy_success": {
        "ru": "✅ <b>Доступ получен!</b>\n\n🎉 Ты успешно купил доступ к приватному каналу!\nС тебя списано <b>150 🪙</b>.\n\nНажми кнопку ниже, чтобы перейти в канал и скачать APK для Android:",
        "en": "✅ <b>Access granted!</b>\n\n🎉 You successfully bought access to the private channel!\n<b>150 🪙</b> deducted.\n\nClick below to join the channel and download APK for Android:",
        "pt": "✅ <b>Acesso concedido!</b>\n\n🎉 Você comprou acesso ao canal privado!\n<b>150 🪙</b> deduzidos.\n\nClique abaixo para entrar no canal e baixar o APK:",
        "es": "✅ <b>¡Acceso concedido!</b>\n\n🎉 ¡Compraste acceso al canal privado!\n<b>150 🪙</b> deducidos.\n\nHaz clic abajo para unirte al canal y descargar el APK:",
        "tr": "✅ <b>Erişim verildi!</b>\n\n🎉 Özel kanala erişim satın aldın!\n<b>150 🪙</b> düşüldü.\n\nKanala katılmak ve APK indirmek için aşağıya tıkla:",
        "de": "✅ <b>Zugang gewährt!</b>\n\n🎉 Du hast Zugang zum privaten Kanal gekauft!\n<b>150 🪙</b> abgezogen.\n\nKlicke unten, um dem Kanal beizutreten und die APK herunterzuladen:",
    },
    "buy_no_coins": {
        "ru": "❌ <b>Недостаточно коинов!</b>\n\nНужно: <b>150 🪙</b> | У тебя: <b>{coins} 🪙</b>\n\nПолучай коины через:\n• Реферальную систему (+{ref} 🪙 за друга)\n• Промокоды от администрации",
        "en": "❌ <b>Not enough coins!</b>\n\nNeeded: <b>150 🪙</b> | You have: <b>{coins} 🪙</b>\n\nEarn coins via:\n• Referral system (+{ref} 🪙 per friend)\n• Admin promo codes",
        "pt": "❌ <b>Moedas insuficientes!</b>\n\nNecessário: <b>150 🪙</b> | Você tem: <b>{coins} 🪙</b>\n\nConsiga moedas:\n• Sistema de referência (+{ref} 🪙 por amigo)\n• Códigos promo",
        "es": "❌ <b>¡Monedas insuficientes!</b>\n\nNecesitas: <b>150 🪙</b> | Tienes: <b>{coins} 🪙</b>\n\nGana monedas:\n• Sistema de referidos (+{ref} 🪙 por amigo)\n• Códigos promo",
        "tr": "❌ <b>Yeterli coin yok!</b>\n\nGerekli: <b>150 🪙</b> | Sende: <b>{coins} 🪙</b>\n\nCoin kazan:\n• Referans sistemi (+{ref} 🪙 arkadaş başına)\n• Promosyon kodları",
        "de": "❌ <b>Nicht genug Coins!</b>\n\nBenötigt: <b>150 🪙</b> | Du hast: <b>{coins} 🪙</b>\n\nErhalte Coins:\n• Empfehlungsprogramm (+{ref} 🪙 pro Freund)\n• Promo-Codes",
    },
    # referral
    "ref_bonus_new": {
        "ru": "🎉 Ты перешёл по реферальной ссылке!\n\n+{coins} 🪙 коинов зачислено на твой счёт!",
        "en": "🎉 You joined via a referral link!\n\n+{coins} 🪙 coins added to your account!",
        "pt": "🎉 Você entrou por um link de referência!\n\n+{coins} 🪙 moedas adicionadas à sua conta!",
        "es": "🎉 ¡Entraste por un enlace de referido!\n\n+{coins} 🪙 monedas añadidas a tu cuenta!",
        "tr": "🎉 Referans linki ile katıldın!\n\nHesabına +{coins} 🪙 coin eklendi!",
        "de": "🎉 Du bist über einen Empfehlungslink beigetreten!\n\n+{coins} 🪙 Coins gutgeschrieben!",
    },
    "ref_bonus_ref": {
        "ru": "🎉 Твой друг <b>{name}</b> перешёл по твоей реферальной ссылке!\n\n+{coins} 🪙 коинов зачислено на твой счёт!",
        "en": "🎉 Your friend <b>{name}</b> joined via your referral link!\n\n+{coins} 🪙 coins added to your account!",
        "pt": "🎉 Seu amigo <b>{name}</b> entrou pelo seu link!\n\n+{coins} 🪙 moedas adicionadas à sua conta!",
        "es": "🎉 ¡Tu amigo <b>{name}</b> entró por tu enlace!\n\n+{coins} 🪙 monedas añadidas a tu cuenta!",
        "tr": "🎉 Arkadaşın <b>{name}</b> referans linkinle katıldı!\n\nHesabına +{coins} 🪙 coin eklendi!",
        "de": "🎉 Dein Freund <b>{name}</b> ist über deinen Link beigetreten!\n\n+{coins} 🪙 Coins gutgeschrieben!",
    },
    # promo
    "promo_prompt": {
        "ru": "🎁 Введи промокод:",
        "en": "🎁 Enter promo code:",
        "pt": "🎁 Digite o código promo:",
        "es": "🎁 Introduce el código promo:",
        "tr": "🎁 Promosyon kodunu gir:",
        "de": "🎁 Gib den Promo-Code ein:",
    },
    "promo_success": {
        "ru": "✅ Промокод активирован!\n\n+{coins} 🪙 зачислено на ваш счёт!",
        "en": "✅ Promo code activated!\n\n+{coins} 🪙 added to your account!",
        "pt": "✅ Código promo ativado!\n\n+{coins} 🪙 adicionado à sua conta!",
        "es": "✅ ¡Código promo activado!\n\n+{coins} 🪙 añadido a tu cuenta!",
        "tr": "✅ Promosyon kodu etkinleştirildi!\n\nHesabına +{coins} 🪙 eklendi!",
        "de": "✅ Promo-Code aktiviert!\n\n+{coins} 🪙 gutgeschrieben!",
    },
    "promo_not_found":   {"ru": "❌ Промокод не найден.",                                    "en": "❌ Promo code not found.",                      "pt": "❌ Código não encontrado.",         "es": "❌ Código no encontrado.",         "tr": "❌ Kod bulunamadı.",           "de": "❌ Code nicht gefunden."},
    "promo_exhausted":   {"ru": "❌ Промокод исчерпан — все активации использованы.",        "en": "❌ Promo code exhausted — all uses claimed.",   "pt": "❌ Código esgotado.",               "es": "❌ Código agotado.",              "tr": "❌ Kod tükendi.",              "de": "❌ Code erschöpft."},
    "promo_already_used":{"ru": "❌ Ты уже активировал этот промокод.",                     "en": "❌ You already activated this promo code.",     "pt": "❌ Você já usou este código.",      "es": "❌ Ya usaste este código.",       "tr": "❌ Bu kodu zaten kullandın.",  "de": "❌ Code bereits verwendet."},
    # faq
    "faq_text": {
        "ru": "❓ FAQ (Помощь)\n\nНапиши свой вопрос — он будет передан администратору.\nОбычно мы отвечаем в течение нескольких часов. ⏳",
        "en": "❓ FAQ (Help)\n\nWrite your question — it will be sent to the admin.\nWe usually reply within a few hours. ⏳",
        "pt": "❓ FAQ (Ajuda)\n\nEscreva sua pergunta — ela será enviada ao administrador.\nNormalmente respondemos em poucas horas. ⏳",
        "es": "❓ FAQ (Ayuda)\n\nEscribe tu pregunta — será enviada al administrador.\nNormalmente respondemos en pocas horas. ⏳",
        "tr": "❓ SSS (Yardım)\n\nSorunuzu yazın — yönetime iletilecektir.\nGenellikle birkaç saat içinde yanıtlarız. ⏳",
        "de": "❓ FAQ (Hilfe)\n\nSchreibe deine Frage — sie wird an den Admin weitergeleitet.\nWir antworten normalerweise innerhalb weniger Stunden. ⏳",
    },
    "faq_sent": {
        "ru": "✅ Ваш вопрос передан администратору!\n\nОжидайте ответа — мы свяжемся с вами в ближайшее время. 🙏",
        "en": "✅ Your question has been sent to the admin!\n\nPlease wait — we'll get back to you soon. 🙏",
        "pt": "✅ Sua pergunta foi enviada ao administrador!\n\nAguarde — entraremos em contato em breve. 🙏",
        "es": "✅ ¡Tu pregunta ha sido enviada al administrador!\n\nEspera — nos pondremos en contacto pronto. 🙏",
        "tr": "✅ Sorunuz yöneticiye iletildi!\n\nLütfen bekleyin — yakında size geri döneceğiz. 🙏",
        "de": "✅ Deine Frage wurde an den Admin gesendet!\n\nBitte warte — wir melden uns bald. 🙏",
    },
    "admin_reply": {
        "ru": "💬 Ответ от администратора:\n\n",
        "en": "💬 Reply from admin:\n\n",
        "pt": "💬 Resposta do administrador:\n\n",
        "es": "💬 Respuesta del administrador:\n\n",
        "tr": "💬 Yönetici yanıtı:\n\n",
        "de": "💬 Antwort vom Admin:\n\n",
    },
    # language
    "lang_choose": {
        "ru": "🌐 Выбор языка\n\nВыбери язык интерфейса:",
        "en": "🌐 Language Selection\n\nChoose your interface language:",
        "pt": "🌐 Seleção de Idioma\n\nEscolha o idioma da interface:",
        "es": "🌐 Selección de Idioma\n\nElige el idioma de la interfaz:",
        "tr": "🌐 Dil Seçimi\n\nArayüz dilini seç:",
        "de": "🌐 Sprachauswahl\n\nWähle deine Oberflächensprache:",
    },
    "lang_changed": {
        "ru": "✅ Язык изменён на Русский!",
        "en": "✅ Language changed to English!",
        "pt": "✅ Idioma alterado para Português!",
        "es": "✅ ¡Idioma cambiado a Español!",
        "tr": "✅ Dil Türkçe olarak değiştirildi!",
        "de": "✅ Sprache auf Deutsch geändert!",
    },
    # games
    "games_menu": {
        "ru": "🎮 Мини-игры\n\nВыбери игру:",
        "en": "🎮 Mini-games\n\nChoose a game:",
        "pt": "🎮 Mini-jogos\n\nEscolha um jogo:",
        "es": "🎮 Minijuegos\n\nElige un juego:",
        "tr": "🎮 Mini Oyunlar\n\nOyun seç:",
        "de": "🎮 Minispiele\n\nWähle ein Spiel:",
    },
    "guess_start": {
        "ru": "🔢 Угадай число!\n\nЯ загадал число от 1 до 100.\nНапиши своё число:",
        "en": "🔢 Guess the number!\n\nI picked a number from 1 to 100.\nType your guess:",
        "pt": "🔢 Adivinhe o número!\n\nEscolhi um número de 1 a 100.\nDigite seu palpite:",
        "es": "🔢 ¡Adivina el número!\n\nElegí un número del 1 al 100.\nEscribe tu intento:",
        "tr": "🔢 Sayıyı tahmin et!\n\n1 ile 100 arasında bir sayı seçtim.\nTahminini yaz:",
        "de": "🔢 Errate die Zahl!\n\nIch habe eine Zahl von 1 bis 100 gewählt.\nSchreibe deine Schätzung:",
    },
    "guess_higher":  {"ru": "📈 Больше! Попытка #{tries}. Попробуй ещё:",         "en": "📈 Higher! Attempt #{tries}. Try again:",       "pt": "📈 Maior! Tentativa #{tries}. Tente novamente:",   "es": "📈 ¡Más alto! Intento #{tries}. Inténtalo:",  "tr": "📈 Daha büyük! Deneme #{tries}. Tekrar dene:", "de": "📈 Höher! Versuch #{tries}. Erneut versuchen:"},
    "guess_lower":   {"ru": "📉 Меньше! Попытка #{tries}. Попробуй ещё:",         "en": "📉 Lower! Attempt #{tries}. Try again:",        "pt": "📉 Menor! Tentativa #{tries}. Tente novamente:",   "es": "📉 ¡Más bajo! Intento #{tries}. Inténtalo:",   "tr": "📉 Daha küçük! Deneme #{tries}. Tekrar dene:", "de": "📉 Niedriger! Versuch #{tries}. Erneut versuchen:"},
    "guess_win":     {"ru": "🎉 Правильно! Число было {num}.\nТы угадал за {tries} попыток!", "en": "🎉 Correct! The number was {num}.\nGuessed in {tries} attempts!", "pt": "🎉 Correto! O número era {num}.\nAdivinhou em {tries} tentativas!", "es": "🎉 ¡Correcto! El número era {num}.\n¡En {tries} intentos!", "tr": "🎉 Doğru! Sayı {num}'di.\n{tries} denemede tahmin ettin!", "de": "🎉 Richtig! Die Zahl war {num}.\nIn {tries} Versuchen erraten!"},
    "guess_invalid": {"ru": "❌ Введи число от 1 до 100:",                         "en": "❌ Enter a number from 1 to 100:",               "pt": "❌ Digite um número de 1 a 100:",                   "es": "❌ Introduce un número del 1 al 100:",          "tr": "❌ 1 ile 100 arasında bir sayı gir:",           "de": "❌ Gib eine Zahl von 1 bis 100 ein:"},
    "rps_choose": {
        "ru": "✊ Камень, ножницы, бумага!\n\nСделай свой выбор:",
        "en": "✊ Rock, Paper, Scissors!\n\nMake your choice:",
        "pt": "✊ Pedra, Papel, Tesoura!\n\nFaça sua escolha:",
        "es": "✊ ¡Piedra, Papel, Tijeras!\n\nHaz tu elección:",
        "tr": "✊ Taş, Kağıt, Makas!\n\nSeçimini yap:",
        "de": "✊ Schere, Stein, Papier!\n\nTriff deine Wahl:",
    },
    "rps_win":    {"ru": "🎉 Ты победил!\n\nТы: {user} | Бот: {bot}",    "en": "🎉 You win!\n\nYou: {user} | Bot: {bot}",     "pt": "🎉 Você ganhou!\n\nVocê: {user} | Bot: {bot}",  "es": "🎉 ¡Ganaste!\n\nTú: {user} | Bot: {bot}",   "tr": "🎉 Kazandın!\n\nSen: {user} | Bot: {bot}",  "de": "🎉 Du gewinnst!\n\nDu: {user} | Bot: {bot}"},
    "rps_lose":   {"ru": "😔 Бот победил!\n\nТы: {user} | Бот: {bot}",   "en": "😔 Bot wins!\n\nYou: {user} | Bot: {bot}",    "pt": "😔 O bot ganhou!\n\nVocê: {user} | Bot: {bot}", "es": "😔 ¡El bot ganó!\n\nTú: {user} | Bot: {bot}", "tr": "😔 Bot kazandı!\n\nSen: {user} | Bot: {bot}", "de": "😔 Bot gewinnt!\n\nDu: {user} | Bot: {bot}"},
    "rps_draw":   {"ru": "🤝 Ничья!\n\nТы: {user} | Бот: {bot}",         "en": "🤝 Draw!\n\nYou: {user} | Bot: {bot}",        "pt": "🤝 Empate!\n\nVocê: {user} | Bot: {bot}",       "es": "🤝 ¡Empate!\n\nTú: {user} | Bot: {bot}",    "tr": "🤝 Berabere!\n\nSen: {user} | Bot: {bot}",  "de": "🤝 Unentschieden!\n\nDu: {user} | Bot: {bot}"},
    "rps_vs_bot":    {"ru": "🤖 Против бота",      "en": "🤖 vs Bot",       "pt": "🤖 vs Bot",      "es": "🤖 vs Bot",      "tr": "🤖 Bota karşı",      "de": "🤖 Gegen Bot"},
    "rps_vs_player": {"ru": "👥 Против игрока",    "en": "👥 vs Player",    "pt": "👥 vs Jogador",  "es": "👥 vs Jugador",  "tr": "👥 Oyuncuya karşı",  "de": "👥 Gegen Spieler"},
    "ch_created": {
        "ru": "⚔️ Вызов создан!\n\nТвой код: <code>RPS-{code}</code>\n\nОтправь этот код другу — пусть введёт его в боте. Жду когда он примет вызов... ⏳",
        "en": "⚔️ Challenge created!\n\nYour code: <code>RPS-{code}</code>\n\nSend this code to your friend — they need to type it in the bot. Waiting... ⏳",
        "pt": "⚔️ Desafio criado!\n\nSeu código: <code>RPS-{code}</code>\n\nEnvie ao seu amigo — ele digita no bot. Aguardando... ⏳",
        "es": "⚔️ ¡Desafío creado!\n\nTu código: <code>RPS-{code}</code>\n\nEnvía a tu amigo — lo escribe en el bot. Esperando... ⏳",
        "tr": "⚔️ Meydan okuma oluşturuldu!\n\nKodun: <code>RPS-{code}</code>\n\nArkadaşına gönder — bota yazması gerekiyor. Bekleniyor... ⏳",
        "de": "⚔️ Herausforderung erstellt!\n\nDein Code: <code>RPS-{code}</code>\n\nSchicke deinem Freund — er gibt ihn im Bot ein. Warte... ⏳",
    },
    "ch_invite": {
        "ru": "⚔️ Игрок {name} вызывает тебя на Камень-Ножницы-Бумага!\n\nПринять вызов?",
        "en": "⚔️ Player {name} challenges you to Rock-Paper-Scissors!\n\nAccept?",
        "pt": "⚔️ Jogador {name} te desafia!\n\nAceitar?",
        "es": "⚔️ ¡{name} te desafía!\n\n¿Aceptar?",
        "tr": "⚔️ {name} seni meydan okumaya davet ediyor!\n\nKabul et?",
        "de": "⚔️ {name} fordert dich heraus!\n\nAnnehmen?",
    },
    "ch_accept_btn":  {"ru": "✅ Принять",   "en": "✅ Accept",  "pt": "✅ Aceitar",  "es": "✅ Aceptar",  "tr": "✅ Kabul et", "de": "✅ Annehmen"},
    "ch_decline_btn": {"ru": "❌ Отклонить", "en": "❌ Decline", "pt": "❌ Recusar",  "es": "❌ Rechazar", "tr": "❌ Reddet",   "de": "❌ Ablehnen"},
    "ch_accepted_p1": {
        "ru": "✅ {name} принял вызов! Делай выбор — соперник не увидит его до конца:\n\n✊ Камень  ✌️ Ножницы  🖐 Бумага",
        "en": "✅ {name} accepted! Make your choice — opponent won't see it until end:\n\n✊ Rock  ✌️ Scissors  🖐 Paper",
        "pt": "✅ {name} aceitou! Faça sua escolha:\n\n✊ Pedra  ✌️ Tesoura  🖐 Papel",
        "es": "✅ ¡{name} aceptó! Haz tu elección:\n\n✊ Piedra  ✌️ Tijera  🖐 Papel",
        "tr": "✅ {name} kabul etti! Seçimini yap:\n\n✊ Taş  ✌️ Makas  🖐 Kağıt",
        "de": "✅ {name} hat angenommen! Triff deine Wahl:\n\n✊ Stein  ✌️ Schere  🖐 Papier",
    },
    "ch_accepted_p2": {
        "ru": "⚔️ Вызов принят! Делай выбор — соперник не увидит его до конца:\n\n✊ Камень  ✌️ Ножницы  🖐 Бумага",
        "en": "⚔️ Challenge accepted! Make your choice:\n\n✊ Rock  ✌️ Scissors  🖐 Paper",
        "pt": "⚔️ Desafio aceito! Faça sua escolha:\n\n✊ Pedra  ✌️ Tesoura  🖐 Papel",
        "es": "⚔️ ¡Desafío aceptado! Haz tu elección:\n\n✊ Piedra  ✌️ Tijera  🖐 Papel",
        "tr": "⚔️ Meydan okuma kabul edildi! Seçimini yap:\n\n✊ Taş  ✌️ Makas  🖐 Kağıt",
        "de": "⚔️ Herausforderung angenommen! Wähle:\n\n✊ Stein  ✌️ Schere  🖐 Papier",
    },
    "ch_waiting":    {"ru": "✅ Выбор принят! Ждём хода соперника... ⏳",   "en": "✅ Choice saved! Waiting for opponent... ⏳",    "pt": "✅ Escolha salva! Aguardando oponente... ⏳",    "es": "✅ ¡Elección guardada! Esperando... ⏳",   "tr": "✅ Seçim kaydedildi! Rakip bekleniyor... ⏳", "de": "✅ Wahl gespeichert! Warte auf Gegner... ⏳"},
    "ch_result": {
        "ru": "🏆 Результат матча!\n\n{p1name}: {p1icon}\n{p2name}: {p2icon}\n\n{verdict}",
        "en": "🏆 Match result!\n\n{p1name}: {p1icon}\n{p2name}: {p2icon}\n\n{verdict}",
        "pt": "🏆 Resultado da partida!\n\n{p1name}: {p1icon}\n{p2name}: {p2icon}\n\n{verdict}",
        "es": "🏆 ¡Resultado del partido!\n\n{p1name}: {p1icon}\n{p2name}: {p2icon}\n\n{verdict}",
        "tr": "🏆 Maç sonucu!\n\n{p1name}: {p1icon}\n{p2name}: {p2icon}\n\n{verdict}",
        "de": "🏆 Matchergebnis!\n\n{p1name}: {p1icon}\n{p2name}: {p2icon}\n\n{verdict}",
    },
    "ch_you_win":    {"ru": "🎉 Ты победил!",     "en": "🎉 You win!",    "pt": "🎉 Você ganhou!",  "es": "🎉 ¡Ganaste!",    "tr": "🎉 Kazandın!",    "de": "🎉 Du gewinnst!"},
    "ch_you_lose":   {"ru": "😔 Ты проиграл!",    "en": "😔 You lose!",   "pt": "😔 Você perdeu!",  "es": "😔 ¡Perdiste!",   "tr": "😔 Kaybettin!",   "de": "😔 Du verlierst!"},
    "ch_draw":       {"ru": "🤝 Ничья!",           "en": "🤝 Draw!",       "pt": "🤝 Empate!",       "es": "🤝 ¡Empate!",     "tr": "🤝 Berabere!",    "de": "🤝 Unentschieden!"},
    "ch_declined":   {"ru": "❌ Вызов отклонён.",  "en": "❌ Challenge declined.", "pt": "❌ Desafio recusado.", "es": "❌ Desafío rechazado.", "tr": "❌ Reddedildi.", "de": "❌ Abgelehnt."},
    "ch_p1_declined":{"ru": "😔 {name} отклонил твой вызов.", "en": "😔 {name} declined your challenge.", "pt": "😔 {name} recusou.", "es": "😔 {name} rechazó.", "tr": "😔 {name} reddetti.", "de": "😔 {name} abgelehnt."},
    "ch_not_found":  {"ru": "❌ Вызов не найден или завершён.", "en": "❌ Challenge not found or finished.", "pt": "❌ Desafio não encontrado.", "es": "❌ Desafío no encontrado.", "tr": "❌ Meydan okuma bulunamadı.", "de": "❌ Nicht gefunden."},
    "ch_own":        {"ru": "❌ Нельзя принять собственный вызов.", "en": "❌ You cannot accept your own challenge.", "pt": "❌ Não pode aceitar seu próprio desafio.", "es": "❌ No puedes aceptar tu propio desafío.", "tr": "❌ Kendi meydan okumanı kabul edemezsin.", "de": "❌ Eigene Herausforderung nicht möglich."},
}


def t(key, lang="ru"):
    return TR.get(key, {}).get(lang) or TR.get(key, {}).get("ru") or key


# ─── Database ─────────────────────────────────────────────────────────────────────

def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id  INTEGER PRIMARY KEY,
                name     TEXT,
                username TEXT,
                lang     TEXT DEFAULT 'ru',
                coins    INTEGER DEFAULT 0,
                ref_code TEXT UNIQUE,
                ref_by   INTEGER DEFAULT NULL
            )
        """)
        conn.execute("CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)")
        conn.execute("CREATE TABLE IF NOT EXISTS fwd_map (msg_id INTEGER PRIMARY KEY, user_id INTEGER)")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS challenges (
                code   TEXT PRIMARY KEY,
                p1     INTEGER,
                p2     INTEGER,
                p1c    TEXT,
                p2c    TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS promo_codes (
                code      TEXT PRIMARY KEY,
                coins     INTEGER,
                max_uses  INTEGER,
                uses      INTEGER DEFAULT 0
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS promo_uses (
                code    TEXT,
                user_id INTEGER,
                PRIMARY KEY (code, user_id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS private_access (
                user_id    INTEGER PRIMARY KEY,
                granted_at TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daily_spin (
                user_id   INTEGER PRIMARY KEY,
                last_spin TEXT
            )
        """)
        # Migrations for existing DB
        for col_sql in [
            "ALTER TABLE users ADD COLUMN coins INTEGER DEFAULT 0",
            "ALTER TABLE users ADD COLUMN ref_code TEXT",
            "ALTER TABLE users ADD COLUMN ref_by INTEGER DEFAULT NULL",
        ]:
            try:
                conn.execute(col_sql)
            except Exception:
                pass


def _gen_ref_code():
    chars = string.ascii_uppercase + string.digits
    while True:
        code = ''.join(random.choices(chars, k=8))
        with get_conn() as conn:
            if not conn.execute("SELECT 1 FROM users WHERE ref_code=?", (code,)).fetchone():
                return code


def db_register(user):
    with get_conn() as conn:
        row = conn.execute("SELECT ref_code FROM users WHERE user_id=?", (user.id,)).fetchone()
        if row:
            conn.execute(
                "UPDATE users SET name=?, username=? WHERE user_id=?",
                (user.first_name, user.username or "", user.id)
            )
        else:
            conn.execute(
                "INSERT INTO users (user_id, name, username, lang, coins, ref_code) VALUES (?,?,?,'ru',0,?)",
                (user.id, user.first_name, user.username or "", _gen_ref_code())
            )


def db_apply_referral(new_user_id, ref_code):
    with get_conn() as conn:
        row = conn.execute("SELECT user_id FROM users WHERE ref_code=?", (ref_code,)).fetchone()
        if not row:
            return None
        referrer_id = row[0]
        if referrer_id == new_user_id:
            return None
        already = conn.execute("SELECT ref_by FROM users WHERE user_id=?", (new_user_id,)).fetchone()
        if already and already[0] is not None:
            return None
        conn.execute("UPDATE users SET coins=coins+? WHERE user_id=?", (REF_BONUS, new_user_id))
        conn.execute("UPDATE users SET coins=coins+? WHERE user_id=?", (REF_BONUS, referrer_id))
        conn.execute("UPDATE users SET ref_by=? WHERE user_id=?", (referrer_id, new_user_id))
        return referrer_id


def db_get_user(user_id):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT user_id, name, username, lang, coins, ref_code FROM users WHERE user_id=?", (user_id,)
        ).fetchone()
        if row:
            return {"id": row[0], "name": row[1], "username": row[2],
                    "lang": row[3], "coins": row[4], "ref_code": row[5]}
        return None


def db_get_lang(user_id):
    with get_conn() as conn:
        row = conn.execute("SELECT lang FROM users WHERE user_id=?", (user_id,)).fetchone()
        return row[0] if row else "ru"


def db_set_lang(user_id, lang):
    with get_conn() as conn:
        conn.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, user_id))


def db_get_coins(user_id):
    with get_conn() as conn:
        row = conn.execute("SELECT coins FROM users WHERE user_id=?", (user_id,)).fetchone()
        return row[0] if row else 0


def db_add_coins(user_id, amount):
    with get_conn() as conn:
        conn.execute("UPDATE users SET coins=MAX(0, coins+?) WHERE user_id=?", (amount, user_id))


def db_user_count():
    with get_conn() as conn:
        return conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]


def db_all_users():
    with get_conn() as conn:
        return conn.execute("SELECT user_id, name, username FROM users").fetchall()


def db_all_users_full():
    with get_conn() as conn:
        return conn.execute(
            "SELECT user_id, name, username, coins FROM users ORDER BY coins DESC"
        ).fetchall()


def db_is_admin(user_id):
    with get_conn() as conn:
        return bool(conn.execute("SELECT 1 FROM admins WHERE user_id=?", (user_id,)).fetchone())


def db_get_admins():
    with get_conn() as conn:
        return conn.execute(
            "SELECT u.user_id, u.name, u.username FROM admins a JOIN users u ON u.user_id=a.user_id"
        ).fetchall()


def db_add_admin(user_id):
    with get_conn() as conn:
        conn.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))


def db_remove_admin(user_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM admins WHERE user_id=?", (user_id,))


def db_add_fwd(msg_id, user_id):
    with get_conn() as conn:
        conn.execute("INSERT OR REPLACE INTO fwd_map (msg_id, user_id) VALUES (?,?)", (msg_id, user_id))


def db_get_fwd(msg_id):
    with get_conn() as conn:
        row = conn.execute("SELECT user_id FROM fwd_map WHERE msg_id=?", (msg_id,)).fetchone()
        return row[0] if row else None


# Challenges

def db_create_challenge(p1):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    with get_conn() as conn:
        conn.execute("INSERT INTO challenges (code, p1, status) VALUES (?,?,'pending')", (code, p1))
    return code


def db_get_challenge(code):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT code, p1, p2, p1c, p2c, status FROM challenges WHERE code=?", (code,)
        ).fetchone()
        if row:
            return {"code": row[0], "p1": row[1], "p2": row[2],
                    "p1c": row[3], "p2c": row[4], "status": row[5]}
        return None


def db_accept_challenge(code, p2):
    with get_conn() as conn:
        conn.execute("UPDATE challenges SET p2=?, status='accepted' WHERE code=?", (p2, code))


def db_set_choice(code, player, choice):
    col = "p1c" if player == 1 else "p2c"
    with get_conn() as conn:
        conn.execute(f"UPDATE challenges SET {col}=? WHERE code=?", (choice, code))


def db_finish_challenge(code):
    with get_conn() as conn:
        conn.execute("UPDATE challenges SET status='done' WHERE code=?", (code,))


# Promo codes

def db_create_promo(code, coins, max_uses):
    with get_conn() as conn:
        try:
            conn.execute(
                "INSERT INTO promo_codes (code, coins, max_uses, uses) VALUES (?,?,?,0)",
                (code, coins, max_uses)
            )
            return True
        except Exception:
            return False


def db_use_promo(code, user_id):
    with get_conn() as conn:
        promo = conn.execute(
            "SELECT coins, max_uses, uses FROM promo_codes WHERE code=?", (code,)
        ).fetchone()
        if not promo:
            return None, "not_found"
        coins, max_uses, uses = promo
        if uses >= max_uses:
            return None, "exhausted"
        already = conn.execute(
            "SELECT 1 FROM promo_uses WHERE code=? AND user_id=?", (code, user_id)
        ).fetchone()
        if already:
            return None, "already_used"
        conn.execute("UPDATE promo_codes SET uses=uses+1 WHERE code=?", (code,))
        conn.execute("INSERT INTO promo_uses (code, user_id) VALUES (?,?)", (code, user_id))
        conn.execute("UPDATE users SET coins=coins+? WHERE user_id=?", (coins, user_id))
        return coins, "ok"


def db_list_promos():
    with get_conn() as conn:
        return conn.execute("SELECT code, coins, max_uses, uses FROM promo_codes").fetchall()


def db_delete_promo(code):
    with get_conn() as conn:
        conn.execute("DELETE FROM promo_codes WHERE code=?", (code,))
        conn.execute("DELETE FROM promo_uses WHERE code=?", (code,))


# Private access

def db_has_private(user_id):
    with get_conn() as conn:
        return bool(conn.execute(
            "SELECT 1 FROM private_access WHERE user_id=?", (user_id,)
        ).fetchone())


def db_buy_private(user_id):
    with get_conn() as conn:
        coins_row = conn.execute("SELECT coins FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not coins_row or coins_row[0] < PRIVATE_COST:
            return False
        conn.execute("UPDATE users SET coins=coins-? WHERE user_id=?", (PRIVATE_COST, user_id))
        conn.execute(
            "INSERT OR IGNORE INTO private_access (user_id, granted_at) VALUES (?,?)",
            (user_id, datetime.now().strftime("%Y-%m-%d %H:%M"))
        )
        return True


# Daily spin
SPIN_PRIZES = [
    (5,  40),   # 5 coins  — 40% chance
    (10, 30),   # 10 coins — 30%
    (15, 15),   # 15 coins — 15%
    (20, 10),   # 20 coins — 10%
    (50,  5),   # 50 coins —  5%
]
SPIN_REELS = {5: "🍋 🍋 🍋", 10: "🍊 🍊 🍊", 15: "🍇 🍇 🍇", 20: "⭐ ⭐ ⭐", 50: "💎 💎 💎"}

def _spin_roll():
    pool = []
    for prize, weight in SPIN_PRIZES:
        pool.extend([prize] * weight)
    return random.choice(pool)

def db_can_spin(user_id):
    """Returns (can_spin: bool, hours_left: int, mins_left: int)"""
    with get_conn() as conn:
        row = conn.execute("SELECT last_spin FROM daily_spin WHERE user_id=?", (user_id,)).fetchone()
        if not row:
            return True, 0, 0
        last = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - last
        if diff.total_seconds() >= 86400:
            return True, 0, 0
        remaining = 86400 - diff.total_seconds()
        hours = int(remaining // 3600)
        mins = int((remaining % 3600) // 60)
        return False, hours, mins

def db_do_spin(user_id):
    """Do spin: update last_spin, add coins. Returns coins won."""
    prize = _spin_roll()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO daily_spin (user_id, last_spin) VALUES (?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET last_spin=excluded.last_spin",
            (user_id, now)
        )
        conn.execute("UPDATE users SET coins=coins+? WHERE user_id=?", (prize, user_id))
    return prize


# ─── Roles ────────────────────────────────────────────────────────────────────────

def get_role(user_id):
    if user_id == OWNER_ID:
        return "owner"
    if db_is_admin(user_id):
        return "admin"
    return "user"


# ─── AI ──────────────────────────────────────────────────────────────────────────

async def rephrase_formal(text):
    try:
        r = await g4f.ChatCompletion.create_async(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content":
                f"Перефразируй вопрос формально и грамотно, не меняя смысл. Только результат:\n{text}"}]
        )
        return r.strip() if r else text
    except Exception:
        return text


async def rephrase_admin_reply(text):
    try:
        r = await g4f.ChatCompletion.create_async(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content":
                f"Перефразируй ответ администратора вежливо и профессионально. Только результат:\n{text}"}]
        )
        return r.strip() if r else text
    except Exception:
        return text


# ─── Keyboards ───────────────────────────────────────────────────────────────────

def main_keyboard(lang, role):
    kb = [
        [InlineKeyboardButton(t("btn_get_dlc", lang), callback_data="get_dlc")],
        [
            InlineKeyboardButton(t("btn_profile", lang), callback_data="profile"),
            InlineKeyboardButton(t("btn_faq", lang), callback_data="faq"),
        ],
        [
            InlineKeyboardButton(t("btn_games", lang), callback_data="games"),
            InlineKeyboardButton(t("btn_leaderboard", lang), callback_data="leaderboard"),
        ],
    ]
    if role in ("admin", "owner"):
        kb.append([InlineKeyboardButton(t("btn_panel", lang), callback_data="panel")])
    return InlineKeyboardMarkup(kb)


def panel_keyboard(role):
    kb = [
        [
            InlineKeyboardButton("📊 Статистика", callback_data="stats"),
            InlineKeyboardButton("📨 Рассылка", callback_data="broadcast"),
        ],
        [
            InlineKeyboardButton("💰 Выдать коины", callback_data="give_coins"),
            InlineKeyboardButton("💸 Забрать коины", callback_data="take_coins"),
        ],
        [
            InlineKeyboardButton("🎁 Создать промокод", callback_data="create_promo"),
            InlineKeyboardButton("📋 Промокоды", callback_data="list_promos"),
        ],
        [InlineKeyboardButton("👥 База пользователей", callback_data="user_db")],
    ]
    if role == "owner":
        kb.append([
            InlineKeyboardButton("➕ Добавить админа", callback_data="add_admin"),
            InlineKeyboardButton("➖ Снять админа", callback_data="remove_admin"),
        ])
    kb.append([InlineKeyboardButton("⬅️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(kb)


# ─── Handlers ─────────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db_register(user)
    lang = db_get_lang(user.id)
    role = get_role(user.id)

    if context.args:
        arg = context.args[0]
        if arg.startswith("ref_"):
            ref_code = arg[4:]
            referrer_id = db_apply_referral(user.id, ref_code)
            if referrer_id:
                await update.message.reply_text(
                    t("ref_bonus_new", lang).replace("{coins}", str(REF_BONUS)),
                    parse_mode="HTML"
                )
                ref_lang = db_get_lang(referrer_id)
                try:
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=t("ref_bonus_ref", ref_lang)
                            .replace("{name}", user.first_name)
                            .replace("{coins}", str(REF_BONUS)),
                        parse_mode="HTML"
                    )
                except Exception:
                    pass

    await update.message.reply_text(
        t("welcome", lang),
        reply_markup=main_keyboard(lang, role)
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    lang = db_get_lang(user.id)
    role = get_role(user.id)

    # ── Main menu / back ─────────────────────────────────────────────────────────
    if query.data == "back":
        context.user_data.clear()
        await query.edit_message_text(
            t("welcome", lang),
            reply_markup=main_keyboard(lang, role)
        )

    # ── Get DLC ──────────────────────────────────────────────────────────────────
    elif query.data == "get_dlc":
        has = db_has_private(user.id)
        coins = db_get_coins(user.id)
        if has:
            kb = [
                [InlineKeyboardButton(t("btn_download_apk", lang), url=DLC_CHANNEL)],
                [InlineKeyboardButton(t("btn_back", lang), callback_data="back")],
            ]
            await query.edit_message_text(
                t("dlc_has_access", lang),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
        else:
            kb = [
                [InlineKeyboardButton(t("btn_buy_access", lang), callback_data="confirm_buy")],
                [InlineKeyboardButton(t("btn_back", lang), callback_data="back")],
            ]
            await query.edit_message_text(
                t("dlc_no_access", lang).replace("{coins}", str(coins)),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )

    # ── Confirm buy ──────────────────────────────────────────────────────────────
    elif query.data == "confirm_buy":
        coins = db_get_coins(user.id)
        if coins < PRIVATE_COST:
            kb = [[InlineKeyboardButton(t("btn_back", lang), callback_data="get_dlc")]]
            await query.edit_message_text(
                t("buy_no_coins", lang)
                    .replace("{coins}", str(coins))
                    .replace("{ref}", str(REF_BONUS)),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
            return
        after = coins - PRIVATE_COST
        kb = [
            [InlineKeyboardButton(t("btn_confirm_buy", lang), callback_data="do_buy")],
            [InlineKeyboardButton(t("btn_back", lang), callback_data="get_dlc")],
        ]
        await query.edit_message_text(
            t("buy_confirm_text", lang)
                .replace("{coins}", str(coins))
                .replace("{after}", str(after)),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )

    # ── Do buy ───────────────────────────────────────────────────────────────────
    elif query.data == "do_buy":
        if db_has_private(user.id):
            kb = [
                [InlineKeyboardButton(t("btn_download_apk", lang), url=DLC_CHANNEL)],
                [InlineKeyboardButton(t("btn_back", lang), callback_data="back")],
            ]
            await query.edit_message_text(
                t("dlc_has_access", lang),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
            return
        success = db_buy_private(user.id)
        if success:
            kb = [
                [InlineKeyboardButton(t("btn_download_apk", lang), url=DLC_CHANNEL)],
                [InlineKeyboardButton(t("btn_back", lang), callback_data="back")],
            ]
            await query.edit_message_text(
                t("buy_success", lang),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
        else:
            coins = db_get_coins(user.id)
            kb = [[InlineKeyboardButton(t("btn_back", lang), callback_data="get_dlc")]]
            await query.edit_message_text(
                t("buy_no_coins", lang)
                    .replace("{coins}", str(coins))
                    .replace("{ref}", str(REF_BONUS)),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )

    # ── Profile ──────────────────────────────────────────────────────────────────
    elif query.data == "profile":
        context.user_data.pop("waiting_action", None)
        context.user_data.pop("waiting_question", None)
        info = db_get_user(user.id)
        coins = info["coins"] if info else 0
        ref_code = info["ref_code"] if info else "—"
        has_private = db_has_private(user.id)
        bot_username = (await context.bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start=ref_{ref_code}"

        role_labels = {
            "owner":  {"ru": "👑 Владелец",       "en": "👑 Owner",        "pt": "👑 Dono",        "es": "👑 Dueño",       "tr": "👑 Sahip",       "de": "👑 Eigentümer"},
            "admin":  {"ru": "🛡 Администратор",   "en": "🛡 Administrator", "pt": "🛡 Administrador","es": "🛡 Administrador","tr": "🛡 Yönetici",    "de": "🛡 Administrator"},
            "user":   {"ru": "👤 Пользователь",    "en": "👤 User",         "pt": "👤 Usuário",      "es": "👤 Usuario",     "tr": "👤 Kullanıcı",   "de": "👤 Nutzer"},
        }
        access_label = {
            "ru": "✅ Есть" if has_private else "❌ Нет",
            "en": "✅ Yes" if has_private else "❌ No",
            "pt": "✅ Sim" if has_private else "❌ Não",
            "es": "✅ Sí" if has_private else "❌ No",
            "tr": "✅ Var" if has_private else "❌ Yok",
            "de": "✅ Ja" if has_private else "❌ Nein",
        }
        name_label   = {"ru": "📛 Имя",            "en": "📛 Name",         "pt": "📛 Nome",         "es": "📛 Nombre",      "tr": "📛 Ad",           "de": "📛 Name"}
        id_label     = {"ru": "🆔 ID",              "en": "🆔 ID",           "pt": "🆔 ID",           "es": "🆔 ID",          "tr": "🆔 ID",           "de": "🆔 ID"}
        role_label   = {"ru": "⭐ Роль",            "en": "⭐ Role",         "pt": "⭐ Função",       "es": "⭐ Rol",         "tr": "⭐ Rol",          "de": "⭐ Rolle"}
        coins_label  = {"ru": "🪙 Коины",           "en": "🪙 Coins",        "pt": "🪙 Moedas",       "es": "🪙 Monedas",     "tr": "🪙 Coinler",     "de": "🪙 Coins"}
        access_lbl   = {"ru": "🔑 Приватный доступ","en": "🔑 Private access","pt": "🔑 Acesso privado","es": "🔑 Acceso privado","tr": "🔑 Özel erişim","de": "🔑 Privater Zugang"}
        ref_lbl      = {"ru": "🔗 Реферальная ссылка","en": "🔗 Referral link","pt": "🔗 Link de referência","es": "🔗 Enlace referido","tr": "🔗 Referans linki","de": "🔗 Empfehlungslink"}

        text = (
            f"👤 <b>{t('btn_profile', lang)}</b>\n\n"
            f"{name_label.get(lang, name_label['ru'])}: <b>{user.first_name}</b>\n"
            f"{id_label.get(lang, id_label['ru'])}: <code>{user.id}</code>\n"
            f"{role_label.get(lang, role_label['ru'])}: {role_labels[role].get(lang, role_labels[role]['ru'])}\n"
            f"{coins_label.get(lang, coins_label['ru'])}: <b>{coins} 🪙</b>\n"
            f"{access_lbl.get(lang, access_lbl['ru'])}: {access_label.get(lang, access_label['ru'])}\n\n"
            f"{ref_lbl.get(lang, ref_lbl['ru'])}:\n<code>{ref_link}</code>"
        )
        kb = [
            [InlineKeyboardButton(t("btn_purchases", lang), callback_data="purchases")],
            [InlineKeyboardButton(t("btn_promo", lang), callback_data="activate_promo")],
            [InlineKeyboardButton(t("btn_language", lang), callback_data="language")],
            [InlineKeyboardButton(t("btn_back", lang), callback_data="back")],
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")

    # ── Purchases ─────────────────────────────────────────────────────────────────
    elif query.data == "purchases":
        has = db_has_private(user.id)
        if has:
            item_name = {"ru": "⭐ Приватный чит — Fwd Assault", "en": "⭐ Private cheat — Fwd Assault",
                         "pt": "⭐ Cheat privado — Fwd Assault", "es": "⭐ Cheat privado — Fwd Assault",
                         "tr": "⭐ Özel hile — Fwd Assault",     "de": "⭐ Privater Cheat — Fwd Assault"}.get(lang, "⭐ Private cheat — Fwd Assault")
            with get_conn() as conn:
                row = conn.execute("SELECT granted_at FROM private_access WHERE user_id=?", (user.id,)).fetchone()
            date_str = row[0][:10] if row else "—"
            kb = [
                [InlineKeyboardButton(t("btn_download_apk", lang), url=DLC_CHANNEL)],
                [InlineKeyboardButton(t("btn_back", lang), callback_data="profile")],
            ]
            await query.edit_message_text(
                f"🛒 <b>Информация о покупке</b>\n\n"
                f"🛒 Товар: {item_name}\n"
                f"🗝 Ключ: Android APK\n"
                f"⏳ Дата покупки: {date_str}",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
        else:
            item_name = {"ru": "🆓 Нет покупок", "en": "🆓 No purchases",
                         "pt": "🆓 Sem compras", "es": "🆓 Sin compras",
                         "tr": "🆓 Satın alma yok", "de": "🆓 Keine Käufe"}.get(lang, "🆓 No purchases")
            kb = [
                [InlineKeyboardButton(t("btn_buy_access", lang), callback_data="confirm_buy")],
                [InlineKeyboardButton(t("btn_back", lang), callback_data="profile")],
            ]
            await query.edit_message_text(
                f"🛒 <b>Информация о покупке</b>\n\n"
                f"🛒 Товар: {item_name}\n"
                f"🗝 Ключ: —\n"
                f"⏳ Дата покупки: —",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )

    # ── Activate promo ────────────────────────────────────────────────────────────
    elif query.data == "activate_promo":
        context.user_data["waiting_action"] = "promo_input"
        kb = [[InlineKeyboardButton(t("btn_back", lang), callback_data="profile")]]
        await query.edit_message_text(
            t("promo_prompt", lang),
            reply_markup=InlineKeyboardMarkup(kb)
        )

    # ── Language ──────────────────────────────────────────────────────────────────
    elif query.data == "language":
        kb = [
            [InlineKeyboardButton(name, callback_data=f"lang_{code}")]
            for code, name in LANGUAGES.items()
        ]
        kb.append([InlineKeyboardButton(t("btn_back", lang), callback_data="profile")])
        await query.edit_message_text(
            t("lang_choose", lang),
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif query.data.startswith("lang_"):
        new_lang = query.data[5:]
        if new_lang in LANGUAGES:
            db_set_lang(user.id, new_lang)
            lang = new_lang
        kb = [
            [InlineKeyboardButton(t("btn_profile", lang), callback_data="profile")],
            [InlineKeyboardButton(t("btn_back", lang), callback_data="back")],
        ]
        await query.edit_message_text(
            t("lang_changed", lang),
            reply_markup=InlineKeyboardMarkup(kb)
        )

    # ── FAQ ───────────────────────────────────────────────────────────────────────
    elif query.data == "faq":
        context.user_data["waiting_question"] = True
        kb = [[InlineKeyboardButton(t("btn_back", lang), callback_data="back")]]
        await query.edit_message_text(t("faq_text", lang), reply_markup=InlineKeyboardMarkup(kb))

    # ── Games ─────────────────────────────────────────────────────────────────────
    elif query.data == "games":
        context.user_data.pop("waiting_question", None)
        context.user_data.pop("waiting_action", None)
        context.user_data.pop("guess_number", None)
        context.user_data.pop("guess_tries", None)
        can_spin, _, _ = db_can_spin(user.id)
        spin_label = {
            "ru": "🎰 Ежедневный спин" + (" ✅" if can_spin else " ⏳"),
            "en": "🎰 Daily Spin" + (" ✅" if can_spin else " ⏳"),
            "pt": "🎰 Giro Diário" + (" ✅" if can_spin else " ⏳"),
            "es": "🎰 Giro Diario" + (" ✅" if can_spin else " ⏳"),
            "tr": "🎰 Günlük Çevirme" + (" ✅" if can_spin else " ⏳"),
            "de": "🎰 Täglicher Spin" + (" ✅" if can_spin else " ⏳"),
        }.get(lang, "🎰 Daily Spin")
        coin_label = {"ru": "🪙 Угадай монету (+3 🪙)", "en": "🪙 Coin Flip (+3 🪙)", "pt": "🪙 Cara ou Coroa (+3 🪙)", "es": "🪙 Cara o Cruz (+3 🪙)", "tr": "🪙 Yazı Tura (+3 🪙)", "de": "🪙 Münzwurf (+3 🪙)"}.get(lang, "🪙 Coin Flip (+3 🪙)")
        casino_label = {"ru": "🎲 Казино", "en": "🎲 Casino", "pt": "🎲 Cassino", "es": "🎲 Casino", "tr": "🎲 Kumarhane", "de": "🎲 Casino"}.get(lang, "🎲 Casino")
        kb = [
            [InlineKeyboardButton(spin_label, callback_data="game_spin")],
            [InlineKeyboardButton(coin_label, callback_data="game_coin")],
            [InlineKeyboardButton(casino_label, callback_data="game_casino")],
            [InlineKeyboardButton("🔢 Угадай число", callback_data="game_guess")],
            [InlineKeyboardButton("✊ Камень-Ножницы-Бумага", callback_data="game_rps")],
            [InlineKeyboardButton(t("btn_back", lang), callback_data="back")],
        ]
        await query.edit_message_text(t("games_menu", lang), reply_markup=InlineKeyboardMarkup(kb))

    elif query.data == "game_spin":
        can_spin, hours, mins = db_can_spin(user.id)
        coins = db_get_coins(user.id)
        if not can_spin:
            kb = [[InlineKeyboardButton(t("btn_back", lang), callback_data="games")]]
            await query.edit_message_text(
                t("spin_cooldown", lang).replace("{hours}", str(hours)).replace("{mins}", str(mins)),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
            return
        # Show spin button
        kb = [
            [InlineKeyboardButton(t("btn_spin", lang), callback_data="do_spin")],
            [InlineKeyboardButton(t("btn_back", lang), callback_data="games")],
        ]
        await query.edit_message_text(
            t("spin_title", lang).replace("{coins}", str(coins)),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )

    elif query.data == "do_spin":
        can_spin, hours, mins = db_can_spin(user.id)
        if not can_spin:
            kb = [[InlineKeyboardButton(t("btn_back", lang), callback_data="games")]]
            await query.edit_message_text(
                t("spin_cooldown", lang).replace("{hours}", str(hours)).replace("{mins}", str(mins)),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
            return
        prize = db_do_spin(user.id)
        total = db_get_coins(user.id)
        reel = SPIN_REELS.get(prize, "🎰 🎰 🎰")
        kb = [[InlineKeyboardButton(t("btn_back", lang), callback_data="games")]]
        await query.edit_message_text(
            t("spin_result", lang)
                .replace("{reel}", reel)
                .replace("{coins}", str(prize))
                .replace("{total}", str(total)),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )

    elif query.data == "game_coin":
        coins = db_get_coins(user.id)
        kb = [
            [
                InlineKeyboardButton(t("btn_coin_heads", lang), callback_data="coin_heads"),
                InlineKeyboardButton(t("btn_coin_tails", lang), callback_data="coin_tails"),
            ],
            [InlineKeyboardButton(t("btn_back", lang), callback_data="games")],
        ]
        await query.edit_message_text(
            t("coin_title", lang).replace("{coins}", str(coins)),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )

    elif query.data in ("coin_heads", "coin_tails"):
        result = random.choice(["heads", "tails"])
        user_pick = "heads" if query.data == "coin_heads" else "tails"
        icons = {"heads": "👑 Орёл" if lang == "ru" else "👑 Heads", "tails": "🌀 Решка" if lang == "ru" else "🌀 Tails"}
        result_icon = icons[result]
        coins = db_get_coins(user.id)
        kb = [
            [
                InlineKeyboardButton(t("btn_coin_heads", lang), callback_data="coin_heads"),
                InlineKeyboardButton(t("btn_coin_tails", lang), callback_data="coin_tails"),
            ],
            [InlineKeyboardButton(t("btn_back", lang), callback_data="games")],
        ]
        if user_pick == result:
            db_add_coins(user.id, 3)
            total = db_get_coins(user.id)
            await query.edit_message_text(
                t("coin_win", lang).replace("{icon}", result_icon).replace("{total}", str(total)),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
        else:
            total = coins
            await query.edit_message_text(
                t("coin_lose", lang).replace("{icon}", result_icon).replace("{total}", str(total)),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )

    elif query.data == "game_casino":
        coins = db_get_coins(user.id)
        context.user_data["waiting_action"] = "casino_bet"
        kb = [[InlineKeyboardButton(t("btn_back", lang), callback_data="games")]]
        await query.edit_message_text(
            t("casino_menu", lang).replace("{coins}", str(coins)),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )

    elif query.data == "leaderboard":
        rows = db_conn().execute(
            "SELECT user_id, name, username, coins FROM users ORDER BY coins DESC LIMIT 20"
        ).fetchall()
        medals = {1: "🥇", 2: "🥈", 3: "🥉"}
        lines = []
        user_rank = None
        for i, (uid, name, uname, c) in enumerate(rows, 1):
            tag = medals.get(i, f"{i}.")
            display = f"@{uname}" if uname else (name or "???")
            lines.append(f"{tag} <b>{display}</b> — <b>{c} 🪙</b>")
            if uid == user.id:
                user_rank = (i, c)
        if not user_rank:
            all_ids = db_conn().execute(
                "SELECT user_id FROM users ORDER BY coins DESC"
            ).fetchall()
            for idx, (uid,) in enumerate(all_ids, 1):
                if uid == user.id:
                    user_rank = (idx, db_get_coins(user.id))
                    break
        rows_text = "\n".join(lines) if lines else "—"
        text = t("leaderboard_title", lang).replace("{rows}", rows_text)
        if user_rank:
            text += "\n\n" + t("your_rank", lang).replace("{rank}", str(user_rank[0])).replace("{coins}", str(user_rank[1]))
        kb = [[InlineKeyboardButton(t("btn_back", lang), callback_data="back")]]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="HTML")

    elif query.data == "game_guess":
        number = random.randint(1, 100)
        context.user_data["guess_number"] = number
        context.user_data["guess_tries"] = 0
        context.user_data["waiting_action"] = "guessing"
        kb = [[InlineKeyboardButton(t("btn_back", lang), callback_data="games")]]
        await query.edit_message_text(t("guess_start", lang), reply_markup=InlineKeyboardMarkup(kb))

    elif query.data == "game_rps":
        kb = [
            [InlineKeyboardButton(t("rps_vs_bot", lang), callback_data="rps_vsbot")],
            [InlineKeyboardButton(t("rps_vs_player", lang), callback_data="rps_vsp")],
            [InlineKeyboardButton(t("btn_back", lang), callback_data="games")],
        ]
        await query.edit_message_text(t("rps_choose", lang), reply_markup=InlineKeyboardMarkup(kb))

    elif query.data == "rps_vsbot":
        kb = [
            [
                InlineKeyboardButton("✊", callback_data="rps_rock"),
                InlineKeyboardButton("✌️", callback_data="rps_scissors"),
                InlineKeyboardButton("🖐", callback_data="rps_paper"),
            ],
            [InlineKeyboardButton(t("btn_back", lang), callback_data="game_rps")],
        ]
        await query.edit_message_text(t("rps_choose", lang), reply_markup=InlineKeyboardMarkup(kb))

    elif query.data in ("rps_rock", "rps_scissors", "rps_paper"):
        choices = {"rps_rock": "✊", "rps_scissors": "✌️", "rps_paper": "🖐"}
        wins_against = {"rps_rock": "rps_scissors", "rps_scissors": "rps_paper", "rps_paper": "rps_rock"}
        bot_key = random.choice(list(choices.keys()))
        user_key = query.data
        user_icon, bot_icon = choices[user_key], choices[bot_key]
        if user_key == bot_key:
            result_text = t("rps_draw", lang).format(user=user_icon, bot=bot_icon)
        elif wins_against[user_key] == bot_key:
            result_text = t("rps_win", lang).format(user=user_icon, bot=bot_icon)
        else:
            result_text = t("rps_lose", lang).format(user=user_icon, bot=bot_icon)
        kb = [
            [
                InlineKeyboardButton("✊", callback_data="rps_rock"),
                InlineKeyboardButton("✌️", callback_data="rps_scissors"),
                InlineKeyboardButton("🖐", callback_data="rps_paper"),
            ],
            [InlineKeyboardButton(t("btn_back", lang), callback_data="game_rps")],
        ]
        await query.edit_message_text(result_text, reply_markup=InlineKeyboardMarkup(kb))

    elif query.data == "rps_vsp":
        code = db_create_challenge(user.id)
        kb = [[InlineKeyboardButton(t("btn_back", lang), callback_data="game_rps")]]
        await query.edit_message_text(
            t("ch_created", lang).replace("{code}", code),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )

    elif query.data.startswith("ch_accept_"):
        code = query.data[len("ch_accept_"):]
        ch = db_get_challenge(code)
        if not ch or ch["status"] != "pending":
            await query.edit_message_text(t("ch_not_found", lang))
            return
        if ch["p1"] == user.id:
            await query.answer(t("ch_own", lang), show_alert=True)
            return
        db_accept_challenge(code, user.id)
        p1_info = db_get_user(ch["p1"])
        p1_name = p1_info["name"] if p1_info else str(ch["p1"])
        p2_name = user.first_name
        mp_kb = InlineKeyboardMarkup([[
            InlineKeyboardButton("✊", callback_data=f"mp_rock_{code}"),
            InlineKeyboardButton("✌️", callback_data=f"mp_scissors_{code}"),
            InlineKeyboardButton("🖐", callback_data=f"mp_paper_{code}"),
        ]])
        p1_lang = db_get_lang(ch["p1"])
        await context.bot.send_message(
            chat_id=ch["p1"],
            text=t("ch_accepted_p1", p1_lang).replace("{name}", p2_name),
            reply_markup=mp_kb
        )
        await query.edit_message_text(
            t("ch_accepted_p2", lang).replace("{name}", p1_name),
            reply_markup=mp_kb
        )

    elif query.data.startswith("ch_decline_"):
        code = query.data[len("ch_decline_"):]
        ch = db_get_challenge(code)
        if not ch or ch["status"] != "pending":
            await query.edit_message_text(t("ch_not_found", lang))
            return
        db_finish_challenge(code)
        p1_lang = db_get_lang(ch["p1"])
        await context.bot.send_message(
            chat_id=ch["p1"],
            text=t("ch_p1_declined", p1_lang).replace("{name}", user.first_name)
        )
        await query.edit_message_text(t("ch_declined", lang))

    elif query.data.startswith("mp_"):
        parts = query.data.split("_", 2)
        if len(parts) != 3:
            return
        _, move, code = parts
        ch = db_get_challenge(code)
        if not ch or ch["status"] != "accepted":
            await query.answer("⏳", show_alert=False)
            return
        icons = {"rock": "✊", "scissors": "✌️", "paper": "🖐"}
        wins_against = {"rock": "scissors", "scissors": "paper", "paper": "rock"}
        if user.id == ch["p1"] and not ch["p1c"]:
            db_set_choice(code, 1, move)
            await query.edit_message_text(t("ch_waiting", lang))
        elif user.id == ch["p2"] and not ch["p2c"]:
            db_set_choice(code, 2, move)
            await query.edit_message_text(t("ch_waiting", lang))
        else:
            await query.answer("⏳", show_alert=False)
            return
        ch = db_get_challenge(code)
        if ch["p1c"] and ch["p2c"]:
            db_finish_challenge(code)
            p1c, p2c = ch["p1c"], ch["p2c"]
            p1_info = db_get_user(ch["p1"])
            p2_info = db_get_user(ch["p2"])
            p1_name = p1_info["name"] if p1_info else str(ch["p1"])
            p2_name = p2_info["name"] if p2_info else str(ch["p2"])
            if p1c == p2c:
                v1 = v2 = "ch_draw"
            elif wins_against[p1c] == p2c:
                v1, v2 = "ch_you_win", "ch_you_lose"
            else:
                v1, v2 = "ch_you_lose", "ch_you_win"
            p1_lang = db_get_lang(ch["p1"])
            p2_lang = db_get_lang(ch["p2"])
            again_kb_p1 = InlineKeyboardMarkup([[
                InlineKeyboardButton(t("btn_new_match", p1_lang), callback_data="rps_vsp"),
                InlineKeyboardButton(t("btn_games", p1_lang), callback_data="games"),
            ]])
            again_kb_p2 = InlineKeyboardMarkup([[
                InlineKeyboardButton(t("btn_new_match", p2_lang), callback_data="rps_vsp"),
                InlineKeyboardButton(t("btn_games", p2_lang), callback_data="games"),
            ]])
            for pid, vkey, plang, kb_again in [
                (ch["p1"], v1, p1_lang, again_kb_p1),
                (ch["p2"], v2, p2_lang, again_kb_p2),
            ]:
                verdict = t(vkey, plang)
                await context.bot.send_message(
                    chat_id=pid,
                    text=t("ch_result", plang)
                        .replace("{p1name}", p1_name).replace("{p1icon}", icons[p1c])
                        .replace("{p2name}", p2_name).replace("{p2icon}", icons[p2c])
                        .replace("{verdict}", verdict),
                    reply_markup=kb_again
                )

    # ── Admin panel ───────────────────────────────────────────────────────────────
    elif query.data == "panel":
        if role not in ("admin", "owner"):
            return
        await query.edit_message_text(
            "⚙️ Панель управления\n\nВыберите действие:",
            reply_markup=panel_keyboard(role)
        )

    elif query.data == "stats":
        if role not in ("admin", "owner"):
            return
        total = db_user_count()
        admins = db_get_admins()
        with get_conn() as conn:
            priv_count = conn.execute("SELECT COUNT(*) FROM private_access").fetchone()[0]
        admin_lines = "\n".join(
            f"  • {name} (@{uname}) — ID: {uid}" for uid, name, uname in admins
        ) or "  нет"
        text = (
            f"📊 <b>Статистика LUNA CLIENT</b>\n\n"
            f"👥 Всего пользователей: <b>{total}</b>\n"
            f"🔑 Пользователей с доступом: <b>{priv_count}</b>\n\n"
            f"🛡 <b>Администраторы:</b>\n{admin_lines}"
        )
        await query.edit_message_text(
            text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="panel")]])
        )

    elif query.data == "broadcast":
        if role not in ("admin", "owner"):
            return
        context.user_data["waiting_action"] = "broadcast"
        kb = [[InlineKeyboardButton("⬅️ Отмена", callback_data="panel")]]
        await query.edit_message_text(
            "📨 Рассылка\n\nНапишите сообщение для всех пользователей:",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif query.data == "give_coins":
        if role not in ("admin", "owner"):
            return
        context.user_data["waiting_action"] = "give_coins"
        kb = [[InlineKeyboardButton("⬅️ Отмена", callback_data="panel")]]
        await query.edit_message_text(
            "💰 Выдать коины\n\nВведите в формате:\n<code>ID КОЛИЧЕСТВО</code>\n\nПример: <code>123456789 100</code>",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )

    elif query.data == "take_coins":
        if role not in ("admin", "owner"):
            return
        context.user_data["waiting_action"] = "take_coins"
        kb = [[InlineKeyboardButton("⬅️ Отмена", callback_data="panel")]]
        await query.edit_message_text(
            "💸 Забрать коины\n\nВведите в формате:\n<code>ID КОЛИЧЕСТВО</code>\n\nПример: <code>123456789 50</code>",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )

    elif query.data == "create_promo":
        if role not in ("admin", "owner"):
            return
        context.user_data["waiting_action"] = "create_promo"
        kb = [[InlineKeyboardButton("⬅️ Отмена", callback_data="panel")]]
        await query.edit_message_text(
            "🎁 Создать промокод\n\nВведите данные в формате:\n<code>КОД КОИНЫ КОЛ_АКТИВАЦИЙ</code>\n\n"
            "Пример: <code>LUNA100 100 10</code>\n"
            "(промокод LUNA100, даёт 100 коинов, можно активировать 10 раз)",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="HTML"
        )

    elif query.data == "list_promos":
        if role not in ("admin", "owner"):
            return
        promos = db_list_promos()
        if promos:
            lines = "\n".join(
                f"  • <code>{code}</code> — {coins}🪙 | {uses}/{max_uses} активаций"
                for code, coins, max_uses, uses in promos
            )
        else:
            lines = "  Промокодов нет"
        await query.edit_message_text(
            f"📋 <b>Список промокодов</b>\n\n{lines}",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="panel")]])
        )

    elif query.data == "user_db":
        if role not in ("admin", "owner"):
            return
        users = db_all_users_full()
        if users:
            lines = []
            for uid, name, uname, coins in users[:50]:
                uname_str = f"@{uname}" if uname else "—"
                lines.append(f"  {name} | {uname_str} | <b>{coins} 🪙</b>")
            text = "👥 <b>База пользователей</b> (топ по коинам):\n\n" + "\n".join(lines)
            if len(users) > 50:
                text += f"\n\n... и ещё {len(users) - 50} пользователей"
        else:
            text = "👥 Пользователей нет"
        await query.edit_message_text(
            text, parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Назад", callback_data="panel")]])
        )

    elif query.data == "add_admin":
        if role != "owner":
            return
        context.user_data["waiting_action"] = "add_admin"
        kb = [[InlineKeyboardButton("⬅️ Отмена", callback_data="panel")]]
        await query.edit_message_text(
            "➕ Выдача админки\n\nВведите ID пользователя:",
            reply_markup=InlineKeyboardMarkup(kb)
        )

    elif query.data == "remove_admin":
        if role != "owner":
            return
        context.user_data["waiting_action"] = "remove_admin"
        kb = [[InlineKeyboardButton("⬅️ Отмена", callback_data="panel")]]
        await query.edit_message_text(
            "➖ Снятие админки\n\nВведите ID пользователя:",
            reply_markup=InlineKeyboardMarkup(kb)
        )


# ─── Message Handler ──────────────────────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = update.message
    role = get_role(user.id)
    lang = db_get_lang(user.id)

    # Owner replies to forwarded FAQ question
    if user.id == OWNER_ID and msg.reply_to_message and not context.user_data.get("waiting_action"):
        target_id = db_get_fwd(msg.reply_to_message.message_id)
        if target_id:
            formal_reply = await rephrase_admin_reply(msg.text)
            target_lang = db_get_lang(target_id)
            await context.bot.send_message(
                chat_id=target_id,
                text=t("admin_reply", target_lang) + formal_reply
            )
            await msg.reply_text(
                f"✅ Ответ отправлен.\n\n✏️ Формальная версия:\n{formal_reply}"
            )
            return

    action = context.user_data.get("waiting_action")

    # ── Guess the number ─────────────────────────────────────────────────────────
    if action == "guessing":
        secret = context.user_data.get("guess_number")
        tries = context.user_data.get("guess_tries", 0) + 1
        context.user_data["guess_tries"] = tries
        kb = [[InlineKeyboardButton(t("btn_back", lang), callback_data="games")]]
        try:
            guess = int(msg.text.strip())
            if guess < 1 or guess > 100:
                raise ValueError
        except ValueError:
            await msg.reply_text(t("guess_invalid", lang), reply_markup=InlineKeyboardMarkup(kb))
            return
        if guess < secret:
            await msg.reply_text(
                t("guess_higher", lang).replace("{tries}", str(tries)),
                reply_markup=InlineKeyboardMarkup(kb)
            )
        elif guess > secret:
            await msg.reply_text(
                t("guess_lower", lang).replace("{tries}", str(tries)),
                reply_markup=InlineKeyboardMarkup(kb)
            )
        else:
            context.user_data.pop("waiting_action", None)
            context.user_data.pop("guess_number", None)
            context.user_data.pop("guess_tries", None)
            win_kb = [
                [InlineKeyboardButton(t("btn_play_again", lang), callback_data="game_guess")],
                [InlineKeyboardButton(t("btn_back", lang), callback_data="games")],
            ]
            await msg.reply_text(
                t("guess_win", lang).replace("{num}", str(secret)).replace("{tries}", str(tries)),
                reply_markup=InlineKeyboardMarkup(win_kb)
            )
        return

    # ── Promo code input ─────────────────────────────────────────────────────────
    if action == "promo_input":
        context.user_data.pop("waiting_action", None)
        code = msg.text.strip().upper()
        coins_got, status = db_use_promo(code, user.id)
        kb = [[InlineKeyboardButton(t("btn_back", lang), callback_data="profile")]]
        if status == "ok":
            await msg.reply_text(
                t("promo_success", lang).replace("{coins}", str(coins_got)),
                reply_markup=InlineKeyboardMarkup(kb)
            )
        elif status == "not_found":
            await msg.reply_text(t("promo_not_found", lang), reply_markup=InlineKeyboardMarkup(kb))
        elif status == "exhausted":
            await msg.reply_text(t("promo_exhausted", lang), reply_markup=InlineKeyboardMarkup(kb))
        elif status == "already_used":
            await msg.reply_text(t("promo_already_used", lang), reply_markup=InlineKeyboardMarkup(kb))
        return

    # ── Casino bet ────────────────────────────────────────────────────────────────
    if action == "casino_bet":
        kb = [[InlineKeyboardButton(t("btn_back", lang), callback_data="games")]]
        raw = msg.text.strip()
        if not raw.isdigit():
            coins = db_get_coins(user.id)
            await msg.reply_text(
                t("casino_no_coins", lang).replace("{coins}", str(coins)),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
            return
        bet = int(raw)
        coins = db_get_coins(user.id)
        if bet < 1 or bet > coins:
            await msg.reply_text(
                t("casino_no_coins", lang).replace("{coins}", str(coins)),
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="HTML"
            )
            return
        # Pool: 10000 slots → outcome index
        # x0:40% x0.5:23% x1:14% x2:13% x5:6.5% x10:3.3% x100:0.1% (total~99.9→round up x10 to 3.4)
        CASINO_POOL = (
            [0] * 2000 +    # x0   20%
            [1] * 2200 +    # x0.5 22%
            [2] * 2000 +    # x1   20%
            [3] * 2000 +    # x2   20%
            [4] * 1200 +    # x5   12%
            [5] * 550 +     # x10  5.5%
            [6] * 50        # x100 0.5%
        )
        OUTCOMES = [
            ("🔥", {"ru": "Сгорело всё!", "en": "Lost it all!", "pt": "Perdeu tudo!", "es": "¡Todo perdido!", "tr": "Hepsini kaybettin!", "de": "Alles verloren!"}, 0.0),
            ("📉", {"ru": "Потерял половину", "en": "Lost half", "pt": "Perdeu metade", "es": "Perdiste la mitad", "tr": "Yarısını kaybettin", "de": "Hälfte verloren"}, 0.5),
            ("😐", {"ru": "Деньги при себе", "en": "Break even", "pt": "Empatou", "es": "Empate", "tr": "Başa baş", "de": "Break-even"}, 1.0),
            ("💰", {"ru": "Удвоил!", "en": "Doubled!", "pt": "Dobrou!", "es": "¡Duplicaste!", "tr": "İki katına çıktı!", "de": "Verdoppelt!"}, 2.0),
            ("🚀", {"ru": "Пятёрка!", "en": "Five times!", "pt": "Cinco vezes!", "es": "¡Cinco veces!", "tr": "Beş katına çıktı!", "de": "Fünffach!"}, 5.0),
            ("💫", {"ru": "ДЕСЯТКА!", "en": "TEN TIMES!", "pt": "DEZ VEZES!", "es": "¡DIEZ VECES!", "tr": "ON KATINA ÇIKTI!", "de": "ZEHNFACH!"}, 10.0),
            ("👑", {"ru": "🎊 ДЖЕКПОТ ×100!!! 🎊", "en": "🎊 JACKPOT ×100!!! 🎊", "pt": "🎊 JACKPOT ×100!!! 🎊", "es": "🎊 JACKPOT ×100!!! 🎊", "tr": "🎊 JACKPOT ×100!!! 🎊", "de": "🎊 JACKPOT ×100!!! 🎊"}, 100.0),
        ]
        VERDICTS_WIN = {"ru": "🤑 Повезло, красавчик!", "en": "🤑 Lucky you!", "pt": "🤑 Que sorte!", "es": "🤑 ¡Qué suerte!", "tr": "🤑 Şansın var!", "de": "🤑 Glückspilz!"}
        VERDICTS_LOSE = {"ru": "😤 Не повезло, попробуй ещё!", "en": "😤 No luck, try again!", "pt": "😤 Sem sorte, tente de novo!", "es": "😤 Sin suerte, ¡inténtalo de nuevo!", "tr": "😤 Şansın yok, tekrar dene!", "de": "😤 Pech gehabt, versuch's nochmal!"}
        VERDICTS_EVEN = {"ru": "😅 По нулям!", "en": "😅 Break even!", "pt": "😅 Empatou!", "es": "😅 ¡Empate!", "tr": "😅 Başa baş!", "de": "😅 Unentschieden!"}

        idx = random.choice(CASINO_POOL)
        icon, name_map, mult = OUTCOMES[idx]
        outcome_name = name_map.get(lang, name_map["en"])
        payout = int(bet * mult)
        delta = payout - bet
        db_add_coins(user.id, delta)
        total = db_get_coins(user.id)
        context.user_data["waiting_action"] = "casino_bet"  # stay in casino mode

        if mult > 1.0:
            verdict = VERDICTS_WIN.get(lang, VERDICTS_WIN["en"])
        elif mult == 1.0:
            verdict = VERDICTS_EVEN.get(lang, VERDICTS_EVEN["en"])
        else:
            verdict = VERDICTS_LOSE.get(lang, VERDICTS_LOSE["en"])

        kb_casino = [
            [InlineKeyboardButton(
                {"ru": "🎲 Сыграть ещё", "en": "🎲 Play again", "pt": "🎲 Jogar de novo", "es": "🎲 Jugar de nuevo", "tr": "🎲 Tekrar oyna", "de": "🎲 Nochmal spielen"}.get(lang, "🎲 Play again"),
                callback_data="game_casino"
            )],
            [InlineKeyboardButton(t("btn_back", lang), callback_data="games")],
        ]
        await msg.reply_text(
            t("casino_result", lang)
                .replace("{bet}", str(bet))
                .replace("{outcome_icon}", icon)
                .replace("{outcome_name}", outcome_name)
                .replace("{payout}", str(payout))
                .replace("{verdict}", verdict)
                .replace("{total}", str(total)),
            reply_markup=InlineKeyboardMarkup(kb_casino),
            parse_mode="HTML"
        )
        return

    # ── Broadcast ────────────────────────────────────────────────────────────────
    if action == "broadcast" and role in ("admin", "owner"):
        context.user_data.pop("waiting_action", None)
        users = db_all_users()
        sent, failed = 0, 0
        for uid, _, _ in users:
            try:
                u_lang = db_get_lang(uid)
                prefix = ("📢 Сообщение от администрации LUNA CLIENT:\n\n"
                          if u_lang == "ru" else
                          "📢 Message from LUNA CLIENT administration:\n\n")
                await context.bot.send_message(chat_id=uid, text=prefix + msg.text)
                sent += 1
            except Exception:
                failed += 1
        await msg.reply_text(f"📨 Рассылка завершена!\n\n✅ Доставлено: {sent}\n❌ Ошибок: {failed}")
        return

    # ── Give / take coins ────────────────────────────────────────────────────────
    if action in ("give_coins", "take_coins") and role in ("admin", "owner"):
        context.user_data.pop("waiting_action", None)
        parts = msg.text.strip().split()
        if len(parts) != 2:
            await msg.reply_text("❌ Неверный формат. Пример: <code>123456789 100</code>", parse_mode="HTML")
            return
        try:
            target_id = int(parts[0])
            amount = int(parts[1])
            if amount <= 0:
                raise ValueError
        except ValueError:
            await msg.reply_text("❌ Неверные данные. ID и количество должны быть числами больше 0.")
            return
        info = db_get_user(target_id)
        if not info:
            await msg.reply_text("❌ Пользователь не найден в базе.")
            return
        if action == "give_coins":
            db_add_coins(target_id, amount)
            new_bal = db_get_coins(target_id)
            await msg.reply_text(
                f"✅ Выдано <b>+{amount} 🪙</b> пользователю {info['name']} (ID: {target_id})\n"
                f"Новый баланс: <b>{new_bal} 🪙</b>",
                parse_mode="HTML"
            )
            try:
                t_lang = db_get_lang(target_id)
                await context.bot.send_message(
                    chat_id=target_id,
                    text=f"🎉 Администратор выдал вам <b>+{amount} 🪙</b> коинов!\nВаш баланс: <b>{new_bal} 🪙</b>" if t_lang == "ru"
                    else f"🎉 Admin gave you <b>+{amount} 🪙</b> coins!\nYour balance: <b>{new_bal} 🪙</b>",
                    parse_mode="HTML"
                )
            except Exception:
                pass
        else:
            db_add_coins(target_id, -amount)
            new_bal = db_get_coins(target_id)
            await msg.reply_text(
                f"✅ Снято <b>-{amount} 🪙</b> у пользователя {info['name']} (ID: {target_id})\n"
                f"Новый баланс: <b>{new_bal} 🪙</b>",
                parse_mode="HTML"
            )
        return

    # ── Create promo ─────────────────────────────────────────────────────────────
    if action == "create_promo" and role in ("admin", "owner"):
        context.user_data.pop("waiting_action", None)
        parts = msg.text.strip().split()
        if len(parts) != 3:
            await msg.reply_text(
                "❌ Неверный формат.\nПример: <code>LUNA100 100 10</code>",
                parse_mode="HTML"
            )
            return
        code_name = parts[0].upper()
        try:
            promo_coins = int(parts[1])
            max_uses = int(parts[2])
            if promo_coins <= 0 or max_uses <= 0:
                raise ValueError
        except ValueError:
            await msg.reply_text("❌ Коины и количество активаций должны быть положительными числами.")
            return
        success = db_create_promo(code_name, promo_coins, max_uses)
        if success:
            await msg.reply_text(
                f"✅ Промокод создан!\n\n"
                f"🎁 Код: <code>{code_name}</code>\n"
                f"💰 Коинов: <b>{promo_coins} 🪙</b>\n"
                f"👥 Активаций: <b>{max_uses}</b>",
                parse_mode="HTML"
            )
        else:
            await msg.reply_text(f"❌ Промокод <code>{code_name}</code> уже существует.", parse_mode="HTML")
        return

    # ── Admin management ──────────────────────────────────────────────────────────
    if action in ("add_admin", "remove_admin") and role == "owner":
        context.user_data.pop("waiting_action", None)
        try:
            target_id = int(msg.text.strip())
        except ValueError:
            await msg.reply_text("❌ Неверный формат. Введите числовой ID.")
            return
        if target_id == OWNER_ID:
            await msg.reply_text("❌ Нельзя изменить роль владельца.")
            return
        info = db_get_user(target_id)
        name = info["name"] if info else str(target_id)
        if action == "add_admin":
            db_add_admin(target_id)
            await msg.reply_text(f"✅ {name} (ID: {target_id}) получил права администратора.")
        else:
            db_remove_admin(target_id)
            await msg.reply_text(f"✅ У {name} (ID: {target_id}) забраны права администратора.")
        return

    # ── RPS challenge code ────────────────────────────────────────────────────────
    if msg.text and msg.text.strip().upper().startswith("RPS-") and len(msg.text.strip()) == 10:
        code = msg.text.strip().upper().replace("RPS-", "")
        ch = db_get_challenge(code)
        if not ch or ch["status"] != "pending":
            await msg.reply_text(t("ch_not_found", lang))
            return
        if ch["p1"] == user.id:
            await msg.reply_text(t("ch_own", lang))
            return
        p1_info = db_get_user(ch["p1"])
        p1_name = p1_info["name"] if p1_info else str(ch["p1"])
        kb = InlineKeyboardMarkup([[
            InlineKeyboardButton(t("ch_accept_btn", lang), callback_data=f"ch_accept_{code}"),
            InlineKeyboardButton(t("ch_decline_btn", lang), callback_data=f"ch_decline_{code}"),
        ]])
        await msg.reply_text(
            t("ch_invite", lang).replace("{name}", p1_name),
            reply_markup=kb
        )
        return

    # ── FAQ question ──────────────────────────────────────────────────────────────
    if context.user_data.get("waiting_question"):
        context.user_data.pop("waiting_question", None)
        formal_text = await rephrase_formal(msg.text)
        sent_msg = await context.bot.send_message(
            chat_id=OWNER_ID,
            text=(
                f"📩 Новый вопрос от пользователя\n\n"
                f"👤 Имя: {user.first_name}\n"
                f"🔗 Username: @{user.username}\n"
                f"🆔 ID: {user.id}\n"
                f"🌐 Язык: {LANGUAGES.get(lang, lang)}\n\n"
                f"❓ Вопрос (оригинал):\n{msg.text}\n\n"
                f"✏️ Вопрос (формально):\n{formal_text}\n\n"
                f"↩️ Ответьте на это сообщение, чтобы отправить ответ пользователю."
            )
        )
        db_add_fwd(sent_msg.message_id, user.id)
        kb = [[InlineKeyboardButton(t("btn_main_menu", lang), callback_data="back")]]
        await msg.reply_text(t("faq_sent", lang), reply_markup=InlineKeyboardMarkup(kb))


# ─── Group/Channel coin-give handler ──────────────────────────────────────────────

import re as _re

async def handle_group_coins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.reply_to_message:
        return
    sender = update.effective_user
    if not sender:
        return

    # Only admins/owner may use this
    if sender.id != OWNER_ID and not db_is_admin(sender.id):
        return

    text = (msg.text or "").strip()
    # Give: "дать 10" / "дать 10 коинов" / "give 10 coins"
    # Take: "забрать 10" / "забрать 10 коинов" / "take 10 coins"
    give_m = _re.match(r"^(?:дать|give)\s+(\d+)(?:\s+(?:коин(?:ов|а)?|coins?))?$", text, _re.IGNORECASE)
    take_m = _re.match(r"^(?:забрать|take)\s+(\d+)(?:\s+(?:коин(?:ов|а)?|coins?))?$", text, _re.IGNORECASE)

    if not give_m and not take_m:
        return

    amount = int((give_m or take_m).group(1))
    if amount <= 0 or amount > 1_000_000:
        return

    target_user = msg.reply_to_message.from_user
    if not target_user or target_user.is_bot:
        await msg.reply_text("❌ Нельзя выдать/забрать коины у бота.")
        return

    db_register(target_user)
    name = f"@{target_user.username}" if target_user.username else target_user.full_name
    admin_name = f"@{sender.username}" if sender.username else sender.full_name

    if give_m:
        db_add_coins(target_user.id, amount)
        total = db_get_coins(target_user.id)
        await msg.reply_text(
            f"✅ <b>{admin_name}</b> выдал <b>{amount} 🪙</b> → <b>{name}</b>\n"
            f"💰 Новый баланс: <b>{total} 🪙</b>",
            parse_mode="HTML"
        )
    else:
        current = db_get_coins(target_user.id)
        actual = min(amount, current)
        db_add_coins(target_user.id, -actual)
        total = db_get_coins(target_user.id)
        await msg.reply_text(
            f"🔻 <b>{admin_name}</b> забрал <b>{actual} 🪙</b> у <b>{name}</b>\n"
            f"💰 Новый баланс: <b>{total} 🪙</b>",
            parse_mode="HTML"
        )


# ─── Run ──────────────────────────────────────────────────────────────────────────

init_db()

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
    handle_message
))
app.add_handler(MessageHandler(
    filters.TEXT & ~filters.COMMAND & (filters.ChatType.GROUPS | filters.ChatType.SUPERGROUP | filters.ChatType.CHANNEL),
    handle_group_coins
))

print("LUNA CLIENT Bot running...")
app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
