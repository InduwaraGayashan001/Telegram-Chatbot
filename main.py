import logging
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv
import os
import sys
import asyncio
from openai import OpenAI


class Reference:
    """A class to store previous response from the bot."""

    def __init__(self) -> None:
        self.response = ""

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
reference = Reference()
model = "openai/gpt-4o-mini"

# Initialize OpenAI client
client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=OPENAI_API_KEY,
)

bot = Bot(token=TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

def clear_past():
    """Clear the reference to the previous response."""
    reference.response = ""

@dp.message(CommandStart())
async def start_command(message: types.Message):
    await message.reply("Hello! I am an assistant bot. How can I help you today?")

@dp.message(Command(commands=["help"]))
async def help_command(message: types.Message):
    await message.reply("Hi there! Here are some commands you can use:\n"
                        "/start - Start the bot\n"
                        "/help - Get help information\n"
                        "/clear - Clear the previous conversation\n")

@dp.message(Command(commands=["clear"]))
async def clear_command(message: types.Message):
    clear_past()
    await message.reply("Previous conversation cleared.")

@dp.message()
async def chatgpt(message: types.Message):
    
    respone = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": reference.response},
            {"role": "user", "content": message.text}
        ],
        temperature=0

    )
    reference.response = respone.choices[0].message.content.strip()
    await bot.send_message(
        chat_id=message.chat.id,
        text=reference.response
    )

async def main():
    
    await dp.start_polling(bot, )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
    logging.info("Bot started successfully.")