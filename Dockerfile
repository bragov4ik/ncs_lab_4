FROM python:3.10
ENV FLASK_APP=main
WORKDIR /web-server
COPY requirements.txt /web-server
RUN pip3 install --upgrade pip -r requirements.txt
COPY . /web-server
RUN python init_database.py
EXPOSE 5000
CMD flask run --host 0.0.0.0