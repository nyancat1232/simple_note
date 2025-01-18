FROM python:3.12

WORKDIR /study

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
COPY pyplus ./pyplus
COPY new_page ./new_page
COPY experiment ./experiment
COPY table_editor ./table_editor
COPY main.py ./

RUN pip3 install -r requirements.txt

EXPOSE 8044

CMD [ "streamlit", "run", "--server.address=0.0.0.0", "--server.port=8044", "main.py"]