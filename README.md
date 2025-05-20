# Pricing Module

A configurable pricing module that supports differential pricing for ride-sharing services. Built with Django and Django REST Framework.

## Features

- Configurable pricing based on:
  - Distance (base price and additional per km)
  - Time duration (with multiplier tiers)
  - Waiting time charges
  - Day of the week
- Django Admin interface for managing pricing configurations
- Automatic logging of configuration changes
- REST API for price calculation
- Input validation and error handling

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd pricing-module
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install django djangorestframework python-dotenv
```

4. Apply database migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```

5. Create a superuser for admin access:
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Usage

### Admin Interface

1. Access the admin interface at `http://localhost:8000/admin/`
2. Log in with your superuser credentials
3. Navigate to "Pricing Configurations" to manage pricing rules
4. View configuration change history in "Configuration Logs"

### API Endpoints

#### Calculate Price

**Endpoint:** `POST /api/calculate-price/`

**Request Body:**
```json
{
    "distance": 5.5,    // Distance in kilometers
    "duration": 45,     // Duration in minutes
    "waiting_time": 5   // Waiting time in minutes
}
```

**Response:**
```json
{
    "price": 450.75,
    "breakdown": {
        "base_price": 80.00,
        "distance_price": 155.00,
        "time_multiplier": 1.25,
        "waiting_charges": 10.00
    },
    "config_used": {
        "name": "Weekday Standard",
        "id": 1
    }
}
```

## Price Calculation Formula

The final price is calculated using the formula:
```
Price = (DBP + (Dn * DAP)) * TMF + WC

Where:
- DBP: Distance Base Price
- Dn: Additional distance traveled
- DAP: Distance Additional Price (per km)
- TMF: Time Multiplier Factor
- WC: Waiting Charges
```

## Configuration Guidelines

1. **Distance Base Price (DBP)**
   - Set base price for initial distance coverage
   - Example: ₹80 for first 3km

2. **Distance Additional Price (DAP)**
   - Price per additional kilometer
   - Example: ₹30/km after base distance

3. **Time Multiplier Factor (TMF)**
   - Different multipliers for different duration ranges
   - Example:
     - Up to 1 hour: 1x
     - 1-2 hours: 1.25x
     - Over 2 hours: 2.2x

4. **Waiting Charges (WC)**
   - Free waiting period (e.g., first 3 minutes)
   - Charge per minute after free period
   - Example: ₹5 per 3 minutes after initial free period
