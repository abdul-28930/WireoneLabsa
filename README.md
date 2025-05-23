# Pricing Module

A configurable pricing module that supports differential pricing for ride-sharing services. Built with Django and Django REST Framework.

## Features

- **Configurable pricing based on:**
  - Distance (base price and additional per km)
  - Time duration (with multiplier tiers)
  - Waiting time charges
  - Day of the week
- **Complete REST API with:**
  - Price calculation endpoint
  - Full CRUD operations for pricing configurations
  - Configuration activation/deactivation
  - Configuration change logging
  - Browsable API interface
- **Django Admin interface** for managing pricing configurations
- **Automatic logging** of configuration changes
- **Comprehensive test suite** with edge cases
- **Sample data management** commands
- **Input validation** and error handling

## Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd pricing-module

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Database Setup

```bash
# Apply migrations
python manage.py migrate

# Create superuser for admin access
python manage.py createsuperuser

# Populate sample data
python manage.py populate_sample_data
```

### 3. Run the Server

```bash
python manage.py runserver
```

The server will start at `http://localhost:8000`

## API Endpoints

### 🔍 API Root
- **GET** `/api/` - Lists all available endpoints and documentation

### 💰 Price Calculation
- **POST** `/api/calculate-price/` - Calculate ride price
- **GET** `/api/calculate-price/` - Get API documentation

### ⚙️ Pricing Configurations
- **GET** `/api/pricing-configs/` - List all configurations
- **POST** `/api/pricing-configs/` - Create new configuration
- **GET** `/api/pricing-configs/{id}/` - Get specific configuration
- **PUT** `/api/pricing-configs/{id}/` - Update configuration
- **DELETE** `/api/pricing-configs/{id}/` - Delete configuration
- **GET** `/api/pricing-configs/active/` - Get only active configurations
- **POST** `/api/pricing-configs/{id}/activate/` - Activate configuration
- **POST** `/api/pricing-configs/{id}/deactivate/` - Deactivate configuration

### 📋 Configuration Logs
- **GET** `/api/configuration-logs/` - View configuration change history

### 🔧 Admin Interface
- **GET** `/admin/` - Django admin interface

## API Usage Examples

### Calculate Price

```bash
curl -X POST http://localhost:8000/api/calculate-price/ \
  -H "Content-Type: application/json" \
  -d '{
    "distance": 5.5,
    "duration": 45,
    "waiting_time": 5
  }'
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
  },
  "calculation_details": {
    "input": {
      "distance": 5.5,
      "duration_minutes": 45,
      "waiting_time_minutes": 5
    },
    "formula": "Price = (Distance_Price * Time_Multiplier) + Waiting_Charges"
  }
}
```

### List Pricing Configurations

```bash
curl http://localhost:8000/api/pricing-configs/
```

### Create New Configuration

```bash
curl -X POST http://localhost:8000/api/pricing-configs/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Night Surcharge",
    "base_distance": "2.0",
    "base_price": "120.0",
    "additional_km_price": "40.0",
    "time_multiplier_1": "1.5",
    "time_multiplier_2": "2.0",
    "time_multiplier_3": "3.0",
    "free_waiting_time": 2,
    "waiting_charge_per_min": "10.0",
    "applicable_days": "0,1,2,3,4,5,6",
    "is_active": true
  }'
```

## Price Calculation Formula

The final price is calculated using the formula:

```
Price = (Distance_Price * Time_Multiplier) + Waiting_Charges

Where:
- Distance_Price = Base_Price + (Additional_Distance * Additional_KM_Price)
- Time_Multiplier = Based on duration (1hr: TMF1, 2hr: TMF2, 3hr+: TMF3)
- Waiting_Charges = (Waiting_Time - Free_Waiting_Time) * Waiting_Charge_Per_Min
```

## Testing

### Run Automated Tests

```bash
# Run all tests
python manage.py test

# Run specific test class
python manage.py test core.tests.CalculatePriceAPITest

# Run with verbose output
python manage.py test --verbosity=2
```

### Manual API Testing

```bash
# Run comprehensive API test script
python test_api.py

# Test specific endpoint
curl -X GET http://localhost:8000/api/
```

### Browse APIs Interactively

Visit `http://localhost:8000/api/` in your browser to use the browsable API interface.

## Configuration Guidelines

### Distance Configuration
- **Base Distance (DBP)**: Distance covered in base price (e.g., 3km)
- **Base Price**: Price for the base distance (e.g., ₹80)
- **Additional KM Price**: Price per additional kilometer (e.g., ₹25/km)

### Time Multipliers
Configure different multipliers for different duration ranges:
- **Up to 1 hour**: 1.0x (no multiplier)
- **1-2 hours**: 1.25x (25% increase)
- **Over 2 hours**: 2.2x (120% increase)

### Waiting Charges
- **Free Waiting Time**: Minutes of free waiting (e.g., 3 minutes)
- **Charge Per Minute**: Rate after free period (e.g., ₹5/minute)

<<<<<<< HEAD
### Day Configuration
Use comma-separated day numbers (0=Monday, 6=Sunday):
- Weekdays: `"0,1,2,3,4"`
- Weekends: `"5,6"`
- All days: `"0,1,2,3,4,5,6"`

## Sample Data

The project includes sample configurations:

1. **Weekday Standard** (Mon-Fri)
   - Base: ₹80 for 3km
   - Additional: ₹25/km
   - Time multipliers: 1.0x, 1.25x, 2.2x
   - Waiting: 3 min free, ₹5/min after

2. **Weekend Premium** (Sat-Sun)
   - Base: ₹100 for 2.5km
   - Additional: ₹35/km
   - Time multipliers: 1.2x, 1.5x, 2.5x
   - Waiting: 2 min free, ₹8/min after

3. **Night Surcharge** (Inactive by default)
   - Base: ₹120 for 2km
   - Additional: ₹40/km
   - Time multipliers: 1.5x, 2.0x, 3.0x
   - Waiting: 2 min free, ₹10/min after

4. **Economy Mode** (Inactive by default)
   - Base: ₹60 for 5km
   - Additional: ₹15/km
   - Time multipliers: 1.0x, 1.1x, 1.5x
   - Waiting: 5 min free, ₹3/min after

## Management Commands

```bash
# Populate sample data
python manage.py populate_sample_data

# Clear and repopulate data
python manage.py populate_sample_data
```

## Development

### Project Structure
```
pricing_module/
├── core/                    # Main Django app
│   ├── api.py              # API views and serializers
│   ├── models.py           # Data models
│   ├── urls.py             # URL routing
│   ├── tests.py            # Test cases
│   ├── admin.py            # Admin interface
│   └── management/         # Management commands
├── pricing_module/         # Django project settings
├── requirements.txt        # Dependencies
├── test_api.py            # API testing script
└── README.md              # This file
```

### Adding New Features

1. **New API Endpoints**: Add to `core/api.py` and `core/urls.py`
2. **New Models**: Add to `core/models.py` and create migrations
3. **New Tests**: Add to `core/tests.py`
4. **New Management Commands**: Add to `core/management/commands/`

### Production Considerations

- Use PostgreSQL instead of SQLite
- Add environment variables for sensitive settings
- Implement caching for frequently accessed configurations
- Add rate limiting for API endpoints
- Use proper logging configuration
- Add monitoring and health checks

## Troubleshooting

### Common Issues

1. **Server won't start**: Check if port 8000 is available
2. **API returns 404**: Ensure URLs are correctly configured
3. **No active configuration**: Run `python manage.py populate_sample_data`
4. **Test failures**: Check database permissions and migrations

### Getting Help

1. Check the browsable API at `/api/`
2. Review the admin interface at `/admin/`
3. Run the test script: `python test_api.py`
4. Check Django logs for detailed error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
=======
4. **Waiting Charges (WC)**
   - Free waiting period (e.g., first 3 minutes)
   - Charge per minute after free period
   - Example: ₹5 per 3 minutes after initial free period
>>>>>>> cdc4da7a68f5ae1fd9da231bd8da7a4cca829e04
