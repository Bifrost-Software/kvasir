ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip

WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

COPY app/server.py .
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
