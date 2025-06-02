# SecureCart
This README provides setup instructions and structure overview for SecureCart, a secure Django-based e-commerce platform.

## Getting Started

1. Clone the repository:
```
git clone https://github.warwick.ac.uk/u5562961/CCSE-CW1.git
cd CCSE-CW1
```

## Project Structure

- `accounts/`: User authentication and profile management
- `cart/`: Shopping cart functionality
- `catalog/`: Product and category management
- `orders/`: Order processing and management
- `pages/`: Static page handling
- `templates/`: HTML templates
- `securecart/`: Core project settings

## Environment Setup

1. Create a virtual environment:
```
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies 

```
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:

```
SECRET_KEY=your_secret_key
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
STRIPE_PUBLISHABLE_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
EMAIL_HOST_USER=your_email
EMAIL_HOST_PASSWORD=your_email_password
```

4. Generate SSL certificates for development:

```
python manage.py generate_certificates
```

5. Run migrations:

```
python manage.py migrate
```

6. Create a superuser:

```
python manage.py createsuperuser
```

## Run

1. Run the development server:

```
python manage.py runserver_plus --cert-file certificates/cert.pem --key-file certificates/key.pem
```

2. Access the application:
    - Open your browser and go to `https://localhost:8000`
    - Note: You might need to accept the self-signed SSL certificate warning in your browser