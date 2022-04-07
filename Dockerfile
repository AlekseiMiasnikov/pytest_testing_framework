FROM python:3.9

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
RUN chmod 777 /app

CMD pytest --alluredir=raw_reports -n auto --reruns 2 --mode selenoid