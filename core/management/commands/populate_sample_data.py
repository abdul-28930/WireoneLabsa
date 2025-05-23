from django.core.management.base import BaseCommand
from decimal import Decimal
from core.models import PricingConfig

class Command(BaseCommand):
    help = 'Populate sample pricing configurations for testing'

    def handle(self, *args, **options):
        # Clear existing configs
        PricingConfig.objects.all().delete()
        
        # Create sample configurations
        configs = [
            {
                'name': 'Weekday Standard',
                'base_distance': Decimal('3.0'),
                'base_price': Decimal('80.0'),
                'additional_km_price': Decimal('25.0'),
                'time_multiplier_1': Decimal('1.0'),
                'time_multiplier_2': Decimal('1.25'),
                'time_multiplier_3': Decimal('2.2'),
                'free_waiting_time': 3,
                'waiting_charge_per_min': Decimal('5.0'),
                'applicable_days': '0,1,2,3,4',  # Monday to Friday
                'is_active': True
            },
            {
                'name': 'Weekend Premium',
                'base_distance': Decimal('2.5'),
                'base_price': Decimal('100.0'),
                'additional_km_price': Decimal('35.0'),
                'time_multiplier_1': Decimal('1.2'),
                'time_multiplier_2': Decimal('1.5'),
                'time_multiplier_3': Decimal('2.5'),
                'free_waiting_time': 2,
                'waiting_charge_per_min': Decimal('8.0'),
                'applicable_days': '5,6',  # Saturday, Sunday
                'is_active': True
            },
            {
                'name': 'Night Surcharge',
                'base_distance': Decimal('2.0'),
                'base_price': Decimal('120.0'),
                'additional_km_price': Decimal('40.0'),
                'time_multiplier_1': Decimal('1.5'),
                'time_multiplier_2': Decimal('2.0'),
                'time_multiplier_3': Decimal('3.0'),
                'free_waiting_time': 2,
                'waiting_charge_per_min': Decimal('10.0'),
                'applicable_days': '0,1,2,3,4,5,6',  # All days (for special scenarios)
                'is_active': False  # Inactive by default
            },
            {
                'name': 'Economy Mode',
                'base_distance': Decimal('5.0'),
                'base_price': Decimal('60.0'),
                'additional_km_price': Decimal('15.0'),
                'time_multiplier_1': Decimal('1.0'),
                'time_multiplier_2': Decimal('1.1'),
                'time_multiplier_3': Decimal('1.5'),
                'free_waiting_time': 5,
                'waiting_charge_per_min': Decimal('3.0'),
                'applicable_days': '0,1,2,3,4',  # Monday to Friday
                'is_active': False  # Inactive by default
            }
        ]
        
        created_count = 0
        for config_data in configs:
            config = PricingConfig.objects.create(**config_data)
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created pricing config: {config.name} ({"Active" if config.is_active else "Inactive"})'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} pricing configurations')
        )
        
        # Display summary
        self.stdout.write('\n--- Sample Data Summary ---')
        active_configs = PricingConfig.objects.filter(is_active=True)
        self.stdout.write(f'Active configurations: {active_configs.count()}')
        
        for config in active_configs:
            days_map = {0: 'Mon', 1: 'Tue', 2: 'Wed', 3: 'Thu', 4: 'Fri', 5: 'Sat', 6: 'Sun'}
            applicable_days = [days_map[int(d)] for d in config.applicable_days.split(',')]
            self.stdout.write(f'  - {config.name}: {", ".join(applicable_days)}')
        
        # Show sample API calls
        self.stdout.write('\n--- Sample API Calls ---')
        self.stdout.write('Test the pricing API with these examples:')
        self.stdout.write('\n1. Basic calculation:')
        self.stdout.write('curl -X POST http://localhost:8000/api/calculate-price/ \\')
        self.stdout.write('  -H "Content-Type: application/json" \\')
        self.stdout.write('  -d \'{"distance": 5.5, "duration": 45, "waiting_time": 5}\'')
        
        self.stdout.write('\n2. Weekend calculation:')
        self.stdout.write('curl -X POST http://localhost:8000/api/calculate-price/ \\')
        self.stdout.write('  -H "Content-Type: application/json" \\')
        self.stdout.write('  -d \'{"distance": 8.0, "duration": 75, "waiting_time": 10}\'')
        
        self.stdout.write('\n3. List all configurations:')
        self.stdout.write('curl http://localhost:8000/api/pricing-configs/')
        
        self.stdout.write('\n4. Get active configurations only:')
        self.stdout.write('curl http://localhost:8000/api/pricing-configs/active/')
        
        self.stdout.write('\n5. View API documentation:')
        self.stdout.write('Visit http://localhost:8000/api/ in your browser') 