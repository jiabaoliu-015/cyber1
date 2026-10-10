# Web Lab — Erebus Station crew portal (space-station-server).
#
# The core website is Python standard library only. Playwright + Chromium power
# the "captain" duty bot that makes the stored-XSS stage solvable, by opening
# submitted tickets as the captain in a headless browser. Set ENABLE_ADMIN_BOT=0
# to run the core site without the bot.
FROM python:3.12-slim

# Browser runtime for the captain bot (the only non-stdlib dependency).
RUN pip install --no-cache-dir playwright \
    && playwright install --with-deps chromium

WORKDIR /app
COPY . .

ENV PYTHONUNBUFFERED=1 \
    ENABLE_ADMIN_BOT=1
EXPOSE 8080

# Bind to all interfaces inside the container; Compose publishes it to loopback only.
CMD ["python3", "-B", "web/app.py", "--host", "0.0.0.0", "--port", "8080"]
