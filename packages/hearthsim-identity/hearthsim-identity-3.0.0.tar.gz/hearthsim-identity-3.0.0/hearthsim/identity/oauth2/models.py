from django.db import models
from django.urls import reverse
from oauth2_provider.models import AbstractApplication
from oauth2_provider.scopes import SettingsScopes


class Application(AbstractApplication):
	allowed_scopes = models.TextField(
		blank=True,
		help_text="Which scopes the application is allowed to request (blank = all scopes)"
	)
	description = models.TextField(blank=True)
	homepage = models.URLField()
	livemode = models.BooleanField(default=False)
	allowed_schemes = models.TextField(
		blank=True,
		help_text="Which redirect_uri schemes the application may use (blank = default)"
	)
	legacy_key = models.CharField(
		blank=True, max_length=255,
		help_text="Legacy API key (backwards-compatibility for pre-oauth2 clients)"
	)

	def get_absolute_url(self):
		return reverse("oauth2_app_update", kwargs={"client_id": self.client_id})

	def get_allowed_schemes(self):
		if self.allowed_schemes:
			return self.allowed_schemes.split()
		return super().get_allowed_schemes()


class ApplicationScopes(SettingsScopes):
	"""
	A scopes backend which imitates the default SettingsScopes but also checks
	the `allowed_scopes` field on Application to determine what an app can request.
	If anything is specified in `allowed_scopes`, those are used instead.
	"""
	def get_available_scopes(self, application=None, request=None, *args, **kwargs):
		if application is not None and application.allowed_scopes.strip():
			return application.allowed_scopes.strip().split()

		return super().get_available_scopes(application, request, *args, **kwargs)
