from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import PricingConfig, ConfigurationLog

class PricingConfigModelTest(TestCase):
    def setUp(self):
        self.config = PricingConfig.objects.create(
            name="Test Config",
            base_distance=Decimal('2.0'),
            base_price=Decimal('50.0'),
            additional_km_price=Decimal('15.0'),
            time_multiplier_1=Decimal('1.0'),
            time_multiplier_2=Decimal('1.25'),
            time_multiplier_3=Decimal('2.2'),
            free_waiting_time=3,
            waiting_charge_per_min=Decimal('5.0'),
            applicable_days="0,1,2,3,4",  # Monday to Friday
            is_active=True
        )

    def test_pricing_config_creation(self):
        self.assertEqual(self.config.name, "Test Config")
        self.assertTrue(self.config.is_active)
        self.assertEqual(self.config.base_distance, Decimal('2.0'))

    def test_string_representation(self):
        expected = "Test Config (Active)"
        self.assertEqual(str(self.config), expected)

class CalculatePriceAPITest(APITestCase):
    def setUp(self):
        self.config = PricingConfig.objects.create(
            name="Test Config",
            base_distance=Decimal('2.0'),
            base_price=Decimal('50.0'),
            additional_km_price=Decimal('15.0'),
            time_multiplier_1=Decimal('1.0'),
            time_multiplier_2=Decimal('1.25'),
            time_multiplier_3=Decimal('2.2'),
            free_waiting_time=3,
            waiting_charge_per_min=Decimal('5.0'),
            applicable_days="0,1,2,3,4,5,6",  # All days
            is_active=True
        )
        self.url = reverse('calculate_price')

    def test_calculate_price_basic(self):
        """Test basic price calculation"""
        data = {
            'distance': 3.0,
            'duration': 30,
            'waiting_time': 2
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Expected: base_price(50) + additional_distance(1*15) = 65, no waiting charges
        expected_price = 65.0
        self.assertEqual(response.data['price'], expected_price)

    def test_calculate_price_with_waiting_charges(self):
        """Test price calculation with waiting charges"""
        data = {
            'distance': 2.0,  # Exactly base distance
            'duration': 30,
            'waiting_time': 8  # 5 minutes over free waiting time
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Expected: base_price(50) + waiting_charges(5*5) = 75
        expected_price = 75.0
        self.assertEqual(response.data['price'], expected_price)

    def test_calculate_price_with_time_multiplier(self):
        """Test price calculation with time multiplier"""
        data = {
            'distance': 2.0,
            'duration': 90,  # 1.5 hours - should use time_multiplier_2
            'waiting_time': 0
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Expected: base_price(50) * time_multiplier_2(1.25) = 62.5
        expected_price = 62.5
        self.assertEqual(response.data['price'], expected_price)

    def test_calculate_price_invalid_input(self):
        """Test validation of negative values"""
        data = {
            'distance': -1.0,
            'duration': 30,
            'waiting_time': 5
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_calculate_price_no_active_config(self):
        """Test error when no active config exists"""
        self.config.is_active = False
        self.config.save()
        
        data = {
            'distance': 5.0,
            'duration': 30,
            'waiting_time': 5
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_api_documentation(self):
        """Test GET request returns API documentation"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('endpoint', response.data)
        self.assertIn('example_request', response.data)

class PricingConfigAPITest(APITestCase):
    def setUp(self):
        self.config = PricingConfig.objects.create(
            name="Test Config",
            base_distance=Decimal('2.0'),
            base_price=Decimal('50.0'),
            additional_km_price=Decimal('15.0'),
            time_multiplier_1=Decimal('1.0'),
            time_multiplier_2=Decimal('1.25'),
            time_multiplier_3=Decimal('2.2'),
            free_waiting_time=3,
            waiting_charge_per_min=Decimal('5.0'),
            applicable_days="0,1,2,3,4",
            is_active=True
        )

    def test_list_pricing_configs(self):
        """Test listing all pricing configurations"""
        url = reverse('pricingconfig-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_pricing_config(self):
        """Test creating a new pricing configuration"""
        url = reverse('pricingconfig-list')
        data = {
            'name': 'New Config',
            'base_distance': '3.0',
            'base_price': '60.0',
            'additional_km_price': '20.0',
            'time_multiplier_1': '1.0',
            'time_multiplier_2': '1.5',
            'time_multiplier_3': '2.5',
            'free_waiting_time': 5,
            'waiting_charge_per_min': '6.0',
            'applicable_days': '5,6',  # Saturday, Sunday
            'is_active': True
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PricingConfig.objects.count(), 2)

    def test_get_active_configs(self):
        """Test getting only active configurations"""
        # Create an inactive config
        PricingConfig.objects.create(
            name="Inactive Config",
            base_distance=Decimal('1.0'),
            base_price=Decimal('40.0'),
            additional_km_price=Decimal('10.0'),
            time_multiplier_1=Decimal('1.0'),
            time_multiplier_2=Decimal('1.0'),
            time_multiplier_3=Decimal('1.0'),
            free_waiting_time=2,
            waiting_charge_per_min=Decimal('3.0'),
            applicable_days="0,1,2,3,4",
            is_active=False
        )
        
        url = reverse('pricingconfig-active')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only active config

    def test_activate_config(self):
        """Test activating a configuration"""
        self.config.is_active = False
        self.config.save()
        
        url = reverse('pricingconfig-activate', kwargs={'pk': self.config.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.config.refresh_from_db()
        self.assertTrue(self.config.is_active)

    def test_deactivate_config(self):
        """Test deactivating a configuration"""
        url = reverse('pricingconfig-deactivate', kwargs={'pk': self.config.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.config.refresh_from_db()
        self.assertFalse(self.config.is_active)

class APIRootTest(APITestCase):
    def test_api_root(self):
        """Test API root endpoint returns all available endpoints"""
        url = reverse('api_root')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('endpoints', response.data)
        self.assertIn('calculate_price', response.data['endpoints'])
        self.assertIn('pricing_configs', response.data['endpoints'])

class PricingCalculationEdgeCasesTest(APITestCase):
    def setUp(self):
        self.config = PricingConfig.objects.create(
            name="Edge Case Config",
            base_distance=Decimal('5.0'),
            base_price=Decimal('100.0'),
            additional_km_price=Decimal('20.0'),
            time_multiplier_1=Decimal('1.0'),
            time_multiplier_2=Decimal('1.5'),
            time_multiplier_3=Decimal('2.5'),
            free_waiting_time=5,
            waiting_charge_per_min=Decimal('10.0'),
            applicable_days="0,1,2,3,4,5,6",
            is_active=True
        )
        self.url = reverse('calculate_price')

    def test_exact_base_distance(self):
        """Test calculation when distance exactly equals base distance"""
        data = {'distance': 5.0, 'duration': 30, 'waiting_time': 0}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['price'], 100.0)  # Exactly base price

    def test_zero_values(self):
        """Test calculation with zero values"""
        data = {'distance': 0, 'duration': 0, 'waiting_time': 0}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['price'], 100.0)  # Base price

    def test_large_values(self):
        """Test calculation with large values"""
        data = {'distance': 100.0, 'duration': 300, 'waiting_time': 60}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(response.data['price'], 0)
        
        # Verify calculation breakdown
        self.assertIn('breakdown', response.data)
        self.assertIn('calculation_details', response.data)
