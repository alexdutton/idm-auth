import urllib.parse

from django.apps import apps, AppConfig
from django.conf import settings
from django.db.models.signals import pre_save



class IDMAuthCoreIntegrationConfig(AppConfig):
    name = 'idm_auth.auth_core_integration'

    def ready(self):
        from idm_auth.models import User
        pre_save.connect(self.create_identity, User)

    def create_identity(self, instance, **kwargs):
        from idm_auth.models import User
        assert isinstance(instance, User)
        if instance.is_active and not instance.identity_id:
            app_config = apps.get_app_config('idm_auth')
            identity_url = urllib.parse.urljoin(settings.IDM_CORE_URL, '/person/')
            data = {
                'names': [{
                    'context': 'presentational',
                    'components': [{
                        'type': 'given',
                        'value': instance.first_name,
                    }, ' ', {
                        'type': 'family',
                        'value': instance.last_name,
                    }]
                }],
                'emails': [{
                    'context': 'home',
                    'value': instance.email,
                }],
                'date_of_birth': instance.date_of_birth.isoformat(),
                'state': 'active',
            }
            response = app_config.session.post(identity_url, data)
            response.raise_for_status()
            instance.identity_id = response.json()['id']