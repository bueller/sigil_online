FROM python

RUN pip3 install flask Flask-Sockets gunicorn
RUN mkdir -p /sigil/api
COPY *py /sigil/api/

EXPOSE 8000
WORKDIR /sigil/api/
ENTRYPOINT ["gunicorn", "--worker-connections", "10", "-t", "86400", "--graceful-timeout", "0", "--threads", "10", "-b", "0.0.0.0:8000", "-k", "flask_sockets.worker", "sol:app"]
