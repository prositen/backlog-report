FROM python:3.10.12 AS build
RUN apt-get update && apt-get -y install git
RUN pip install --upgrade pip
COPY requirements.txt /requirements.txt
RUN pip install --root /install -r /requirements.txt --no-warn-script-location

FROM python:3.10

ENV TZ=Europe/Stockholm
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY --from=build /install /
ENV PYTHONPATH .:/app
COPY ./ /app
WORKDIR /app
COPY ./version.txt /app
COPY ./start.sh /start.sh
RUN chmod +x /start.sh
CMD ["/start.sh"]
