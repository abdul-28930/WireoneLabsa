from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import PricingConfig, ConfigurationLog

class PricingConfigForm(ModelForm):
    class Meta:
        model = PricingConfig
        fields = '__all__'

    def clean_applicable_days(self):
        days = self.cleaned_data['applicable_days']
        try:
            day_list = [int(d.strip()) for d in days.split(',')]
            for day in day_list:
                if day not in range(7):
                    raise ValidationError(f"Invalid day number: {day}. Must be between 0 and 6.")
            return ','.join(str(d) for d in sorted(day_list))
        except ValueError:
            raise ValidationError("Days must be comma-separated numbers between 0 and 6")

    def clean(self):
        cleaned_data = super().clean()
        
        # Validate time multipliers
        tm1 = cleaned_data.get('time_multiplier_1')
        tm2 = cleaned_data.get('time_multiplier_2')
        tm3 = cleaned_data.get('time_multiplier_3')
        
        if all([tm1, tm2, tm3]):
            if not (tm1 <= tm2 <= tm3):
                raise ValidationError(
                    "Time multipliers must be in ascending order: "
                    "multiplier_1 <= multiplier_2 <= multiplier_3"
                )
        
        return cleaned_data

class PricingConfigAdmin(admin.ModelAdmin):
    form = PricingConfigForm
    list_display = ('name', 'is_active', 'base_price', 'base_distance', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'is_active')
        }),
        ('Distance Pricing', {
            'fields': ('base_distance', 'base_price', 'additional_km_price')
        }),
        ('Time Multipliers', {
            'fields': ('time_multiplier_1', 'time_multiplier_2', 'time_multiplier_3')
        }),
        ('Waiting Charges', {
            'fields': ('free_waiting_time', 'waiting_charge_per_min')
        }),
        ('Schedule', {
            'fields': ('applicable_days',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        # Log the configuration change
        action = 'UPDATE' if change else 'CREATE'
        ConfigurationLog.objects.create(
            config=obj,
            action=action,
            actor=request.user,
            changes=form.changed_data
        )

class ConfigurationLogAdmin(admin.ModelAdmin):
    list_display = ('config', 'action', 'actor', 'timestamp')
    list_filter = ('action', 'actor', 'timestamp')
    search_fields = ('config__name', 'actor__username')
    readonly_fields = ('config', 'action', 'actor', 'timestamp', 'changes')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(PricingConfig, PricingConfigAdmin)
admin.site.register(ConfigurationLog, ConfigurationLogAdmin)
