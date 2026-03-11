FROM python:3.14.3  

EXPOSE 8080
WORKDIR /app

COPY . ./

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py", "--dashboard-port=8080"]