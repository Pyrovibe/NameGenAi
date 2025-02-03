import telebot
import threading
import subprocess
import os
import time
import asyncio
from collections import defaultdict
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from openai import AsyncOpenAI
import base58
import random
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()  # Load environment variables from .env file

# --- Configuration (Placeholders) ---
# !! IMPORTANT !! Replace these with your actual values in the .env file
BOT_TOKEN = os.environ.get("BOT_TOKEN", "your_telegram_bot_token")  # Placeholder
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "your_openai_api_key")  # Placeholder
SOLANA_KEYGEN_PATH = os.environ.get("SOLANA_KEYGEN_PATH", "/path/to/solana-keygen")  # Placeholder

# --- Bot Settings (Customizable) ---
BOT_NAME = os.environ.get("BOT_NAME", "NameGenAI")  # Allow customizing the bot's name
BRAND_EMOJI = os.environ.get("BRAND_EMOJI", "⚡")  # Allow customizing the brand emoji
TWITTER_LINK = os.environ.get("TWITTER_LINK", "https://x.com/your_twitter_handle") # Placeholder for Twitter link
ESTIMATED_ADDRESSES_PER_SECOND = 100000  # You can make this configurable if needed

# --- Derived Constants ---
BRAND_HEADER = f"{BRAND_EMOJI} {BOT_NAME}"
BRAND_FOOTER = "\n\nPowered by the Official Solana CLI 🚀"  # You might make the footer customizable too

# --- Initialize Bot and OpenAI Client ---
bot = telebot.TeleBot(BOT_TOKEN)
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# --- User Data (Keep as is) ---
user_data = defaultdict(lambda: {
    "search_status": None,
    "current_mode": None,
    "generating_wallet": False,
    "last_update_time": None,
    "process": None,
    "start_time": None,
    "found_count": 0,
    "wallet_info": None,
    "update_message_id": None,
    "ignore_case": False,
})

# --- AI Helper Class ---
class AIHelper:
    def __init__(self):
        self.system_prompt = """You are an expert assistant for a generic Solana wallet generator bot. Provide clear, accurate, and user-friendly guidance.

**Key Information:**

*   **Wallet Generation:**
    *   Secure, local generation using the Official Solana CLI.
    *   Users can specify patterns for the start or end of the address.
    *   Patterns use Base58 characters (1-9, A-Z, a-z, excluding 0, I, O, l).
    *   Users can generate patterns up to 8 characters.
    *   Users can toggle case-sensitivity.
    *   Generation time varies based on pattern length and complexity.
*   **Solana:**
    *   Solana is a high-performance blockchain.
    *   Wallet addresses are derived from public keys.
    *   Private keys must be kept secret and secure.
*   **Base58:**
    *   Base58 is an encoding scheme used to represent data in a more compact and human-readable format than raw binary.
    *   Valid Base58 characters for Solana addresses: `123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz`
*   **Security:**
    *   Emphasize the importance of keeping private keys and mnemonic phrases safe.
    *   Warn users never to share their private keys or mnemonics.

**Example Interactions (Generic):**

*   **User:** How do I generate a wallet that starts with "ABC"?
    *   **AI:** To generate a wallet that starts with "ABC", select "Generate Wallet" and then "Starts With." Enter "ABC" as your desired pattern and start the generation process.
*   **User:** What are some pattern ideas?
    *   **AI:** Here are some pattern ideas:
        *   (Provide a few generic examples, potentially based on themes like animals, colors, technology, etc.)

**Remember**: Be concise, helpful, and always prioritize security in your responses.
        """

    async def get_pattern_suggestion(self, prompt):
        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert at generating cool and memorable patterns for Solana wallet addresses using Base58 characters. Generate 5-10 patterns between 1 and 5 characters long. Prioritize patterns that are 1-2 character long. Do not have any intro text, just give the pattern separated by commas." },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=200
            )
            suggestions_str = response.choices[0].message.content.strip()
            suggestions = [s.strip() for s in suggestions_str.split(",") if s.strip()]
            num_suggestions = min(len(suggestions), 5)  # Limit to 5 suggestions
            chosen_suggestions = random.sample(suggestions, num_suggestions)
            return ", ".join(chosen_suggestions)
        except Exception as e:
            print(f"AI Error: {e}")
            return "Error generating suggestions." # Provide a generic error message

    async def get_help_response(self, user_message):
        try:
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=250
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI Error: {e}")
            return "I'm currently unavailable. Please try again later."

# --- Instantiate AI Helper ---
ai_helper = AIHelper()

# --- Helper Functions ---
async def process_ai_request(message):
    query = message.text.replace('/ask', '').strip()
    if not query:
        return "Please add your question after /ask"
    return await ai_helper.get_help_response(query)

def escape_markdown_v2(text):
    escape_chars = r"\_*[]()~>#+-=|{}.!"
    return "".join(f"\\{char}" if char in escape_chars else char for char in text)

def create_main_menu_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(f"{BRAND_EMOJI} Generate Wallet", callback_data="generate_wallet"))
    markup.add(InlineKeyboardButton("🤖 AI Assistant", callback_data="ai_help"))
    markup.add(InlineKeyboardButton("📚 Help", callback_data="help_menu"))
    if TWITTER_LINK:  # Only add Twitter button if the link is provided
        markup.add(InlineKeyboardButton("🐦 Twitter", url=TWITTER_LINK))
    markup.add(InlineKeyboardButton("🔄 Reset Bot", callback_data="reset_bot"))
    return markup

def create_help_menu_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📝 Pattern Rules", callback_data="help_pattern"))
    markup.add(InlineKeyboardButton("🤖 AI Help", callback_data="help_ai"))
    markup.add(InlineKeyboardButton("🔐 Security", callback_data="help_security"))
    markup.add(InlineKeyboardButton("ℹ️ About This Bot", callback_data="help_about")) # Generic "About"
    markup.add(InlineKeyboardButton("📋 How to Use", callback_data="help_how"))
    markup.add(InlineKeyboardButton("↩️ Back to Main Menu", callback_data="main_menu"))
    return markup

def create_generate_wallet_menu():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🎯 Starts With", callback_data="generate_starts_with"))
    markup.add(InlineKeyboardButton("🎯 Ends With", callback_data="generate_ends_with"))
    markup.add(InlineKeyboardButton("🎯 Starts & Ends With", callback_data="generate_starts_and_ends_with"))
    markup.add(InlineKeyboardButton("🤖 AI Suggestion", callback_data="generate_ai_pattern"))
    markup.add(InlineKeyboardButton("🔀 Ignore Case", callback_data="toggle_ignore_case"))
    markup.add(InlineKeyboardButton("↩️ Back to Main Menu", callback_data="main_menu"))
    return markup

# ... (rest of your functions: create_thread_count_menu, calculate_estimated_time, format_time_estimate, reset_user_state)

# --- Bot Command Handlers ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        f"{BRAND_HEADER}\n\n"
        "Welcome to this Solana vanity wallet generator! ✨\n\n" # Made more generic
        "Create unique, personalized Solana wallet addresses.\n\n"  # Made more generic
        "Select an option below to begin:"
        f"{BRAND_FOOTER}"
    )
    bot.reply_to(message, escape_markdown_v2(welcome_text), reply_markup=create_main_menu_markup(), parse_mode="MarkdownV2")

def run_async_in_thread(async_func, *args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_func(*args))
    loop.close()
    return result

@bot.message_handler(commands=['ask'])
def handle_ai_question(message):
    chat_id = message.chat.id
    response = run_async_in_thread(process_ai_request, message)
    bot.send_message(chat_id, response)
    bot.send_message(chat_id, "What would you like to do next?", reply_markup=create_main_menu_markup())

@bot.callback_query_handler(func=lambda call: call.data == "generate_ai_pattern")
def generate_ai_pattern(call):
    chat_id = call.message.chat.id
    try:
        # Make the AI prompt more generic
        prompt = "Suggest cool 1-5 character patterns (prioritize 1-2 characters) for a Solana wallet. Use Base58 characters."
        patterns = run_async_in_thread(ai_helper.get_pattern_suggestion, prompt)
        bot.send_message(
            chat_id,
            f"Here are some pattern suggestions:\n\n**{patterns}**\n\nWhat would you like to do next?",  # Removed the bot's name
            reply_markup=create_generate_wallet_menu(),
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        print(f"Error: {e}")
        bot.answer_callback_query(call.id, "Error generating pattern. Please try again.")

# --- Wallet Generation Function ---
def start_wallet_generation(chat_id, pattern, mode, message):
    print(f"Starting wallet generation for user {chat_id} with pattern '{pattern}' in mode '{mode}'")

    user = user_data[chat_id]
    user["generating_wallet"] = True
    user["start_time"] = time.time()
    user["last_update_time"] = time.time()
    user["found_count"] = 0

    try:
        if not os.path.exists(SOLANA_KEYGEN_PATH):
            raise FileNotFoundError(f"solana-keygen not found at {SOLANA_KEYGEN_PATH}")
        subprocess.run([SOLANA_KEYGEN_PATH, "--version"], capture_output=True, check=True, text=True)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"Error checking for solana-keygen: {e}")
        user["generating_wallet"] = False
        bot.send_message(
            chat_id,
            escape_markdown_v2(f"{BRAND_HEADER}\n\nSystem Error: Solana CLI tools not detected or incorrect path set. Please check the configuration.{BRAND_FOOTER}"),  # More specific error
            reply_markup=create_main_menu_markup(),
            parse_mode="MarkdownV2"
        )
        return

    ignore_case = user.get("ignore_case", False)

    command = [SOLANA_KEYGEN_PATH, "grind"]
    if ignore_case:
        command.append("--ignore-case")
    if mode == "starts_with":
        command.extend([f"--starts-with", f"{pattern}:1"])
    elif mode == "ends_with":
        command.extend([f"--ends-with", f"{pattern}:1"])
    elif mode == "starts_and_ends_with":
        prefix, suffix = pattern.split(",")
        prefix = prefix.strip()
        suffix = suffix.strip()
        command.extend([f"--starts-and-ends-with", f"{prefix}:{suffix}:1"])

    print(f"DEBUG: command={command}")

    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        user["process"] = process

    except Exception as e:
        user["generating_wallet"] = False
        bot.send_message(
            chat_id,
            escape_markdown_v2(f"{BRAND_HEADER}\n\nGeneration failed. Please try again.{BRAND_FOOTER}"),
            reply_markup=create_main_menu_markup()
        )
        print(f"Wallet generation failed for user {chat_id}: {str(e)}")
        return

    progress_bar = "░" * 10
    initial_message = bot.send_message(
        chat_id,
        escape_markdown_v2(f"{BRAND_HEADER}\n\n"
            f"🔍 Generation in Progress... [{progress_bar}]\n\n"
            f"{BRAND_FOOTER}"),
        parse_mode="MarkdownV2"
    )
    user["update_message_id"] = initial_message.message_id

    stop_markup = ReplyKeyboardMarkup(resize_keyboard=True)
    stop_markup.add(KeyboardButton('🛑 Stop Generation'))
    bot.send_message(chat_id, "Use the button below to stop the generation.", reply_markup=stop_markup)

    def monitor_generation():
        chat_id = message.chat.id
        user = user_data[chat_id]
        process = user["process"]
        last_update_time = time.time()
        update_message_id = user["update_message_id"]

        while user["generating_wallet"]:
            if process.poll() is not None:
                stdout, stderr = process.communicate()

                if stderr:
                    print(f"Wallet generation error for user {chat_id}: {stderr}")
                    bot.send_message(
                        chat_id,
                        escape_markdown_v2(f"{BRAND_HEADER}\n\nAn error occurred during generation. Please try again.\n\nError: {stderr}{BRAND_FOOTER}"),
                        reply_markup=create_main_menu_markup()
                    )
                    user["generating_wallet"] = False
                    return

                if "Wrote keypair to" in stdout:
                    user["generating_wallet"] = False
                    success_message = escape_markdown_v2(
                        f"{BRAND_HEADER}\n\n"
                        "**Wallet Generated Successfully!**\n\n"  # Made more generic
                        "The wallet address has been successfully generated.\n"  # Made more generic
                        "**Remember to keep your key file safe and secure!**\n"  # Emphasize security
                        f"{BRAND_FOOTER}"
                    )

                    try:
                        bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=user["update_message_id"],
                            text=success_message,
                            reply_markup=create_main_menu_markup(),
                            parse_mode="MarkdownV2"
                        )
                    except Exception as e:
                        print(f"Error updating message with success: {e}")
                    bot.send_message(chat_id, "Generation complete.", reply_markup=ReplyKeyboardRemove())
                    return
                else:
                    bot.send_message(
                        chat_id,
                        escape_markdown_v2(f"{BRAND_HEADER}\n\nAn error occurred during generation. No keypair file was created. Please try again.{BRAND_FOOTER}"),
                        reply_markup=create_main_menu_markup()
                    )
                    user["generating_wallet"] = False
                    return

            current_time = time.time()
            if current_time - last_update_time >= 10:
                progress_segment = int((current_time - user["start_time"]) % 150 / 15)
                progress_bar = "▓" * progress_segment + "░" * (10 - progress_segment)

                update_message = escape_markdown_v2(
                    f"{BRAND_HEADER}\n\n"
                    f"🔍 Generation in Progress... [{progress_bar}]\n\n"
                    f"{BRAND_FOOTER}"
                )

                try:
                    bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=update_message_id,
                        text=update_message,
                        parse_mode="MarkdownV2"
                    )
                    last_update_time = current_time
                except Exception as e:
                    print(f"Error updating progress message: {e}")

            time.sleep(1)

    monitor_generation()

# ... (rest of your command handlers: handle_stop_command, generate_wallet_menu_callback, ai_help_callback)

def escape_markdown_v2_selectively(text):
    escape_chars_map = {
        "_": r"\_", "*": r"\*", "[": r"\[", "]": r"\]", "(": r"\(",
        ")": r"\)", "~": r"\~", "`": r"\`", ">": r"\>", "#": r"\#",
        "+": r"\+", "-": r"\-", "=": r"\=", "|": r"\|", "{": r"\{",
        "}": r"\}", ".": r"\.", "!": r"\!"
    }
    escaped_text = ""
    inside_code_block = False
    for char in text:
        if char == '`':
            inside_code_block = not inside_code_block
        if not inside_code_block and char in escape_chars_map:
            escaped_text += escape_chars_map[char]
        else:
            escaped_text += char
    return escaped_text

# --- Help Menu Handlers ---
@bot.callback_query_handler(func=lambda call: call.data.startswith("help_"))
def handle_help_callback(call):
    chat_id = call.message.chat.id
    section = call.data.split("_")[1]

    # Make help sections more generic
    help_sections = {
        "pattern": (
            f"{BRAND_HEADER}\n\n"
            "**Wallet Generation Guidelines**\n\n"
            "This bot generates secure Solana wallet addresses using Base58 encoding.\n\n"  # Generic
            "**Valid Characters**\n"
            "• Digits: 1-9\n"
            "• Letters: A-Z, a-z (excluding I, O, l)\n\n"
            "**Pattern Specifications**\n"
            "• Pattern Length: 1-8 characters\n"
            "• Full Address: 44 characters\n"
            "• Encoding: Base58\n"
            "• Case-sensitive (unless 'Ignore Case' is enabled)\n"
        ),
        "security": (
            f"{BRAND_HEADER}\n\n"
            "**Security and Privacy**\n\n"
            "• Keys are generated locally using the Solana CLI.\n"  # Mention Solana CLI
            "• No private key data is stored by this bot.\n"  # Emphasize security
            "• The bot uses secure methods to handle temporary data.\n\n" # Generic statement
            "**User Responsibilities**\n"
            "• Save your generated key files securely.\n"  # User responsibility
            "• **Never share your private keys or mnemonics with anyone.**\n"  # Strong warning
        ),
        "about": (
            f"{BRAND_HEADER}\n\n"
            f"**About {BOT_NAME}**\n\n"  # Use the bot's configured name
            "This bot helps you create custom Solana wallet addresses.\n"  # Generic
            "• It uses the official Solana CLI for secure key generation.\n"  # Mention Solana CLI
            "• It provides an AI assistant to help with pattern ideas.\n"  # Mention AI
        ),
        "how": (
            f"{BRAND_HEADER}\n\n"
            "**Quick Start Guide**\n\n"
            "1. Select 'Generate Wallet'.\n"
            "2. Choose how you want to customize your address (start/end/both).\n"
            "3. Enter your desired pattern.\n"
            "4. Toggle 'Ignore Case' if you don't want case sensitivity.\n"
            "5. Wait for the generation process to complete.\n"
            "6. **Securely save the generated wallet information.**\n"  # Emphasize security
        ),
        "ai": (
            f"{BRAND_HEADER}\n\n"
            "**AI Assistant Features**\n\n"
            "• Use /ask followed by your question to get help.\n"
            "• The AI can suggest patterns for your wallet address.\n"
            "• Ask the AI about Solana addresses or security.\n"
            f"{BRAND_FOOTER}"
        ),
    }

    if section == "menu":
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=f"{BRAND_HEADER}\n\n**Help Menu**\n\nSelect a topic below:",
            reply_markup=create_help_menu_markup(),
            parse_mode="MarkdownV2"
        )
    elif section in help_sections:
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=escape_markdown_v2_selectively(help_sections[section]),
            reply_markup=create_help_menu_markup(),
            parse_mode="MarkdownV2"
        )
    else:
        bot.answer_callback_query(call.id, text="Invalid help option.")

# ... (rest of your callback handlers: help_menu, request_pattern_starts_with, request_pattern_ends_with, request_pattern_starts_and_ends_with, return_to_main_menu, reset_bot_handler, toggle_ignore_case)

# --- Pattern Input Handler ---
@bot.message_handler(func=lambda message: True)
def handle_pattern_input(message):
    chat_id = message.chat.id
    user = user_data[chat_id]

    if user["generating_wallet"]:
        if message.text and (message.text == '🛑 Stop Generation' or message.text.startswith('/stop')):
            handle_stop_command(message)
        else:
            bot.reply_to(
                message,
                escape_markdown_v2(f"{BRAND_HEADER}\n\nWallet generation is in progress. Please wait or use the Stop Generation button.{BRAND_FOOTER}"),
                parse_mode="MarkdownV2"
            )
        return

    pattern = message.text.strip()
    invalid_chars = "IlO0+/"

    mode = user["current_mode"]
    if mode == "starts_and_ends_with":
        try:
            parts = pattern.split(",")
            if len(parts) == 2:
                prefix, suffix = parts
                prefix = prefix.strip()
                suffix = suffix.strip()
            elif len(parts) == 1:
                if user_data[chat_id].get("original_mode") == "starts_with":
                    prefix = parts[0].strip()
                    suffix = ""
                else:
                    prefix = ""
                    suffix = parts[0].strip()
            else:
                raise ValueError
        except ValueError:
            bot.send_message(
                chat_id,
                escape_markdown_v2(f"{BRAND_HEADER}\n\nInvalid input for start and end patterns. Please use the format: `prefix,suffix` (e.g., `ABC,XYZ`).{BRAND_FOOTER}"),  # Generic example
                parse_mode="MarkdownV2"
            )
            return

        total_length = len(prefix) + len(suffix)

        if not (0 <= len(prefix) <= 8 and 0 <= len(suffix) <= 8):
            bot.send_message(
                chat_id,
                escape_markdown_v2(f"{BRAND_HEADER}\n\nPrefix and Suffix should be between 0-8 characters each.{BRAND_FOOTER}"),
                parse_mode="MarkdownV2"
            )
            return

        if any(char in prefix for char in invalid_chars) or any(char in suffix for char in invalid_chars):
            bot.send_message(
                chat_id,
                escape_markdown_v2(f"{BRAND_HEADER}\n\nInvalid characters found. Please use only Base58 characters: 123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz{BRAND_FOOTER}"),
                parse_mode="MarkdownV2"
            )
            return

        if "original_mode" not in user_data[chat_id]:
            user_data[chat_id]["original_mode"] = mode

        if 5 <= total_length <= 8:
            user_data[chat_id]["temp_pattern"] = pattern
            user_data[chat_id]["original_mode"] = mode

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("✅ Yes, Proceed", callback_data=f"proceed_with_long_pattern"))
            markup.add(InlineKeyboardButton("❌ Cancel", callback_data="generate_wallet"))

            bot.send_message(
                chat_id,
                escape_markdown_v2(f"{BRAND_HEADER}\n\n"
                    "⚠️ **WARNING:** Generating a pattern with a combined length of 5-8 characters may take several hours or even days, depending on the complexity of the pattern, whether 'Ignore Case' is enabled, and server load. 1-4 character patterns are recommended for faster generation.\n\n"
                    "Do you want to proceed with generating the pattern?\n\n"
                    f"{BRAND_FOOTER}"),
                reply_markup=markup,
                parse_mode="MarkdownV2"
            )
        else:
            start_wallet_generation(chat_id, pattern, mode, message)

    elif mode:
        pattern = pattern.strip()
        if len(pattern) < 1 or len(pattern) > 8:
            bot.send_message(
                chat_id,
                escape_markdown_v2(f"{BRAND_HEADER}\n\n"
                    "Pattern should be between 1-8 characters long."
                    f"{BRAND_FOOTER}"),
                parse_mode="MarkdownV2"
            )
            return

        if any(char in pattern for char in invalid_chars):
            bot.send_message(
                chat_id,
                escape_markdown_v2(f"{BRAND_HEADER}\n\n"
                    "Please enter a valid pattern using Base58 characters.\n\n"
                    "Valid characters: 123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
                    f"{BRAND_FOOTER}"),
                parse_mode="MarkdownV2"
            )
            return

        if 5 <= len(pattern) <= 8:
            user_data[chat_id]["temp_pattern"] = pattern
            user_data[chat_id]["original_mode"] = mode

            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("✅ Yes, Proceed", callback_data=f"proceed_with_long_pattern"))
            markup.add(InlineKeyboardButton("❌ Cancel", callback_data="generate_wallet"))

            bot.send_message(
                chat_id,
                escape_markdown_v2(f"{BRAND_HEADER}\n\n"
                    "⚠️ **WARNING:** Generating a 5-8 character pattern may take several hours or even days depending on the complexity of the pattern, whether 'Ignore Case' is enabled, and server load. 1-4 character patterns are recommended for faster generation.\n\n"
                    "Do you want to proceed with generating the pattern?\n\n"
                    f"{BRAND_FOOTER}"),
                reply_markup=markup,
                parse_mode="MarkdownV2"
            )

        else:
            start_wallet_generation(chat_id, pattern, mode, message)
    else:
        bot.send_message(
            chat_id,
            escape_markdown_v2(f"{BRAND_HEADER}\n\nPlease select a pattern placement option first (Starts With/Ends With){BRAND_FOOTER}"),
            parse_mode="MarkdownV2"
        )

# ... (rest of your callback handlers: proceed_with_long_pattern, regenerate_callback)

# --- Main Execution ---
if __name__ == "__main__":
    while True:
        try:
            print(f"{BRAND_EMOJI} {BOT_NAME} is starting...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(5)
