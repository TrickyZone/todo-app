# pi-shaped-demo

````markdown
# Animated To-Do Web Application

A simple **To-Do list web application** with an animated frontend, built using:

- **Backend:** Python Flask  
- **Frontend:** Vanilla HTML/CSS/JS  
- **Database:** PostgreSQL  
- **Cache/Session:** Redis  

Users can sign up, log in, and manage their personal to-do list.

---

## Features

- User login & signup  
- Add and delete todos  
- Animated UI for fun interaction  
- Redis caching for todo counts  
- `/db` route to view your todos in JSON (requires login)  

---

## Prerequisites

- Docker  
- Docker Compose (for local testing without Kubernetes)  
- Minikube + kubectl (for Kubernetes deployment)  
- Python 3.10+ (optional, if running locally without Docker)

---

## Running Locally with Python (without Docker)

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
````

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make sure PostgreSQL and Redis are running locally. Set environment variables:

```bash
export POSTGRES_DB=todoapp
export POSTGRES_USER=todo
export POSTGRES_PASSWORD=todopw
```

4. Initialize the database:

```bash
psql -U todo -d todoapp -f init.sql
```

5. Run the Flask app:

```bash
python app.py
```

6. Open in browser:

```
http://127.0.0.1:8081
```

* Login with: `alice / alicepw`
* Or create a new account.

---

## Running with Docker Compose

`docker-compose.yml` example:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: todoapp
      POSTGRES_USER: todo
      POSTGRES_PASSWORD: todopw
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7

  web:
    build: .
    ports:
      - "8081:8081"
    environment:
      POSTGRES_DB: todoapp
      POSTGRES_USER: todo
      POSTGRES_PASSWORD: todopw
    depends_on:
      - db
      - redis

volumes:
  db_data:
```

Run:

```bash
docker-compose up --build
```

Open in browser:

```
http://localhost:8081
```

---

## Deploying on Minikube

1. Start Minikube:

```bash
minikube start
eval $(minikube docker-env)
```

2. Build the Docker image inside Minikube:

```bash
docker build -t todoapp:latest .
```

3. Apply Kubernetes manifests:

```bash
kubectl apply -f k8s/init-sql.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/app.yaml
```

4. Check pods:

```bash
kubectl get pods
```

5. Access the app:

```bash
minikube service todoapp
```

* Login with `alice / alicepw` or create a new account.

---

## Accessing the Database

1. Get Postgres pod name:

```bash
kubectl get pods
```

2. Enter Postgres shell:

```bash
kubectl exec -it <postgres-pod-name> -- psql -U todo -d todoapp
```

3. Useful queries:

```sql
\dt;                 -- list tables
SELECT * FROM users; -- show users
SELECT * FROM todos; -- show todos
```

---

## Access Todos in JSON

* Login to the app first.
* Then open:

```
http://<your-ip>:<node-port>/db
```

Example (Minikube NodePort 30001):

```
http://192.168.50.59:30001/db
```

This returns a JSON object with the logged-in user’s todos.

---

## Security Notes

* Passwords are currently stored in **plain text**. Use hashing (`werkzeug.security`) for production.
* `/db` exposes data for the logged-in user only. Do **not** expose passwords in JSON.

---

## License

MIT License

