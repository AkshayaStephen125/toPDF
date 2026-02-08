# toPDF – AWS Powered PDF Generator

## 📌 About the Project

**toPDF** is an AWS‑powered backend application that converts uploaded content (text, images, documents) into PDF files.

### Architecture Overview

* Files are uploaded to **AWS S3**
* An **AWS Lambda** function converts content into PDF
* Converted PDFs are stored back in **S3**
* Secure access is enforced using **IAM roles, permissions, and trust policies**
* The application is deployed on **AWS EC2**
* **Nginx + Gunicorn** are used for production‑ready deployment

---

## 🚀 Deployment & Setup Steps

### 1️⃣ Clone the Project

Clone the repository and move into the project directory.

```bash
git clone https://github.com/AkshayaStephen125/toPDF.git
cd app/toPDF
```

---

### 2️⃣ Create S3 Bucket

Create an S3 bucket to store uploaded files and generated PDFs.

* **Bucket Name:** `pdfy-it`
* Region: Same region as Lambda & EC2
* Disable public access (recommended)

---

### 3️⃣ Create Lambda Function to Generate PDF

Create an AWS Lambda function:

* **Function Name:** `generate-pdf`
* Runtime: Python 3.x
* Role: Custom IAM role with S3 access

*Lambda performs serverless PDF generation when triggered by the application.*

---

### 4️⃣ Impose IAM Roles for S3 Access & Lambda Invocation

Create an IAM role with the following permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::pdfy-it",
        "arn:aws:s3:::pdfy-it/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:*:*:function:generate-pdf"
    }
  ]
}
```

***Explanation:***

* *Grants read/write access to S3*
* *Allows invoking the Lambda PDF generator*

---

### 5️⃣ Integrate AWS Using `aws configure`

Configure AWS credentials on EC2.

```bash
aws configure
```

Provide:

* AWS Access Key
* AWS Secret Key
* Default Region
* Output format (json)

*This connects the EC2 instance with AWS services securely.*

---

### 6️⃣ Launch Instance in AWS EC2

Steps:

1. Launch EC2 (Ubuntu 20.04 / 22.04)
2. Create or use existing key pair (`toPDF.pem`)
3. Attach IAM role with Lambda invoke permission
4. Select security group

---

### 7️⃣ Impose IAM Permission for EC2 to Invoke Lambda

Attach this policy to the EC2 IAM role:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:*:*:function:generate-pdf"
    }
  ]
}
```

*Allows EC2‑hosted Django app to trigger Lambda.*

---

### 8️⃣ Update Inbound Rules (VERY IMPORTANT)

**EC2 → Security Groups → Inbound Rules**

| Type | Port | Source    |
| ---- | ---- | --------- |
| SSH  | 22   | Your IP   |
| HTTP | 80   | 0.0.0.0/0 |

***Explanation:***

* *SSH for server access*
* *HTTP for public traffic*

---

## 🛠 Production Setup Using Nginx

### 1️⃣ SSH Into EC2 Instance

```bash
ssh -i toPDF.pem ubuntu@<EC2_PUBLIC_IP>
```

* `ssh` – Secure shell
* `-i` – Private key file

---

### 2️⃣ System Update

```bash
sudo apt update
sudo apt upgrade -y
```

Updates system packages.

---

### 3️⃣ Project Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install django
```

Creates and activates a virtual environment.

---

### 4️⃣ Run Django Dev Server (Test Only)

```bash
python manage.py runserver 0.0.0.0:8000
```

⚠ Not for production use.

---

### 5️⃣ Install Gunicorn (Production WSGI Server)

```bash
pip install gunicorn
```

Test:

```bash
gunicorn toPDF.wsgi:application --bind 0.0.0.0:8000
```

---

### 6️⃣ Install Nginx

```bash
sudo apt install nginx -y
sudo systemctl status nginx
```

---

### 7️⃣ Nginx Configuration for Django

```bash
sudo nano /etc/nginx/sites-available/toPDF
```

```nginx
server {
    listen 80;
    server_name <EC2_PUBLIC_IP>;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Enable:

```bash
sudo ln -s /etc/nginx/sites-available/toPDF /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

---

### 8️⃣ Create Gunicorn Systemd Service

```bash
sudo nano /etc/systemd/system/gunicorn.service
```

```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/toPDF
ExecStart=/home/ubuntu/toPDF/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 toPDF.wsgi:application

[Install]
WantedBy=multi-user.target
```

Enable & start:

```bash
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

---

### 9️⃣ Static Files (Production)

```bash
python manage.py collectstatic
```

**settings.py**

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

**Nginx update:**

```nginx
location /static/ {
    alias /home/ubuntu/toPDF/staticfiles/;
}
```

Restart:

```bash
sudo systemctl restart nginx
```

---

### 🔐 10️⃣ AWS Security Group (CRITICAL)

Allowed Ports:

* 22 – SSH
* 80 – HTTP

❌ Remove:

* 8000 (internal only)

---

## ✅ Production Behavior

* App runs after logout
* Survives server reboot
* Gunicorn auto‑starts
* Nginx handles public traffic

---

## 🔧 Common Management Commands

```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
sudo systemctl status gunicorn
sudo systemctl status nginx
journalctl -u gunicorn --no-pager | tail -30
```

---

### 👩‍💻 Author

**Akshaya Stephen**

AWS | Django | Serverless | Production Deployment
