FROM python:3.7-slim
LABEL author='mkhvdm@gmail.com' version=0.1
RUN mkdir /app_foodgram
WORKDIR /app_foodgram
COPY . .
RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0:8000" ]
# CMD ["python3", "manage.py", "runserver", "0:8000"]
