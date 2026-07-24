FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir pyTelegramBotAPI requests

# Copy bot files (config_token.py excluded - use BOT_TOKEN env)
COPY collbomber_bot.py .

# Run bot
CMD ["python3", "-u", "collbomber_bot.py"]
