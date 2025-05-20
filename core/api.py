from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from decimal import Decimal
from .models import PricingConfig

class CalculatePriceView(APIView):
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