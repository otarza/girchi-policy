from django.apps import AppConfig


class AccountsConfig(AppConfig):
    # Django 6: DEFAULT_AUTO_FIELD is BigAutoField by default — no need to set it.
    name = "apps.accounts"
    verbose_name = "Accounts"
