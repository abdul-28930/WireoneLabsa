from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework import serializers
from django.utils import timezone
from decimal import Decimal
from .models import PricingConfig, ConfigurationLog

class PricingConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingConfig
        fields = '__all__'
        
    def validate_applicable_days(self, value):
        """Validate that applicable_days contains valid day numbers (0-6)"""
        try:
            days = [int(d.strip()) for d in value.split(',')]
            for day in days:
                if day < 0 or day > 6:
                    raise serializers.ValidationError("Days must be between 0-6 (Monday=0, Sunday=6)")
            return value
        except ValueError:
            raise serializers.ValidationError("Invalid format for applicable_days")

class ConfigurationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigurationLog
        fields = '__all__'

class PricingConfigViewSet(viewsets.ModelViewSet):
    queryset = PricingConfig.objects.all()
    serializer_class = PricingConfigSerializer
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active pricing configurations"""
        active_configs = PricingConfig.objects.filter(is_active=True)
        serializer = self.get_serializer(active_configs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a specific pricing configuration"""
        config = self.get_object()
        config.is_active = True
        config.save()
        return Response({'status': 'activated'})
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """Deactivate a specific pricing configuration"""
        config = self.get_object()
        config.is_active = False
        config.save()
        return Response({'status': 'deactivated'})

class ConfigurationLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ConfigurationLog.objects.all()
    serializer_class = ConfigurationLogSerializer

class CalculatePriceView(APIView):
    """
    Calculate price based on distance, duration, and waiting time.
    
    POST /api/calculate-price/
    
    Request body:
    {
        "distance": 5.5,    // Distance in kilometers
        "duration": 45,     // Duration in minutes  
        "waiting_time": 5   // Waiting time in minutes
    }
    
    Response:
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
    """
    
    def get_active_config(self, day_of_week):
        configs = PricingConfig.objects.filter(is_active=True)
        for config in configs:
            applicable_days = [int(d) for d in config.applicable_days.split(',')]
            if day_of_week in applicable_days:
                return config
        return None

    def calculate_time_multiplier(self, config, duration_hours):
        if duration_hours <= 1:
            return config.time_multiplier_1
        elif duration_hours <= 2:
            return config.time_multiplier_2
        else:
            return config.time_multiplier_3

    def post(self, request):
        try:
            # Get required parameters
            distance = Decimal(str(request.data.get('distance', 0)))  # in kilometers
            duration = Decimal(str(request.data.get('duration', 0)))  # in minutes
            waiting_time = Decimal(str(request.data.get('waiting_time', 0)))  # in minutes
            
            # Validate input
            if distance < 0 or duration < 0 or waiting_time < 0:
                return Response(
                    {"error": "Distance, duration, and waiting time must be non-negative"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get current day of week (0 = Monday, 6 = Sunday)
            current_day = timezone.now().weekday()
            
            # Get active pricing configuration for current day
            config = self.get_active_config(current_day)
            if not config:
                return Response(
                    {"error": "No active pricing configuration found for the current day"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Calculate base price
            if distance <= config.base_distance:
                distance_price = config.base_price
            else:
                additional_distance = distance - config.base_distance
                distance_price = config.base_price + (additional_distance * config.additional_km_price)

            # Calculate time multiplier
            duration_hours = duration / 60  # Convert minutes to hours
            time_multiplier = self.calculate_time_multiplier(config, duration_hours)
            
            # Calculate waiting charges
            if waiting_time <= config.free_waiting_time:
                waiting_charges = Decimal('0')
            else:
                billable_waiting_time = waiting_time - config.free_waiting_time
                waiting_charges = billable_waiting_time * config.waiting_charge_per_min

            # Calculate final price
            final_price = (distance_price * time_multiplier) + waiting_charges

            return Response({
                "price": round(final_price, 2),
                "breakdown": {
                    "base_price": float(config.base_price),
                    "distance_price": float(distance_price),
                    "time_multiplier": float(time_multiplier),
                    "waiting_charges": float(waiting_charges)
                },
                "config_used": {
                    "name": config.name,
                    "id": config.id
                },
                "calculation_details": {
                    "input": {
                        "distance": float(distance),
                        "duration_minutes": float(duration),
                        "waiting_time_minutes": float(waiting_time)
                    },
                    "formula": "Price = (Distance_Price * Time_Multiplier) + Waiting_Charges"
                }
            })

        except (ValueError, TypeError):
            return Response(
                {"error": "Invalid input format"},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """
        Get API documentation for the calculate-price endpoint
        """
        return Response({
            "endpoint": "/api/calculate-price/",
            "method": "POST",
            "description": "Calculate ride price based on distance, duration, and waiting time",
            "required_parameters": {
                "distance": "Distance in kilometers (decimal)",
                "duration": "Duration in minutes (decimal)", 
                "waiting_time": "Waiting time in minutes (decimal)"
            },
            "example_request": {
                "distance": 5.5,
                "duration": 45,
                "waiting_time": 5
            },
            "example_response": {
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
        })

class APIRootView(APIView):
    """
    API Root - Lists all available endpoints
    """
    def get(self, request):
        return Response({
            "message": "Pricing Module API",
            "version": "1.0",
            "endpoints": {
                "calculate_price": "/api/calculate-price/",
                "pricing_configs": "/api/pricing-configs/",
                "configuration_logs": "/api/configuration-logs/",
                "active_configs": "/api/pricing-configs/active/",
                "admin": "/admin/",
                "api_root": "/api/"
            },
            "documentation": {
                "calculate_price": "POST to calculate ride price",
                "pricing_configs": "CRUD operations for pricing configurations",
                "configuration_logs": "View configuration change history",
                "active_configs": "Get all active pricing configurations"
            }
        }) 