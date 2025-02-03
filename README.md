# ⚡ NameGenAI: Solana vanity address generator. 

NameGenAI is a Telegram bot designed to help users create unique and personalized Solana wallet addresses. This repository provides a customizable template of the NameGenAI codebase, allowing developers to build their own Solana wallet generation bots. The code is open-source, so you can see exactly how it works and adapt it to your own needs.

## About NameGenAI

NameGenAI's core functionality revolves around generating custom Solana addresses (vanity addresses). It leverages the official Solana CLI tools for secure, local key generation and integrates with OpenAI's GPT-3.5 Turbo to provide intelligent pattern suggestions.

**Key Features of NameGenAI:**

*   **Vanity Address Generation:** Users can specify patterns they want to appear at the beginning, end, or both the start and end of their Solana wallet addresses. The bot uses the `solana-keygen grind` command to achieve this.
*   **AI-Powered Pattern Suggestions:** NameGenAI integrates with OpenAI's GPT-3.5 Turbo to offer creative and relevant pattern ideas. It can even personalize suggestions based on user-provided names.
*   **Case Sensitivity Control:** Users have the option to toggle case sensitivity on or off for their desired patterns.
*   **User-Friendly Telegram Interface:** The bot features a menu-driven interface with clear commands and inline keyboards, making it easy to use.
*   **Real-time Progress Updates:** Users receive updates during the address generation process, so they know what's happening.
*   **Comprehensive Help and Support:** A help menu and an AI assistant are available to guide users.

## Why This Template is Being Released

The primary goal of releasing this template is to empower other developers and provide transparency into NameGenAI's inner workings. By open-sourcing the code, we aim to:

*   **Educate:** Allow developers to learn how a Solana wallet generation bot functions, including interactions with the Solana CLI, Telegram API, and OpenAI API.
*   **Enable Customization:** Provide a foundation for developers to create their own unique Solana-based bots with tailored features, design, AI prompts, and branding.
*   **Foster Innovation:** Encourage the development of new and innovative Solana utilities and services.
*   **Promote Transparency:** Let users see exactly how NameGenAI operates, particularly regarding security and key generation.

## How the Code Works

The template mirrors the core architecture of NameGenAI and is designed to be modular and customizable. Here's a breakdown:

1. **Telegram Bot API Interaction:** The `telebot` library is used to handle commands, messages, and interactions with users on Telegram. You can customize the bot's responses, commands, and overall flow by modifying the relevant handlers.
2. **Solana CLI Integration:** The `subprocess` module is employed to execute the `solana-keygen` command-line tool. This tool, part of the official Solana CLI, is responsible for the actual wallet address generation. The code constructs the appropriate `solana-keygen grind` commands based on user input.
3. **OpenAI API Integration:** The `openai` library facilitates communication with OpenAI's GPT-3.5 Turbo model. This is used to generate pattern suggestions based on user prompts. You can customize the AI's behavior by modifying the prompts in the `AIHelper` class.
4. **Menu-Driven Interface:** The bot presents a user-friendly interface through Telegram's inline keyboards and menus. You can modify the menu structure, button options, and overall design by changing the `create_main_menu_markup`, `create_help_menu_markup`, and `create_generate_wallet_menu` functions.
5. **State Management:** A `user_data` dictionary (using `collections.defaultdict`) is used to track the state of each user's interaction. This includes their selected generation mode, entered pattern, progress, and other relevant data.
6. **Asynchronous Operations:** `asyncio` is used to handle potentially long-running tasks, such as wallet generation and AI requests. This ensures the bot remains responsive even during time-consuming operations.

**Workflow:**

The bot follows a straightforward workflow:

1. **`/start` Command:** Initiates the bot and presents the main menu.
2. **Main Menu:** Offers options like "Generate Wallet," "AI Assistant," "Help," etc.
3. **Generate Wallet:** Guides users through selecting a generation mode ("Starts With," "Ends With," "Starts & Ends With"), getting AI suggestions (optional), and toggling case sensitivity.
4. **Pattern Input:** Prompts users to enter their desired pattern.
5. **Wallet Generation:** Constructs and executes the appropriate `solana-keygen grind` command in a separate process using `subprocess.Popen`.
6. **Progress Updates:** Periodically sends messages to the user about the generation progress, including a dynamic progress bar.
7. **Result:** Informs the user when a matching address is found. **The private key is displayed once and the user must copy it immediately.**
8. **`/stop` Command:** Allows users to terminate the generation process at any time.

## Security Features and Considerations

*   **Temporary Key Generation:** The bot **never** handles, stores, or transmits private keys. It delegates all key generation to the official Solana CLI (`solana-keygen`). The keypair is generated within the `solana-keygen` process, existing only during the generation process.
*   **Official Solana CLI:** The bot relies on the official Solana CLI tools, ensuring that key generation follows established security practices and is performed by a trusted, audited tool.
*   **No Private Key Storage:** The code does not include any functionality to access, store, or manipulate private keys in any way. The bot's primary role is to construct and execute `solana-keygen` commands based on user input and display the key once to the user.
*   **User Responsibility:** Users are ultimately responsible for:
    *   **Immediately copying and securely storing the private key when it is displayed.**
    *   **Understanding the security implications of generating and using Solana wallets.**
    *   **Never sharing their private keys with anyone.**
*   **Environment Variables:** Sensitive data, such as API keys and the bot token, are managed through environment variables (using the `dotenv` library). This is a standard security practice to avoid hardcoding sensitive information directly into the source code.
*   **Open Source Code:** The code is open source, allowing for community scrutiny and review. This transparency helps ensure that the bot operates as intended and that there are no hidden security vulnerabilities.
*   **Disclaimer:** The developers of this template are not responsible for any financial losses or security breaches that may result from the use of this code or any modified versions of it. **Use this template at your own risk.** You are solely responsible for thoroughly reviewing, securing, and testing any bot you create based on this template.
*   **No Recovery:** **If the user does not save the private key when it is displayed, it is lost forever.** There is no backup, and no one else can retrieve it for them.

## Prerequisites and Knowledge Required

Before you can effectively use this template, you should have:

*   **Python Proficiency:** A solid understanding of Python programming, including:
    *   Asynchronous programming with `asyncio`.
    *   Working with external libraries (e.g., `telebot`, `openai`).
    *   Handling subprocesses (`subprocess` module).
*   **Telegram Bot API:** Familiarity with the Telegram Bot API and the `telebot` library is essential. You should understand how to handle commands, messages, inline keyboards, and callback queries.
*   **Solana CLI:** You need to understand how the `solana-keygen` tool works, particularly the `grind` command and its options.
*   **OpenAI API:** You should know how to use the OpenAI API, manage API keys, and structure prompts for GPT-3.5 Turbo.
*   **Security Best Practices:** You must be aware of security best practices for handling API keys, user data, and potentially sensitive operations.
*   **Server Administration (if self-hosting):** If you plan to host your customized bot on a server, you should have basic server administration skills.

## How to Use This Template to Build Your Own Bot

1. **Prerequisites:**
    *   **Install Solana CLI:** Follow the official instructions: [https://docs.solana.com/cli/install](https://docs.solana.com/cli/install)
    *   **Python 3.7+:** Make sure you have Python 3.7 or a later version installed.
    *   **pip:** Ensure that `pip` (the Python package installer) is installed.

2. **Clone the Repository:**

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

    Replace `<repository_url>` and `<repository_directory>` with the actual URL and directory name of this repository.

3. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configuration (.env file):**

    *   Create a file named `.env` in the project's root directory.
    *   **Telegram Bot Token:**
        *   Obtain a bot token from BotFather on Telegram (search for the BotFather bot and follow its instructions).
        *   Add this line to your `.env` file:

            ```
            BOT_TOKEN=your_telegram_bot_token
            ```

    *   **OpenAI API Key:**
        *   Get an API key from OpenAI: [https://platform.openai.com/](https://platform.openai.com/)
        *   Add this line to your `.env` file:

            ```
            OPENAI_API_KEY=your_openai_api_key
            ```

    *   **Solana Keygen Path (Optional):**
        *   If `solana-keygen` is not in your system's PATH, you need to specify its location. Find where it's installed (e.g., `/usr/local/bin/solana-keygen` on Linux/macOS) and add this to your `.env` file:

            ```
            SOLANA_KEYGEN_PATH=/path/to/solana-keygen
            ```

    *   **Customization (Optional):**
        *   You can change the bot's name, brand emoji, and Twitter link:

            ```
            BOT_NAME=MyWalletGenBot
            BRAND_EMOJI=✨
            TWITTER_LINK=https://x.com/MyTwitterHandle
            ```

5. **Code Customization:**

    *   **`your_bot_file.py` (or whatever you named it):** This is the main file where you'll make most of your changes.
    *   **`AIHelper` class:**
        *   Modify the `system_prompt` to change the AI's personality and instructions, thereby altering how it generates pattern suggestions.
        *   Adjust the `get_pattern_suggestion` method to fine-tune the AI's suggestion generation process.
    *   **Bot Command Handlers:**
        *   Modify existing handlers (e.g., `send_welcome`, `handle_ai_question`, `generate_wallet_menu_callback`, etc.) to change the bot's behavior and responses to user commands.
        *   Add new command handlers using the `@bot.message_handler()` decorator to extend the bot's functionality.
    *   **Callback Query Handlers:**
        *   Modify existing callback handlers (e.g., `handle_help_callback`, `request_pattern_starts_with`, etc.) to alter how the bot responds to button presses in inline keyboards.
        *   Add new callback handlers using the `@bot.callback_query_handler()` decorator to handle new types of button interactions.
    *   **`start_wallet_generation` function:**
        *   Review this function carefully, especially if you change how the `solana-keygen` command is constructed or how the generation process is monitored.
    *   **Menu Structure:**
        *   Change the `create_main_menu_markup`, `create_help_menu_markup`, and `create_generate_wallet_menu` functions to modify the bot's menu structure and button options.
    *   **Help Messages:**
        *   Update the `help_sections` dictionary in the `handle_help_callback` function to provide accurate and relevant information to your users.

6. **Testing:**

    *   Run the bot locally:

        ```bash
        python your_bot_file.py
        ```

    *   Thoroughly test all the bot's features and commands in Telegram.
    *   Use different patterns, toggle case sensitivity, and try various scenarios to identify potential issues or areas for improvement.

7. **Deployment (Optional):**

    *   If you want to keep your bot running 24/7, you'll need to deploy it to a server.
    *   **Options:**
        *   **Cloud Platforms:** Heroku, AWS, Google Cloud, DigitalOcean, etc.
        *   **VPS (Virtual Private Server):** Provides more control but requires more server administration knowledge.
    *   **Deployment Steps (General):**
        1. Choose a hosting provider and set up a server.
        2. Install necessary dependencies (Solana CLI, Python, required libraries) on the server.
        3. Transfer your bot's code (including the `.env` file) to the server.
        4. Set up environment variables on the server (using the platform's interface or other methods).
        5. Use a process manager like `pm2` or `systemd` to keep your bot running in the background and restart it if it crashes.

## Important Notes

*   **Security:** Always prioritize security. Review the code carefully, especially the parts that interact with the Solana CLI and handle user input. Implement additional security measures as needed.
*   **Error Handling:** The template has some basic error handling, but you should add more robust error handling and logging to your customized bot. This will help you identify and fix issues more easily.
*   **Rate Limiting:** Consider implementing rate limiting to prevent abuse of the bot, especially for the AI features (which might have usage limits from OpenAI).
*   **Documentation:** Keep your code well-documented, especially if you make significant changes. This will make it easier for others (and yourself) to understand and maintain the code.
*   **Testing:** Write unit tests or integration tests to ensure your customizations work as expected and don't introduce bugs.
*   **No Recovery:** **If the user does not save the private key when it is displayed, it is lost forever.** There is no backup, and no one else can retrieve it for them.

## Disclaimer

This code is provided as a **template for educational and development purposes only**. The developers of this template are not responsible for any financial losses or security issues that may arise from the use of this code or any modified versions of it. **Use this template at your own risk.** You are solely responsible for ensuring the security and proper functioning of any bot you create based on this template. You are also responsible for complying with all applicable laws and regulations, as well as the terms of service of Telegram and OpenAI.

By using this template, you acknowledge that you have read and understood this disclaimer and that you are responsible for the security and proper functioning of your bot.

**Please note:** This is a **template** and requires programming knowledge to customize and deploy. It is not a ready-to-use bot. You will need to configure API keys, understand the code structure, and potentially modify the code to achieve your desired functionality.
