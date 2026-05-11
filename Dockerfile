FROM python:3.11-slim

# Install clang/gcc
RUN apt-get update && apt-get install -y clang gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy files
COPY attack.c .
COPY drx.py .
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Compile C binary
RUN clang attack.c -o bgmi_attack -lpthread && chmod +x bgmi_attack

# Create bin directory
RUN mkdir -p /root/bin && cp bgmi_attack /root/bin/

# Run bot
CMD ["python", "drx.py"]
