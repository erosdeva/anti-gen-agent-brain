FROM python:3.14.3  

EXPOSE 8080
WORKDIR /app

COPY . ./

RUN pip install -r requirements.txt && \
    export GOOGLE_API_KEY="AQ.Ab8RN6IiNz2exEsMaDO_3CkQAGUNNNKA3166TQCa7c96hJTXPg"

ENTRYPOINT ["streamlit", "run", "dashboard.py", "--server.port=8080", "--server.address=0.0.0.0"]
