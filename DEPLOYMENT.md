# Deployment Guide

Complete guide for deploying Smart Energy Platform to AWS EC2.

## Prerequisites

- AWS Account (AWS Academy or regular AWS)
- GitHub account
- Domain name (optional)

## Step 1: Launch EC2 Instance

1. Go to AWS Console > EC2 > Launch Instance
2. **Name**: smart-energy-platform
3. **AMI**: Ubuntu Server 22.04 LTS
4. **Instance type**: t2.micro (free tier)
5. **Key pair**: Create new (download .pem file)
6. **Security Group**: Allow SSH (22), HTTP (80), HTTPS (443)
7. **Launch instance**

## Step 2: Connect to EC2
```bash
# Set key permissions
chmod 400 energy-platform-key.pem

# Connect
ssh -i energy-platform-key.pem ubuntu@YOUR_EC2_IP
```

## Step 3: Install Dependencies
```bash
# Update system
sudo apt update
sudo apt upgrade -y

# Install Python and tools
sudo apt install -y python3-pip python3-venv nginx git

# Clone repository
git clone https://github.com/x24250511/smart-energy-platform.git
cd smart-energy-platform

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## Step 4: Setup Database
```bash
# Run migrations
python manage.py migrate

# Create users
python manage.py shell
# Then run user creation script
```

## Step 5: Configure Environment
```bash
# Create .env file
nano .env

# Add configurations (see README.md)
```

## Step 6: Setup Systemd Service
```bash
# Create service file
sudo nano /etc/systemd/system/energy-platform.service

# Add service configuration
# Enable and start
sudo systemctl enable energy-platform
sudo systemctl start energy-platform
```

## Step 7: Configure Nginx
```bash
# Create nginx config
sudo nano /etc/nginx/sites-available/energy-platform

# Enable site
sudo ln -s /etc/nginx/sites-available/energy-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Step 8: Setup AWS Services
```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_SESSION_TOKEN=your_token
export AWS_REGION=us-east-1

# Run setup
python deployment/aws/setup_all_aws_services.py
```

## Step 9: Configure CI/CD

1. Add GitHub secrets:
   - EC2_SSH_KEY
   - EC2_HOST

2. Push to main branch triggers auto-deployment

## Troubleshooting

### Application not starting
```bash
sudo journalctl -u energy-platform -n 50
```

### Nginx errors
```bash
sudo nginx -t
sudo tail -f /var/log/nginx/error.log
```

### Database issues
```bash
python manage.py check
python manage.py migrate
```

## Maintenance

### Update application
```bash
cd ~/smart-energy-platform
git pull origin main
sudo systemctl restart energy-platform
```

### View logs
```bash
sudo journalctl -u energy-platform -f
```

### Backup database
```bash
cp db.sqlite3 db.sqlite3.backup
```
