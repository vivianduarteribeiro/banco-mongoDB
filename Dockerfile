# Dockerfile
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
ENV PORT=8501
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /app
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
