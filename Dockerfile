FROM python:3.12

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/app

EXPOSE 8000

CMD ["sh", "-c", "PYTHONPATH=/code/app uvicorn src.main:app --host 0.0.0.0 --port 8000"]
