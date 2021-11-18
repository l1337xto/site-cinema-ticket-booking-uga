from django.db.models.functions import Now
from userauth.models import *
ScheduleMovie._base_manager.filter(PlayingOn__lte=Now()).delete()
Promotions._base_manager.filter(promo_validity__lte=Now()).delete()
