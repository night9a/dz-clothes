# DZ Clothes - Full Stack Flask Application

A complete e-commerce platform built with Flask, featuring a modern HTML/CSS frontend and a robust backend.

## Features

### Customer Features
- **Product Catalog**: Browse products with categories, images, and pricing in Algerian Dinar (DA)
- **Shopping Cart**: Session-based cart for guests, database-backed for registered users
- **User Authentication**: Email/password registration with email verification
- **Multi-language**: French and Arabic support
- **Order Management**: Checkout with Baridi Mob payment integration
- **Discount Codes**: Apply promotional codes at checkout

### Admin Features
- **Dashboard**: View sales statistics and order summaries
- **Product Management**: Add, edit, and delete products
- **Order Management**: View and update order statuses
- **Discount Management**: Create and manage discount codes
- **Telegram Notifications**: Receive instant notifications for new orders

## Installation

### 1. Prerequisites
- Python 3.8 or higher
- PostgreSQL database
- (Optional) Mailjet account for email sending
- (Optional) Telegram bot for notifications

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file based on `.env.example`:

```bash
# Database (required)
DATABASE_URL=postgres://user:password@host:port/database?sslmode=require

# JWT Secret (required)
JWT_SECRET_KEY=your-super-secret-key-change-in-production

# Email (optional but recommended)
MAILJET_API_KEY=your_mailjet_api_key
MAILJET_SECRET_KEY=your_mailjet_secret_key
MAIL_FROM=noreply@yourdomain.com

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# Application
FLASK_ENV=development
FRONTEND_URL=http://localhost:5000
```

### 4. Initialize Database
The application will automatically create tables and seed sample data on first run:

```bash
python app.py
```

### 5. Access the Application
Open your browser and navigate to:
```
http://localhost:5000
```

## Default Admin Account
- **Email**: admin@admin.com
- **Password**: 123

**⚠️ Important**: Change this password immediately after first login!

## Project Structure
```
dz-clothes-flask/
├── app.py                 # Main Flask application
├── auth.py                # Authentication logic
├── config.py              # Configuration settings
├── db.py                  # Database operations
├── mail_service.py        # Email service (Mailjet)
├── telegram_service.py    # Telegram notifications
├── telegram_bot.py        # Telegram bot runner
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variables template
├── templates/             # HTML templates
│   ├── base.html         # Base template with header/footer
│   ├── home.html         # Homepage
│   ├── shop.html         # Product catalog
│   ├── product.html      # Product detail page
│   ├── cart.html         # Shopping cart
│   ├── checkout.html     # Checkout page
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── verify_email.html # Email verification
│   └── admin/            # Admin panel templates
│       ├── dashboard.html
│       ├── orders.html
│       ├── products.html
│       ├── discounts.html
│       └── settings.html
└── static/                # Static files
    ├── css/
    │   └── style.css     # Main stylesheet
    ├── js/               # JavaScript files (optional)
    └── images/           # Image files

## Usage

### Customer Workflow
1. Browse products on the homepage or shop page
2. Add products to cart (works without registration)
3. Register an account and verify email
4. Checkout with Baridi Mob payment details
5. Receive order confirmation

### Admin Workflow
1. Login with admin credentials
2. View dashboard for sales overview
3. Manage products (add/edit/delete)
4. Process orders (update status)
5. Create discount codes
6. Configure Telegram notifications

## Email Configuration

The application uses Mailjet for sending emails. To set up:

1. Create a free account at https://mailjet.com
2. Get your API key and Secret key from the dashboard
3. Add them to your `.env` file:
```
MAILJET_API_KEY=your_api_key
MAILJET_SECRET_KEY=your_secret_key
MAIL_FROM=noreply@yourdomain.com
```

If email is not configured, verification links will be printed to the console.

## Telegram Notifications

To receive order notifications via Telegram:

1. Create a bot using @BotFather on Telegram
2. Copy the bot token to your `.env` file
3. Run `python telegram_bot.py` in a separate terminal
4. Send `/start` to your bot to get your chat ID
5. Enter the chat ID in the admin settings panel

## Database Schema

The application creates the following tables:
- `users` - User accounts and authentication
- `products` - Product catalog
- `cart_items` - Shopping cart items
- `orders` - Customer orders
- `order_items` - Items in each order
- `discounts` - Promotional discount codes
- `admin_settings` - Application settings

## API Endpoints

The application also includes API endpoints for programmatic access:
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/products` - List products
- `GET /api/products/<id>` - Get product details
- `POST /api/cart` - Add to cart
- `POST /api/checkout` - Place order
- (Plus admin endpoints for management)

## Development

To run in development mode with auto-reload:

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

## Production Deployment

For production deployment:

1. Set environment to production:
```
FLASK_ENV=production
```

2. Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. Use a reverse proxy like Nginx
4. Enable HTTPS
5. Set strong JWT secret
6. Configure proper database connection pooling

## Troubleshooting

### Database Connection Issues
- Verify DATABASE_URL is correct
- Check PostgreSQL is running
- Ensure SSL mode is appropriate for your setup

### Email Not Sending
- Verify Mailjet credentials
- Check MAIL_FROM is a verified sender
- Review console logs for errors

### Telegram Not Working
- Verify bot token is correct
- Ensure bot is started (`python telegram_bot.py`)
- Check chat ID is saved in admin settings

## Support

For issues or questions:
- Check the console logs for error messages
- Verify environment variables are set correctly
- Ensure all dependencies are installed

## License

This project is created for educational purposes.

## Credits

Created by mosho - https://www.instagram.com/mosho_tenx/
