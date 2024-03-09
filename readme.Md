# Quiz App README

This repository contains a simple Quiz App and the setup of Flask in Python WSGI HTTP Server.

## Installation and Setup

### Prerequisites

Make sure you have the following installed:

- Python 3
- pip (Python package installer)

### Setup Instructions

1. Clone the repository to your local machine:

    ```bash
    git clone <repository_url>
    ```

2. Navigate to the project directory:

    ```bash
    cd <project_directory>
    ```

3. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the Gunicorn server:

    ```bash
    sudo gunicorn -w 4 -b 0.0.0.0:8000 app:app
    ```

## Usage

Once the server is running, you can access the Quiz App by visiting `http://<server_address>` in your web browser.

## NGINX Configuration

To deploy the Quiz App with NGINX, you can use the following configuration:

```nginx
server {
    listen 80;
    server_name <server_domain>;  # Replace with your domain name or server IP

    location / {
        proxy_pass http://127.0.0.1:8000;  # Assuming Gunicorn is running on port 8000
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-for $proxy_add_x_forwarded_for;
    }
}
```

## Restart Nginx 

```
sudo systemctl restart nginx
```

