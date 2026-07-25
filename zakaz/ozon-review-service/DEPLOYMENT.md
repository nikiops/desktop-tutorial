# Deployment Guide

This service is intended to run on a Linux server behind Nginx with HTTPS and a process manager such as systemd.

## 1. Connect to the server

Use SSH credentials managed outside this repository. Prefer key-based authentication and disable password-based root login where possible.

```bash
ssh <user>@<server-host>
```

Never store server passwords, private keys or hosting credentials in Git.

## 2. Clone the repository

```bash
git clone <repository-url>
cd <repository>/zakaz/ozon-review-service
```

## 3. Configure the application

Create a local `.env` file on the server and provide the required credentials through the server environment or secret manager.

```env
OZON_CLIENT_ID=your_client_id
OZON_API_KEY=your_ozon_api_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=your_model
YANDEX_API_KEY=your_yandex_api_key
YANDEX_FOLDER_ID=your_folder_id
YANDEX_MODEL=your_model
```

Do not commit the resulting `.env` file.

## 4. Install and start

Use the deployment scripts in this directory as a starting point, or install the Python environment manually and run the FastAPI service behind Nginx.

Typical verification commands:

```bash
sudo systemctl status ozon-service
sudo journalctl -u ozon-service -f
curl http://localhost:8000/health
```

## 5. HTTPS

Configure Nginx as a reverse proxy and issue a TLS certificate using your preferred certificate provider (for example, Let's Encrypt/Certbot).

## Security checklist

- Keep API keys in environment variables or a secret manager.
- Use SSH keys instead of committed passwords.
- Rotate any credential that was previously committed to Git history.
- Restrict server firewall rules to required ports only.
- Run the application as a dedicated non-root service account where practical.
