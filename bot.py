import os
import random
import json
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token from environment
TOKEN = os.getenv('BOT_TOKEN')

# Word database with etymology facts
WORD_DATABASE = [
    {
        "word": "Serendipity",
        "origin": "Coined by Horace Walpole in 1754 from 'The Three Princes of Serendip', a fairy tale where heroes made happy discoveries by accident.",
        "meaning": "The occurrence of events by chance in a happy or beneficial way.",
        "example": "A serendipitous encounter led to their successful business partnership."
    },
    {
        "word": "Etymology",
        "origin": "From Greek 'etymon' (true sense) and 'logia' (study). First used in the 14th century.",
        "meaning": "The study of the origin and history of words.",
        "example": "She was fascinated by the etymology of common English words."
    },
    {
        "word": "Nostalgia",
        "origin": "From Greek 'nostos' (return home) and 'algos' (pain). Originally meant 'homesickness' and was considered a medical condition!",
        "meaning": "A sentimental longing for the past.",
        "example": "Listening to old songs filled him with nostalgia."
    },
    {
        "word": "Pandemonium",
        "origin": "Coined by John Milton in 'Paradise Lost' as the capital of Hell, from Greek 'pan' (all) and 'daimon' (demon).",
        "meaning": "Wild and noisy disorder or confusion.",
        "example": "The announcement caused pandemonium in the hall."
    },
    {
        "word": "Quarantine",
        "origin": "From Italian 'quaranta giorni' (forty days), referring to the 40-day isolation period for ships during the Black Death.",
        "meaning": "A period of isolation to prevent disease spread.",
        "example": "The travelers were placed in quarantine upon arrival."
    },
    {
        "word": "Robot",
        "origin": "From Czech 'robota' meaning 'forced labor' or 'drudgery'. First used in Karel Čapek's play 'R.U.R.' in 1920.",
        "meaning": "A machine capable of carrying out complex actions automatically.",
        "example": "The factory uses robots for assembly."
    },
    {
        "word": "Zombie",
        "origin": "From West African 'nzambi' (god) or 'zumbi' (fetish). Brought to English through Haitian folklore.",
        "meaning": "A mythical undead creature, or someone behaving mechanically.",
        "example": "The zombie movie terrified the audience."
    },
    {
        "word": "Mentor",
        "origin": "From Greek mythology, Mentor was the wise advisor of Telemachus in Homer's Odyssey.",
        "meaning": "An experienced and trusted advisor.",
        "example": "She became a mentor to young entrepreneurs."
    },
    {
        "word": "Eureka",
        "origin": "From Greek 'heurēka' meaning 'I have found it'. Supposedly exclaimed by Archimedes when he discovered displacement.",
        "meaning": "Used to express sudden discovery or triumph.",
        "example": "Eureka! I finally solved the problem!"
    },
    {
        "word": "Juggernaut",
        "origin": "From Sanskrit 'Jagannatha' meaning 'Lord of the Universe', a title of the Hindu god Krishna.",
        "meaning": "A huge, powerful, and overwhelming force or institution.",
        "example": "The company became a juggernaut in the tech industry."
    }
]

# Puzzle database
PUZZLE_DATABASE = [
    {
        "clue": "I come from a Czech word meaning 'forced labor'. What word am I?",
        "answer": "robot",
        "hint": "Think of a machine that works automatically"
    },
    {
        "clue": "My origin is from a fairy tale about three princes who made happy discoveries. What word am I?",
        "answer": "serendipity",
        "hint": "It's about finding something good unexpectedly"
    },
    {
        "clue": "I was coined by John Milton in 'Paradise Lost' as the capital of Hell. What word am I?",
        "answer": "pandemonium",
        "hint": "Think of chaos and confusion"
    },
    {
        "clue": "I come from the Greek words for 'return home' and 'pain'. What word am I?",
        "answer": "nostalgia",
        "hint": "You feel this when remembering the past"
    },
    {
        "clue": "My origin is from Italian meaning 'forty days' during the Black Death. What word am I?",
        "answer": "quarantine",
        "hint": "Used during the pandemic"
    }
]

# User statistics storage (simple in-memory for demo)
user_stats = {}

# Helper functions
def get_word_of_day():
    """Get the word of the day based on date"""
    day = datetime.now().day
    return WORD_DATABASE[day % len(WORD_DATABASE)]

def format_word_info(word_data):
    """Format word information for display"""
    return f"📖 *{word_data['word']}*\n\n" \
           f"🔍 *Meaning:* {word_data['meaning']}\n\n" \
           f"📜 *Origin:* {word_data['origin']}\n\n" \
           f"💡 *Example:* _{word_data['example']}_"

def get_favorites_key(user_id):
    return f"favorites_{user_id}"

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    welcome_text = f"🔍 *Welcome to Word Detective, {user.first_name}!*\n\n" \
                   "I'm your personal word detective! I'll help you discover the fascinating origins of words, " \
                   "solve word puzzles, and expand your vocabulary.\n\n" \
                   "📚 *What can you do?*\n" \
                   "• Get a random word with its origin story\n" \
                   "• Solve word mysteries and puzzles\n" \
                   "• Get the word of the day\n" \
                   "• Save your favorite words\n" \
                   "• Track your learning progress\n\n" \
                   "Use /help to see all commands, or simply tap a button below to begin!"

    keyboard = [
        [
            InlineKeyboardButton("📖 Random Word", callback_data="random_word"),
            InlineKeyboardButton("🧩 Puzzle", callback_data="puzzle")
        ],
        [
            InlineKeyboardButton("📅 Word of Day", callback_data="daily_word"),
            InlineKeyboardButton("⭐ Favorites", callback_data="show_favorites")
        ],
        [
            InlineKeyboardButton("📊 My Stats", callback_data="show_stats"),
            InlineKeyboardButton("❓ Help", callback_data="show_help")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

    # Initialize user stats
    user_id = update.effective_user.id
    if user_id not in user_stats:
        user_stats[user_id] = {
            "words_learned": 0,
            "puzzles_solved": 0,
            "last_active": datetime.now().isoformat()
        }

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    help_text = "🤔 *How to use Word Detective Bot*\n\n" \
                "📌 *Available Commands:*\n" \
                "/start - Start your word detective journey\n" \
                "/help - Show this help message\n" \
                "/word - Get a random word with origin story\n" \
                "/puzzle - Solve a word mystery puzzle\n" \
                "/daily - Get today's word of the day\n" \
                "/favorite - Save a word to favorites (reply to a word)\n" \
                "/mystats - View your learning statistics\n" \
                "/about - Learn more about this bot\n\n" \
                "🎯 *Quick Tips:*\n" \
                "• Use the buttons below messages for quick actions\n" \
                "• Reply to a word with /favorite to save it\n" \
                "• Your stats track your learning progress!\n\n" \
                "Have fun becoming a word detective! 🕵️"

    keyboard = [
        [
            InlineKeyboardButton("📖 Get Word", callback_data="random_word"),
            InlineKeyboardButton("🧩 Solve Puzzle", callback_data="puzzle")
        ],
        [
            InlineKeyboardButton("📅 Daily Word", callback_data="daily_word"),
            InlineKeyboardButton("📊 My Stats", callback_data="show_stats")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

async def random_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a random word with its origin."""
    word_data = random.choice(WORD_DATABASE)
    message = format_word_info(word_data)
    
    keyboard = [
        [
            InlineKeyboardButton("📖 Another Word", callback_data="random_word"),
            InlineKeyboardButton("⭐ Save Word", callback_data=f"save_{word_data['word']}")
        ],
        [
            InlineKeyboardButton("📅 Daily Word", callback_data="daily_word"),
            InlineKeyboardButton("🧩 Puzzle", callback_data="puzzle")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Update stats
    user_id = update.effective_user.id
    if user_id in user_stats:
        user_stats[user_id]["words_learned"] += 1
        user_stats[user_id]["last_active"] = datetime.now().isoformat()

    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        await update.callback_query.answer()

async def puzzle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a word puzzle."""
    puzzle_data = random.choice(PUZZLE_DATABASE)
    puzzle_text = f"🧩 *Word Mystery Puzzle*\n\n" \
                  f"🔍 *Clue:* {puzzle_data['clue']}\n\n" \
                  f"💡 *Hint:* {puzzle_data['hint']}\n\n" \
                  f"🤔 Can you guess the word? Reply with your answer!"

    # Store the answer in context for checking
    context.user_data['current_puzzle'] = puzzle_data['answer'].lower()

    keyboard = [
        [
            InlineKeyboardButton("💡 Give Me Answer", callback_data=f"puzzle_answer_{puzzle_data['answer']}"),
            InlineKeyboardButton("🔄 New Puzzle", callback_data="puzzle")
        ],
        [
            InlineKeyboardButton("📖 Random Word", callback_data="random_word")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(puzzle_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.message.reply_text(puzzle_text, reply_markup=reply_markup, parse_mode='Markdown')
        await update.callback_query.answer()

async def daily_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the word of the day."""
    word_data = get_word_of_day()
    message = f"📅 *Word of the Day*\n\n{format_word_info(word_data)}"

    keyboard = [
        [
            InlineKeyboardButton("📖 Random Word", callback_data="random_word"),
            InlineKeyboardButton("⭐ Save Word", callback_data=f"save_{word_data['word']}")
        ],
        [
            InlineKeyboardButton("🧩 Puzzle", callback_data="puzzle"),
            InlineKeyboardButton("📊 Stats", callback_data="show_stats")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        await update.callback_query.answer()

async def favorite_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save a word to favorites."""
    user_id = update.effective_user.id
    
    # Check if replying to a message
    if update.message.reply_to_message:
        # Try to extract word from replied message
        replied_text = update.message.reply_to_message.text
        # Simple extraction - find word between **
        import re
        match = re.search(r'\*\*(.*?)\*\*', replied_text)
        if match:
            word = match.group(1).strip()
            # Find word in database
            found = False
            for w in WORD_DATABASE:
                if w['word'].lower() == word.lower():
                    # Initialize favorites list for user
                    if 'favorites' not in context.user_data:
                        context.user_data['favorites'] = []
                    if w not in context.user_data['favorites']:
                        context.user_data['favorites'].append(w)
                        await update.message.reply_text(f"⭐ *{w['word']}* has been saved to your favorites!")
                        return
                    else:
                        await update.message.reply_text(f"📌 *{w['word']}* is already in your favorites!")
                        return
            await update.message.reply_text("❌ Couldn't find that word in the database. Try with a word I've shown you!")
        else:
            await update.message.reply_text("❌ Please reply to a word message with /favorite")
    else:
        # Show favorites list
        if 'favorites' in context.user_data and context.user_data['favorites']:
            fav_list = "⭐ *Your Favorite Words*\n\n"
            for idx, word in enumerate(context.user_data['favorites'], 1):
                fav_list += f"{idx}. *{word['word']}* - {word['meaning'][:50]}...\n"
            await update.message.reply_text(fav_list, parse_mode='Markdown')
        else:
            await update.message.reply_text("📭 You don't have any favorite words yet. Reply to a word message with /favorite to save it!")

async def mystats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics."""
    user_id = update.effective_user.id
    
    if user_id in user_stats:
        stats = user_stats[user_id]
        stats_text = f"📊 *Your Learning Statistics*\n\n" \
                     f"📖 Words learned: {stats['words_learned']}\n" \
                     f"🧩 Puzzles solved: {stats['puzzles_solved']}\n" \
                     f"⭐ Favorites: {len(context.user_data.get('favorites', []))}\n" \
                     f"📅 Last active: {stats['last_active'][:10]}\n\n" \
                     f"Keep up the great work, word detective! 🕵️"

        keyboard = [
            [
                InlineKeyboardButton("📖 Learn More Words", callback_data="random_word"),
                InlineKeyboardButton("🧩 Solve Puzzles", callback_data="puzzle")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if update.message:
            await update.message.reply_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            await update.callback_query.message.reply_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text("📊 Start using the bot to track your statistics!")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send about information."""
    about_text = "🤖 *About Word Detective Bot*\n\n" \
                 "Word Detective Bot is an educational tool designed to help you discover the fascinating origins of words, " \
                 "expand your vocabulary, and have fun with word puzzles!\n\n" \
                 "🔍 *Features:*\n" \
                 "• Daily word with etymology\n" \
                 "• Word puzzles and mysteries\n" \
                 "• Save favorite words\n" \
                 "• Track learning progress\n\n" \
                 "📚 *Perfect for:*\n" \
                 "• Students\n" \
                 "• Language enthusiasts\n" \
                 "• Writers\n" \
                 "• Curious minds\n\n" \
                 "Start your word detective journey today! 🕵️"

    await update.message.reply_text(about_text, parse_mode='Markdown')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    data = query.data

    if data == "random_word":
        await random_word(update, context)
    elif data == "puzzle":
        await puzzle(update, context)
    elif data == "daily_word":
        await daily_word(update, context)
    elif data == "show_favorites":
        await favorite_word(update, context)
    elif data == "show_stats":
        await mystats(update, context)
    elif data == "show_help":
        await help_command(update, context)
    elif data.startswith("puzzle_answer_"):
        answer = data.replace("puzzle_answer_", "")
        await query.message.reply_text(f"✅ The answer is: *{answer.capitalize()}*!\n\nDid you get it right? Keep practicing! 🎯", parse_mode='Markdown')
        # Update stats
        user_id = update.effective_user.id
        if user_id in user_stats:
            user_stats[user_id]["puzzles_solved"] += 1
        await query.answer()
    elif data.startswith("save_"):
        word_name = data.replace("save_", "")
        for word in WORD_DATABASE:
            if word['word'].lower() == word_name.lower():
                if 'favorites' not in context.user_data:
                    context.user_data['favorites'] = []
                if word not in context.user_data['favorites']:
                    context.user_data['favorites'].append(word)
                    await query.message.reply_text(f"⭐ *{word['word']}* saved to favorites!")
                else:
                    await query.message.reply_text(f"📌 *{word['word']}* is already in favorites!")
                break
        await query.answer()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages for puzzle answers."""
    user_answer = update.message.text.lower()
    
    # Check if there's an active puzzle
    if 'current_puzzle' in context.user_data:
        correct_answer = context.user_data['current_puzzle']
        if user_answer == correct_answer:
            await update.message.reply_text(f"🎉 *Correct!* The answer was '{correct_answer.capitalize()}'!\n\nYou're a true word detective! 🕵️")
            # Update stats
            user_id = update.effective_user.id
            if user_id in user_stats:
                user_stats[user_id]["puzzles_solved"] += 1
            # Clear puzzle
            del context.user_data['current_puzzle']
        elif len(user_answer) > 3:  # Avoid very short responses
            await update.message.reply_text(f"❌ Not quite right! Try again or use '💡 Give Me Answer' button.")

def main():
    """Start the bot."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("word", random_word))
    application.add_handler(CommandHandler("puzzle", puzzle))
    application.add_handler(CommandHandler("daily", daily_word))
    application.add_handler(CommandHandler("favorite", favorite_word))
    application.add_handler(CommandHandler("mystats", mystats))
    application.add_handler(CommandHandler("about", about_command))

    # Add callback handler for buttons
    application.add_handler(CallbackQueryHandler(button_handler))

    # Add message handler for puzzle answers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    print("🤖 Word Detective Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
