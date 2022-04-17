FROM python:3.11
ENV FLASK_APP=main
WORKDIR /web-server
COPY requirements.txt /web-server
RUN pip3 install --upgrade pip -r requirements.txt
COPY . /web-server
RUN python ./web-server/init_database.py
EXPOSE 5000
CMD flask run