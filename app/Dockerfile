FROM python:3.10-slim

# set workdir
WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# copy app code
COPY . .

# expose Flask port
EXPOSE 8081

# run app
CMD ["python", "app.py"]

















# FROM python:3.10-slim

# WORKDIR /app

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt

# COPY . .

# CMD ["python", "app.py"]
