FROM python:3.10-slim

WORKDIR /src

COPY . /src

RUN pip install --upgrade pip
RUN pip install -r src/requirements.txt

EXPOSE 8080

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
