# Telegram Content Generator Bot 🤖

This bot automatically generates engaging content (text + images) and posts it to a Telegram channel at regular intervals. It uses AI APIs for text generation (DeepSeek via OpenRouter) and image creation (Yandex Cloud ML).

## Key Features ✨
- **AI-Powered Content**: Generates blog-style posts using DeepSeek-R1 model
- **Image Generation**: Creates custom images via Yandex Art AI
- **Scheduled Posting**: Auto-posts every 15 minutes
- **HTML Formatting**: Supports Telegram-compatible HTML tags
- **Smart Truncation**: Ensures content fits Telegram limits

## How It Works ⚙️

### 1. Content Generation Pipeline
1. DeepSeek-R1 generates formatted text with:
   - HTML tags (converted to Telegram format)
   - Image description in [PHOTO:...] format
2. Yandex Art AI creates image from description
3. Bot combines text + image for final post

### 2. Technical Stack
- **Text Generation**: `deepseek/deepseek-r1-0528` via OpenRouter
- **Image Generation**: Yandex Cloud ML (`yandex-art`)
- **Core**: Python + `python-telegram-bot`
- **Scheduling**: `schedule` library with threading

## Setup Guide 🛠️

### Prerequisites
- Python 3.8+
- Telegram bot token
- OpenRouter API key
- Yandex Cloud credentials

### Installation
```bash
git clone [your-repo-url]
cd [repo-folder]
pip install -r requirements.txt
__________________________________

### Configuration
Create .env file:
TG_TOKEN=your_telegram_bot_token
TG_CHAT_ID=target_channel_id
DEEPSEEK_API_KEY=your_openrouter_key
YANDEX_API_KEY=your_yandex_key
YANDEX_FOLDER_ID=your_folder_id

### File Structure
├── bot.py            # Main bot logic
├── generated_images/ # Auto-created image cache
├── .env.example      # Configuration template
└── requirements.txt  # Dependencies


### Notes ⚠️
Images are automatically deleted after posting

HTML tags are converted to Telegram-compatible format

Content is truncated to 1024 chars for Telegram limits (but, if you don't need to generate picture, you can send more text)


### To use this:
1. Create a new file named `README.md` in your project folder
2. Copy all this text
3. Paste it into the file
4. Customize the parts in square brackets (like [your-repo-url])

Would you like me to:
1. Add any additional sections?
2. Provide the requirements.txt content?
3. Include troubleshooting tips?
4. Make any specific modifications?
