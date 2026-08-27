FROM python:3.11-slim

# Install system dependencies & LaTeX distribution
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Add src to PYTHONPATH so 'src.xyz' imports work cleanly
ENV PYTHONPATH=/app

COPY . .

CMD ["python", "-u", "src/bot.py"]
