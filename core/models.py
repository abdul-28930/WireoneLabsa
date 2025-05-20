from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

class PricingConfig(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    
    # Distance Base Price Configuration
    base_distance = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Distance covered in base price (in KMs)"
    )
    base_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Base price for the initial distance"
    )
    
    # Distance Additional Price
    additional_km_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Price per additional kilometer"
    )
    
    # Time Multiplier Factors
    time_multiplier_1 = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=1.0,
        help_text="Multiplier for first hour"
    )
    time_multiplier_2 = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=1.25,
        help_text="Multiplier for second hour"
    )
    time_multiplier_3 = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=2.2,
        help_text="Multiplier for third hour onwards"
    )
    
    # Waiting Charges
    free_waiting_time = models.IntegerField(
        default=3,
        help_text="Free waiting time in minutes"
    )
    waiting_charge_per_min = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Charge per minute after free waiting time"
    )
    
    # Days of week this config applies to
    applicable_days = models.CharField(
        max_length=13,  # 7 days + 6 commas
        help_text="Comma-separated days of week (0-6, Monday is 0)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"

    class Meta:
        verbose_name = "Pricing Configuration"
        verbose_name_plural = "Pricing Configurations"

class ConfigurationLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
    ]
    
    config = models.ForeignKey(PricingConfig, on_delete=models.CASCADE)
    action = models.CharField(max_length=6, choices=ACTION_CHOICES)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.action} by {self.actor} at {self.timestamp}"

    class Meta:
        verbose_name = "Configuration Log"
        verbose_name_plural = "Configuration Logs"
