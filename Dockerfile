FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir pyTelegramBotAPI requests

# Copy bot files
COPY collbomber_bot.py .
COPY config_token.py .

# Run bot
CMD ["python3", "-u", "collbomber_bot.py"]
