FROM python:3.14.3  

EXPOSE 8080
WORKDIR /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/bin/bash", "/entrypoint.sh"]