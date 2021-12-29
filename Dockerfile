FROM ubuntu:latest

COPY . .

RUN apt-get update

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Moscow
RUN apt-get install -y tzdata

RUN apt-get install -y  \
            python3.9     \
            pip

RUN pip install -r requirements.txt

# main.py will be entrypoint
CMD ["pipenv", "run", "python", "main.py"]
