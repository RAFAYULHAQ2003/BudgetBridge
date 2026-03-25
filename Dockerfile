FROM python:3.12.10-slim

WORKDIR /app

# RUN apt-get update && apt-get install -y \
#     gcc \
#     libpq-dev \
#     python3-dev \
#     build-essential \
#     postgresql-client \
#     netcat-openbsd \
#     bash \
#     && rm -rf /var/lib/apt/lists/*


RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    build-essential \
    postgresql-client \
    netcat-openbsd \
    bash \
    libpango1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libxml2 \
    libxslt1.1 \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh

RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/wait-for-it.sh

EXPOSE 8000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

CMD ["gunicorn", "BudgetBridge.wsgi:application", "--bind", "0.0.0.0:8000"]