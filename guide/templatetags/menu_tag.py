import datetime
from django import template
from guide.models import Article

register = template.Library()

@register.simple_tag
def wagtail_custom_menu():
	return Article.objects.all().exclude(slug="accueil")