# 🤖 AI Payroll Agent Bot

A Python-based Telegram bot that automates salary tracking using Large Language Models (LLM).

## 🌟 Key Features
- **AI-Powered OCR**: Uses Google Gemini 1.5 to extract specific work hours from schedule photos (tables).
- **Automated Payout Calculation**: Calculates total earnings based on a fixed hourly rate ($31.7$ PLN/h).
- **Persistence**: Stores all logged hours in a SQLite database for monthly tracking.
- **Hybrid Input**: Supports both automated image analysis and manual hour logging.

## 🛠️ Tech Stack
- **Python 3.10+**
- **Telegram Bot API** (python-telegram-bot)
- **Google Generative AI** (Gemini 1.5 Flash/Pro)
- **SQLite** for data storage

## 🚀 Setup
1. Clone the repository:
   ```bash
   git clone [https://github.com/your-username/ai-payroll-bot.git](https://github.com/your-username/ai-payroll-bot.git)