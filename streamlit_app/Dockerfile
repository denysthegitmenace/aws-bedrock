FROM python:3.12-slim

RUN pip install -U pip

COPY requirements.txt app/requirements.txt
RUN pip install -r app/requirements.txt

# copy into a directory of its own (so it isn't in the toplevel dir)
COPY . /app
WORKDIR /app

EXPOSE 80

ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8


# run it!
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=80", "--server.address=0.0.0.0"]
