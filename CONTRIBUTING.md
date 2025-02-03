# Contributing to NameGenAI

Thank you for your interest in contributing to NameGenAI! We welcome contributions from everyone.

## Ways to Contribute

*   **Report Bugs:** If you find a bug, please open an issue on GitHub describing the problem and how to reproduce it.
*   **Suggest Features:** If you have an idea for a new feature, feel free to open an issue to discuss it.
*   **Improve Documentation:** Help us make the documentation clearer, more accurate, and easier to understand.
*   **Write Code:** Contribute code to fix bugs, add features, or improve the existing codebase.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** to your local machine:

    ```bash
    git clone https://github.com/your-username/NameGenAI-Bot.git
    ```
3. **Create a new branch** for your changes:

    ```bash
    git checkout -b my-feature-branch
    ```
4. **Make your changes** and commit them with clear, descriptive commit messages.
5. **Push your branch** to your fork:

    ```bash
    git push origin my-feature-branch
    ```
6. **Open a pull request** on GitHub from your branch to the `main` branch of the original repository.

## Development Setup
* Create a virtual environment
```bash
python3 -m venv venv

Activate the virtual environment (Linux/macOS)

source venv/bin/activate

Activate the virtual environment (Windows)

venv\Scripts\activate

Install the dependencies

pip install -r requirements.txt

Create a .env file and add the following with your own keys

BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
SOLANA_KEYGEN_PATH=/path/to/solana-keygen

Coding Style Guidelines
Follow PEP 8 style guidelines.

Write clear and concise code.

Comment your code where necessary.

Write unit tests for your changes if possible.

Pull Request Guidelines
Keep your pull requests focused on a single issue or feature.

Provide a clear description of your changes in the pull request.

Make sure your code builds and passes all tests.

Be responsive to feedback from reviewers.

Code of Conduct
Please note that this project has a Code of Conduct. By participating in this project, you agree to abide by its terms.

We look forward to your contributions!
