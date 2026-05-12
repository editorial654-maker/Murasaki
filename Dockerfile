# Railway optimized Dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV RAILWAY=true

RUN apt-get update && apt-get install -y \
    clang \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY attack.c .
COPY super.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Compile and verify with Railway-specific output
RUN echo "::group::🔨 Compiling attack binary" && \
    clang attack.c -o bgmi_attack -lpthread && \
    chmod +x bgmi_attack && \
    echo "::endgroup::" && \
    echo "::group::✅ Verification" && \
    if [ -f "./bgmi_attack" ]; then \
        echo "Binary size: $(ls -lh bgmi_attack | awk '{print $5}')"; \
        echo "Verification PASSED ✅"; \
    else \
        echo "Verification FAILED ❌"; \
        exit 1; \
    fi && \
    echo "::endgroup::"

RUN mkdir -p /root/bin && cp bgmi_attack /root/bin/

# Railway deploy notification
RUN echo '#!/bin/bash\n\
echo "🛸═══════════════════════════════════════════════════════════🛸"\n\
echo "⚡ ZETA REALM - DEPLOYED ON RAILWAY ⚡"\n\
echo "🛸═══════════════════════════════════════════════════════════🛸"\n\
echo ""\n\
echo "🤖 Bot: ZO | 👑 Alpha: @YOWAI_MO_456"\n\
echo "✅ Binary: VERIFIED | 💀 Mode: ATTACK READY"\n\
echo ""\n\
echo "📡 Bot is LIVE - Awaiting commands..."\n\
echo "🛸═══════════════════════════════════════════════════════════🛸"\n' > /railway_notify.sh && chmod +x /railway_notify.sh

CMD /railway_notify.sh && python super.py
