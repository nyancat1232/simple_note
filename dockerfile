FROM python:3.11

WORKDIR /study

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
COPY pyplus ./pyplus
COPY sqlutil ./sqlutil
COPY pages ./pages
COPY main.py ./
COPY .streamlit ./.streamlit

RUN pip3 install -r requirements.txt

EXPOSE 8044

CMD [ "streamlit", "run", "--server.address=0.0.0.0", "--server.port=8044", "main.py"]