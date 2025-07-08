# Student Management System

## Prerequisites

- Python 3.10+  
- Git  
- (Optional) Virtual environment tool (`venv` or `virtualenv`)

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/prejanNeu/Student-Management-System.git
cd Student-Management-System
python3 -m venv smsenv
source smsenv/bin/activate    # Linux/macOS
# For Windows:
# smsenv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 127.0.0.1:PORT

```

