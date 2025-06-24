FROM python:3.12
LABEL authors="jiisanda"

WORKDIR /usr/src/app

COPY requirements/api.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r api.txt  # Fix the path here too

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
