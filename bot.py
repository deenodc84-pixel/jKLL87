import os
import random
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get token
TOKEN = os.getenv('BOT_TOKEN')
if not TOKEN:
    logger.error("No BOT_TOKEN found!")
    exit(1)

# Word Database
WORDS = [
    {"word": "Serendipity", "origin": "From 'The Three Princes of Serendip' (1754)", "meaning": "Happy accident discoveries", "example": "A serendipitous meeting changed his life"},
    {"word": "Etymology", "origin": "Greek 'etymon' (true sense) + 'logia' (study)", "meaning": "Study of word origins", "example": "She studied etymology at university"},
    {"word": "Nostalgia", "origin": "Greek 'nostos' (return) + 'algos' (pain)", "meaning": "Sentimental longing for past", "example": "Old photos filled him with nostalgia"},
    {"word": "Pandemonium", "origin": "Coined by Milton in 'Paradise Lost'", "meaning": "Wild chaos and confusion", "example": "The concert caused pandemonium"},
    {"word": "Quarantine", "origin": "Italian 'quaranta giorni' (40 days)", "meaning": "Isolation period", "example": "They were in quarantine for 14 days"},
    {"word": "Robot", "origin": "Czech 'robota' (forced labor)", "meaning": "Automated machine", "example": "Robots assemble cars in factories"},
    {"word": "Mentor", "origin": "Greek myth - Mentor was Odysseus' advisor", "meaning": "Trusted advisor", "example": "She mentored young entrepreneurs"},
    {"word": "Eureka", "origin": "Greek 'heurēka' (I found it)", "meaning": "Discovery exclamation", "example": "Eureka! The solution is here!"},
    {"word": "Juggernaut", "origin": "Sanskrit 'Jagannatha' (Lord of Universe)", "meaning": "Overwhelming force", "example": "The company became a juggernaut"},
    {"word": "Zombie", "origin": "West African 'nzambi' (god)", "meaning": "Undead creature", "example": "The zombie movie was terrifying"}
]

PUZZLES = [
    {"clue": "I come from a Czech word meaning 'forced labor'. What am I?", "answer": "robot"},
    {"clue": "I'm from a fairy tale about three princes. What am I?", "answer": "serendipity"},
    {"clue": "I was coined by Milton as Hell's capital. What am I?", "answer": "pandemonium"},
    {"clue": "I come from Greek for 'return home' and 'pain'. What am I?", "answer": "nostalgia"},
    {"clue": "I'm from Italian for 'forty days'. What am I?", "answer": "quarantine"}
]

user_data = {}

# Helper functions
def format_word(word):
    return f"📖 *{word['word']}*\n\n🔍 *Meaning:* {word['meaning']}\n📜 *Origin:* {word['origin']}\n💡 *Example:* _{word['example']}_"

def get_main_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Random Word", callback_data="word"), InlineKeyboardButton("🧩 Puzzle", callback_data="puzzle")],
        [InlineKeyboardButton("📅 Word of Day", callback_data="daily"), InlineKeyboardButton("⭐ Favorites", callback_data="favorites")],
        [InlineKeyboardButton("📊 Stats", callback_data="stats"), InlineKeyboardButton("❓ Help", callback_data="help")]
    ])

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = f"🔍 *Welcome Word Detective, {user.first_name}!*\n\nI help you discover fascinating word origins, solve puzzles & expand vocabulary!\n\n📚 Use the buttons below or /help for commands."
    
    await update.message.reply_text(msg, reply_markup=get_main_keyboard(), parse_mode='Markdown')
    logger.info(f"✅ User {user.id} started the bot")
    
    # Initialize user stats
    uid = user.id
    if uid not in user_data:
        user_data[uid] = {"words": 0, "puzzles": 0, "favorites": []}

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🤔 *Commands*\n\n/start - Start\n/help - This help\n/word - Random word\n/puzzle - Word puzzle\n/daily - Word of day\n/favorite - Save favorites\n/mystats - Your stats\n/about - About bot"
    await update.message.reply_text(msg, reply_markup=get_main_keyboard(), parse_mode='Markdown')

async def random_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = random.choice(WORDS)
    msg = format_word(word)
    
    # Update stats
    uid = update.effective_user.id
    if uid in user_data:
        user_data[uid]["words"] = user_data[uid].get("words", 0) + 1
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Another", callback_data="word"), InlineKeyboardButton("⭐ Save", callback_data=f"save_{word['word']}")],
        [InlineKeyboardButton("🧩 Puzzle", callback_data="puzzle"), InlineKeyboardButton("📅 Daily", callback_data="daily")]
    ])
    
    if update.message:
        await update.message.reply_text(msg, reply_markup=keyboard, parse_mode='Markdown')
    else:
        await update.callback_query.message.reply_text(msg, reply_markup=keyboard, parse_mode='Markdown')
        await update.callback_query.answer()

async def puzzle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    puzzle = random.choice(PUZZLES)
    context.user_data['answer'] = puzzle['answer']
    
    msg = f"🧩 *Word Mystery*\n\n🔍 {puzzle['clue']}\n\n🤔 Reply with your guess!"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💡 Reveal Answer", callback_data=f"reveal_{puzzle['answer']}")],
        [InlineKeyboardButton("🔄 New Puzzle", callback_data="puzzle")]
    ])
    
    if update.message:
        await update.message.reply_text(msg, reply_markup=keyboard, parse_mode='Markdown')
    else:
        await update.callback_query.message.reply_text(msg, reply_markup=keyboard, parse_mode='Markdown')
        await update.callback_query.answer()

async def daily_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    day = datetime.now().day
    word = WORDS[day % len(WORDS)]
    msg = f"📅 *Word of the Day*\n\n{format_word(word)}"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⭐ Save", callback_data=f"save_{word['word']}"), InlineKeyboardButton("📖 Another", callback_data="word")]
    ])
    
    if update.message:
        await update.message.reply_text(msg, reply_markup=keyboard, parse_mode='Markdown')
    else:
        await update.callback_query.message.reply_text(msg, reply_markup=keyboard, parse_mode='Markdown')
        await update.callback_query.answer()

async def favorite_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    
    if update.message and update.message.reply_to_message:
        # Save from reply
        text = update.message.reply_to_message.text
        for word in WORDS:
            if word['word'] in text:
                if uid in user_data:
                    if 'favorites' not in user_data[uid]:
                        user_data[uid]['favorites'] = []
                    if word not in user_data[uid]['favorites']:
                        user_data[uid]['favorites'].append(word)
                        await update.message.reply_text(f"⭐ *{word['word']}* saved!")
                    else:
                        await update.message.reply_text(f"📌 *{word['word']}* already saved!")
                return
        await update.message.reply_text("❌ Reply to a word message")
    else:
        # Show favorites
        if uid in user_data and user_data[uid].get('favorites'):
            msg = "⭐ *Your Favorites*\n\n"
            for i, w in enumerate(user_data[uid]['favorites'], 1):
                msg += f"{i}. *{w['word']}* - {w['meaning']}\n"
            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text("📭 No favorites yet! Reply to a word with /favorite")

async def mystats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in user_data:
        d = user_data[uid]
        msg = f"📊 *Your Stats*\n\n📖 Words learned: {d.get('words', 0)}\n🧩 Puzzles solved: {d.get('puzzles', 0)}\n⭐ Favorites: {len(d.get('favorites', []))}"
        await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text("📊 Start learning to track stats!")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "🤖 *Word Detective Bot*\n\nEducational bot for word origins, etymology & puzzles! 🕵️\n\nCreated for language lovers, students & curious minds."
    await update.message.reply_text(msg, parse_mode='Markdown')

# Button Handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    if data == "word":
        await random_word(update, context)
    elif data == "puzzle":
        await puzzle(update, context)
    elif data == "daily":
        await daily_word(update, context)
    elif data == "favorites":
        await favorite_word(update, context)
    elif data == "stats":
        await mystats(update, context)
    elif data == "help":
        await help_command(update, context)
    elif data.startswith("reveal_"):
        answer = data.replace("reveal_", "")
        await query.message.reply_text(f"✅ The answer is: *{answer.capitalize()}*!")
        
        uid = update.effective_user.id
        if uid in user_data:
            user_data[uid]["puzzles"] = user_data[uid].get("puzzles", 0) + 1
        
        await query.answer()
    elif data.startswith("save_"):
        word_name = data.replace("save_", "")
        uid = update.effective_user.id
        
        for word in WORDS:
            if word['word'].lower() == word_name.lower():
                if uid not in user_data:
                    user_data[uid] = {"words": 0, "puzzles": 0, "favorites": []}
                if 'favorites' not in user_data[uid]:
                    user_data[uid]['favorites'] = []
                if word not in user_data[uid]['favorites']:
                    user_data[uid]['favorites'].append(word)
                    await query.message.reply_text(f"⭐ *{word['word']}* saved!")
                else:
                    await query.message.reply_text(f"📌 *{word['word']}* already saved!")
                break
        await query.answer()

# Message Handler for puzzle answers
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if 'answer' in context.user_data:
        if update.message.text.lower() == context.user_data['answer']:
            await update.message.reply_text(f"🎉 *Correct!* It was '{context.user_data['answer'].capitalize()}'!")
            
            uid = update.effective_user.id
            if uid in user_data:
                user_data[uid]["puzzles"] = user_data[uid].get("puzzles", 0) + 1
            
            del context.user_data['answer']
        else:
            await update.message.reply_text("❌ Not quite! Try again or tap 'Reveal Answer'.")

# Main function
def main():
    try:
        # Clear any webhook first
        import requests
        requests.get(f"https://api.telegram.org/bot{TOKEN}/deleteWebhook?drop_pending_updates=true")
        
        # Create app
        app = Application.builder().token(TOKEN).build()
        
        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("word", random_word))
        app.add_handler(CommandHandler("puzzle", puzzle))
        app.add_handler(CommandHandler("daily", daily_word))
        app.add_handler(CommandHandler("favorite", favorite_word))
        app.add_handler(CommandHandler("mystats", mystats))
        app.add_handler(CommandHandler("about", about_command))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("🚀 Word Detective Bot is starting...")
        print(f"🤖 Bot username: @jKLL87BOT")
        print("✅ Bot is ready!")
        
        # Start polling
        app.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
