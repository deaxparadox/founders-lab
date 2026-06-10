# Deployment Guide

**Server:** AWS EC2 — Ubuntu (`ubuntu@ip-172-31-14-162`)  
**Domains:**  
- Frontend: `https://agent.thentrepreneurlab.com`  
- Backend: `https://backend.thentrepreneurlab.com`

---

## Server Layout (current state)

```
/home/ubuntu/
├── brunda/                          # OLD backend repo (no longer used, keep for venv)
│   └── venv/brunda-backend/         # Python virtualenv — SHARED by new backend too
├── brunda-fe-deploy/                # Frontend source / build repo
│   ├── dist/                        # Built output (gitignored, extracted from dist.tar)
│   └── .env                         # Frontend env vars
├── ai-bot-handover/                 # ACTIVE backend repo (dev/backend branch)
│   ├── src/                         # Django app root
│   │   ├── run_unicorn.py           # Uvicorn entry point
│   │   ├── .env                     # Backend env vars
│   │   └── logs/                    # Django log files
│   └── requirements.txt
└── dist.tar                         # Frontend build archive (dropped here to deploy)

/var/www/agent-fe/                   # Nginx serves frontend from here

/etc/nginx/sites-available/
├── backend.thentrepreneurlab.com    # Backend reverse proxy config
└── agent.thentrepreneurlab.com      # Frontend static file config
```

**Process manager:** PM2  
**PM2 process ID 2** → `agent-be-2` → runs `ai-bot-handover/src/run_unicorn.py`

---

## Part 1 — Initial Server Setup (first-time only)

### 1.1 System packages

```bash
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv python3-pip
sudo apt-get install -y nginx postgresql redis tmux
sudo apt-get install -y certbot python3-certbot-nginx

# Node.js (for PM2)
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# PM2
sudo npm install -g pm2
```

### 1.2 PostgreSQL database

```bash
# Create DB user
sudo -u postgres createuser -P --interactive
# When prompted:
#   Name: superdbuser (or your chosen name)
#   Password: <your password>
#   Superuser: y

# Create database
sudo -u postgres createdb brundadb -O superdbuser
```

Verify connection:
```bash
psql -U superdbuser -h localhost -d brundadb
```

### 1.3 Redis

Redis installed via apt runs on localhost:6379 by default. No config change needed.

```bash
sudo systemctl enable redis
sudo systemctl start redis
redis-cli ping   # should return PONG
```

---

## Part 2 — Backend Deployment

### 2.1 Clone the repository

```bash
cd /home/ubuntu
git clone https://github.com/thentrepreneurlab/ai-bot-handover.git --single-branch --branch dev/backend
cd ai-bot-handover
```

### 2.2 Python virtual environment

The virtualenv lives in the old `brunda/` repo directory. Reuse it:

```bash
# If brunda/ venv already exists:
source /home/ubuntu/brunda/venv/brunda-backend/bin/activate

# If setting up fresh (brunda/ not present):
python3 -m venv /home/ubuntu/venv/backend
source /home/ubuntu/venv/backend/bin/activate
```

Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3 Environment file

```bash
vim /home/ubuntu/ai-bot-handover/src/.env
```

Paste and fill in:

```bash
# Server
HOST=0.0.0.0
PORT=9018

# PostgreSQL
DBNAME=brundadb
DBHOST=localhost
DBPORT=5432
DBUSER=superdbuser
DBPASSWORD=<your_db_password>

# OpenAI
OPENAI_API_KEY=<your_key>
OPENAI_CHAT_MODEL=gpt-4o
MODEL_PLATFORM=openai

# Bubble.io
BUBBLE_API_KEY=<your_key>
BUBBLE_BASE_URL=https://api.bubble.io
BUBBLE_PASSWORD_DEFAULT=1234567890

# Pinecone
PINECONE_API_KEY=<your_key>
PINECONE_INDEX_NAME=<your_index>

# Google Places
GOOGLE_API_KEY=<your_key>

# URLs
FRONTEND_URL=https://agent.thentrepreneurlab.com?sid={}
BACKEND_URL=https://backend.thentrepreneurlab.com

# Django
DEBUG=False
SECRET_KEY=<generate_a_new_one>
ALLOWED_HOSTS=backend.thentrepreneurlab.com,localhost

# Token bypass (comma-separated emails, or leave empty)
TOKEN_DISABLE_ACCOUNT=
```

Generate a new SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2.4 Run database migrations

```bash
source /home/ubuntu/brunda/venv/brunda-backend/bin/activate
cd /home/ubuntu/ai-bot-handover/src
python manage.py migrate
```

LangGraph checkpoint tables (`langgraph_checkpoint`, `langgraph_checkpoint_blobs`, `langgraph_writes`) are created automatically when the server starts for the first time.

### 2.5 Start the backend with PM2

```bash
cd /home/ubuntu/ai-bot-handover/src

# First-time start
pm2 start run_unicorn.py --interpreter python --name agent-be

# Save PM2 process list so it survives reboots
pm2 save
pm2 startup   # follow the printed instruction (usually: sudo env PATH=... pm2 startup)
```

Check it's running:
```bash
pm2 list
pm2 log agent-be        # watch logs in real time (Ctrl+C to exit)
```

---

## Part 3 — Frontend Deployment

There are two methods. **Method A** is the current live workflow (pre-built tar). **Method B** is building directly on the server.

### Method A — Deploy from dist.tar (current workflow)

This is how it's been done. A pre-built `dist.tar` is produced on a dev machine and uploaded to the server.

**On the dev machine (before uploading):**
```bash
cd brunda-fe-deploy   # or your frontend repo
npm run build
tar -cvf dist.tar dist/
scp dist.tar ubuntu@<server-ip>:~/
```

**On the server:**
```bash
cd /home/ubuntu

# Clean out old build
rm -rvf dist

# Extract new build
tar -xvf dist.tar

# Copy to Nginx web root
sudo cp -vr dist/* /var/www/agent-fe/

# Reload Nginx
sudo systemctl restart nginx.service

# Clean up
rm -rvf dist
```

### Method B — Build directly on the server

```bash
cd /home/ubuntu/brunda-fe-deploy
git pull

# Edit env if needed
vim .env
# VITE_CHAT_API_BASE_URL=https://backend.thentrepreneurlab.com
# VITE_EXTERNAL_DASHBOARD_URL=https://dashboard.thentrepreneurlab.com/entrepreneur

npm install
npm run build

sudo cp -vr dist/* /var/www/agent-fe/
sudo systemctl restart nginx.service
```

---

## Part 4 — Nginx Configuration

### 4.1 Frontend site

```bash
sudo vim /etc/nginx/sites-available/agent.thentrepreneurlab.com
```

```nginx
server {
    listen 80;
    server_name agent.thentrepreneurlab.com;

    root /var/www/agent-fe;
    index index.html;

    # SPA fallback — all routes serve index.html
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

Enable it:
```bash
sudo ln -s /etc/nginx/sites-available/agent.thentrepreneurlab.com /etc/nginx/sites-enabled/
```

### 4.2 Backend site (reverse proxy)

```bash
sudo vim /etc/nginx/sites-available/backend.thentrepreneurlab.com
```

```nginx
server {
    listen 80;
    server_name backend.thentrepreneurlab.com;

    location / {
        proxy_pass http://127.0.0.1:9018;
        proxy_http_version 1.1;

        # WebSocket support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Increase timeout for long AI responses
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
}
```

Enable it:
```bash
sudo ln -s /etc/nginx/sites-available/backend.thentrepreneurlab.com /etc/nginx/sites-enabled/
```

### 4.3 Test and reload Nginx

```bash
sudo nginx -t                        # must say "syntax is ok"
sudo systemctl restart nginx.service
```

### 4.4 SSL (Certbot — one time setup)

```bash
sudo certbot --nginx -d agent.thentrepreneurlab.com
sudo certbot --nginx -d backend.thentrepreneurlab.com
```

Certbot auto-renews via a systemd timer. Verify:
```bash
sudo systemctl status certbot.timer
```

---

## Part 5 — Routine Operations

### Deploying a backend code update

```bash
cd /home/ubuntu/ai-bot-handover

# Pull latest code
git pull

# If there are local uncommitted changes (e.g. debug edits):
git stash -u -m "description of stash"
git pull

# Restart the backend
pm2 restart agent-be

# Watch logs
pm2 log agent-be
```

If new Python packages were added to `requirements.txt`:
```bash
source /home/ubuntu/brunda/venv/brunda-backend/bin/activate
pip install -r requirements.txt
pm2 restart agent-be
```

If there are new database migrations:
```bash
source /home/ubuntu/brunda/venv/brunda-backend/bin/activate
cd /home/ubuntu/ai-bot-handover/src
pm2 stop agent-be
python manage.py migrate
pm2 start agent-be
```

### Deploying a frontend update

See Part 3 above. Short version:
```bash
# Drop dist.tar in ~/
tar -xvf dist.tar
sudo cp -vr dist/* /var/www/agent-fe/
sudo systemctl restart nginx.service
rm -rvf dist
```

### Checking service health

```bash
pm2 list                             # backend process status
pm2 log agent-be                     # real-time backend logs
sudo systemctl status nginx          # Nginx status
sudo systemctl status postgresql     # DB status
sudo systemctl status redis          # Redis status
```

### Viewing backend logs

```bash
# Real-time (PM2)
pm2 log agent-be

# Django app logs (rotating files)
tail -f /home/ubuntu/ai-bot-handover/src/logs/ai_app.log
tail -f /home/ubuntu/ai-bot-handover/src/logs/bubbleio_app.log

# Check log file size
du -sch /home/ubuntu/ai-bot-handover/src/logs/ai_app.log
```

### Restarting everything after a server reboot

PM2 is configured to auto-start on boot (`pm2 startup` + `pm2 save` during initial setup). After a reboot just verify:

```bash
pm2 list                             # should show agent-be running
sudo systemctl status nginx
sudo systemctl status postgresql
sudo systemctl status redis
```

If PM2 processes are not running:
```bash
source /home/ubuntu/brunda/venv/brunda-backend/bin/activate
cd /home/ubuntu/ai-bot-handover/src
pm2 start run_unicorn.py --interpreter python --name agent-be
pm2 save
```

---

## Part 6 — Working with PostgreSQL

```bash
# Connect to the database
psql -U superdbuser -h localhost -d brundadb

# Common queries:
# List tables
\dt

# Check LangGraph checkpoint tables exist
\dt langgraph*

# Check user count
SELECT count(*) FROM bubbleio_bubbleusermodel;

# Check chat sessions
SELECT * FROM ai_agentchatidmodel ORDER BY created_at DESC LIMIT 10;

# Check token usage
SELECT * FROM ai_tokenusage;

# Exit
\q
```

---

## Part 7 — Quick Reference

| Task | Command |
|------|---------|
| Start backend | `pm2 start run_unicorn.py --interpreter python --name agent-be` |
| Restart backend | `pm2 restart agent-be` |
| Stop backend | `pm2 stop agent-be` |
| Backend logs | `pm2 log agent-be` |
| List PM2 processes | `pm2 list` |
| Test Nginx config | `sudo nginx -t` |
| Reload Nginx | `sudo systemctl restart nginx.service` |
| Deploy frontend | `tar -xvf dist.tar && sudo cp -vr dist/* /var/www/agent-fe/ && sudo systemctl restart nginx.service` |
| Run migrations | `cd src && python manage.py migrate` |
| Activate virtualenv | `source /home/ubuntu/brunda/venv/brunda-backend/bin/activate` |
| DB access | `psql -U superdbuser -h localhost -d brundadb` |

---

## Part 8 — Known Quirks on This Server

1. **Virtualenv location** — The Python venv is in `brunda/venv/brunda-backend/`, not inside `ai-bot-handover/`. Always activate with `source /home/ubuntu/brunda/venv/brunda-backend/bin/activate` before running Python commands.

2. **PM2 with Python** — PM2 is a Node.js process manager. It works with Python via `--interpreter python`. The process restarts are the same as any other PM2 process.

3. **Two backend processes** — During the migration from `brunda/` to `ai-bot-handover/`, a second process (`agent-be-2`, ID: 2) was started. The old process (ID: 1) may still exist in PM2's list. Run `pm2 list` and make sure only the `ai-bot-handover` process is running.

4. **Frontend is not built on the server** — The server has no `.env` for the frontend build. Builds are done on a dev machine and deployed as `dist.tar`. If you need to build on the server, set up `.env` in `brunda-fe-deploy/` first.

5. **GitHub PATs in bash history** — Three GitHub personal access tokens are visible in `/home/ubuntu/.bash_history`. These should be rotated/revoked if not already. Clear the history after rotation:
   ```bash
   # After rotating tokens in GitHub:
   history -c && history -w
   ```

6. **Log file growth** — `src/logs/ai_app.log` grows quickly under load. Django has a 10MB rotating handler configured. Monitor with `du -sch src/logs/ai_app.log`. If disk fills up, safe to delete old log files while the server is running (they'll be recreated).

7. **tmux** — tmux is installed for keeping sessions alive over SSH. Useful for watching logs while doing other work: `tmux new-session -s logs` then `pm2 log agent-be` inside it.
