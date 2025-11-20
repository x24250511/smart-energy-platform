# Smart Energy Platform

Cloud-based peer-to-peer energy trading platform with AWS integration.

## Live Demo

**Application**: http://100.30.26.145

**Test Credentials**:
- Admin: EN01001 / Adminpass1600
- Users: EN01002-EN01011 / Energy@123

## Features

- User authentication with custom energy number system
- Real-time energy generation and consumption tracking
- Peer-to-peer energy trading (buyback, loan, donation)
- Credit-based transaction system
- AWS cloud integration with 5 services
- Automated CI/CD pipeline

## Technology Stack

### Backend
- Django 4.2
- Python 3.12
- SQLite database
- Custom authentication system

### Cloud Services (AWS)
1. **EC2** - Application hosting
2. **S3** - PDF report storage
3. **DynamoDB** - User data backup
4. **Lambda** - Energy calculations
5. **CloudWatch** - Metrics and monitoring
6. **SNS** - notifing user with Email

### DevOps
- GitHub Actions CI/CD
- Nginx reverse proxy
- Gunicorn WSGI server
- Systemd service management

### Library
- [smart-energy-manager-lib](https://pypi.org/project/smart-energy-manager-lib/) - Custom Python library for energy management

## Architecture
```
User Browser
    ↓
Nginx (Port 80)
    ↓
Gunicorn (Port 8000)
    ↓
Django Application
    ↓
├── SQLite (Primary DB)
├── AWS S3 (PDF Storage)
├── AWS DynamoDB (Backup)
├── AWS Lambda (Calculations)
└── AWS CloudWatch (Monitoring)
```

## Installation

### Local Development
```bash
# Clone repository
git clone https://github.com/x24250511/smart-energy-platform.git
cd smart-energy-platform

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed EC2 setup instructions.

## AWS Services Setup
```bash
# Set AWS credentials
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_SESSION_TOKEN=your_token
export AWS_REGION=us-east-1

# Run setup script
python deployment/aws/setup_all_aws_services.py
```

This creates:
- DynamoDB table for data backup
- S3 bucket for PDF storage
- Lambda function for calculations
- SNS topic for notifications
- CloudWatch dashboard for monitoring

## CI/CD Pipeline

Every push to `main` branch triggers:

1. **Code Quality Check** - Flake8 linting
2. **Security Scan** - Bandit security analysis
3. **Tests** - Django test suite
4. **Deploy** - Automatic deployment to EC2

View pipeline: [GitHub Actions](https://github.com/x24250511/smart-energy-platform/actions)

## Project Structure
```
energy_platform/
├── accounts/              # User authentication app
├── energy/               # Energy management app
├── energy_platform/      # Django project settings
├── static/              # CSS, JS, images
├── deployment/          # Deployment scripts
│   └── aws/            # AWS setup scripts
├── .github/
│   └── workflows/      # CI/CD pipeline
├── requirements.txt
└── manage.py
```

## API Endpoints

- `/accounts/login/` - User login
- `/accounts/register/` - User registration
- `/accounts/logout/` - User logout
- `/energy/` - Dashboard
- `/energy/update/` - Update energy data
- `/energy/buyback/` - Sell surplus energy
- `/energy/loan/` - Loan energy to others
- `/energy/donation/` - Donate energy


## Testing
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test energy

# Check code
python manage.py check
```

## Monitoring

**CloudWatch Dashboard**: [View Dashboard](https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=SmartEnergyPlatform)

Metrics tracked:
- Transaction counts by type
- Total energy traded
- Average transaction sizes
- Lambda performance
- System health

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m "Add feature"`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## License

MIT License - see LICENSE file

## Contact

Project: https://github.com/x24250511/smart-energy-platform
Library: https://pypi.org/project/smart-energy-manager-lib/
Email: projectwebx11@gmail.com

## Acknowledgments

- Django Framework
- AWS Cloud Services
- Bootstrap CSS Framework
- Python Community
