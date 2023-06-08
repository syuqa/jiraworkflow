from django.apps import AppConfig


class JiraConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Jira'

    def ready(self) -> None:
        import Jira.signals
