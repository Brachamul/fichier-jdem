from django.contrib import admin

from .models import *


class AdherentAdmin(admin.ModelAdmin):
	model = Adherent
	list_per_page = 250
	list_display = ("num_adherent", "nom", "prenom", "federation", "email", "a_jour_de_cotisation", "fichier")
	readonly_fields = (
		"num_adherent", "genre", "nom", "prenom", "federation", "date_premiere_adhesion", "date_derniere_cotisation",
		"a_jour_de_cotisation", "adresse1", "adresse2", "adresse3", "adresse4", "code_postal", "ville", "pays", "npai", "date_de_naissance",
		"profession", "tel_portable", "tel_bureau", "tel_domicile", "email", "mandats", "commune", "canton",
		"fichier")
admin.site.register(Adherent, AdherentAdmin)



class ReadersInline(admin.TabularInline):
	model = Reader
	extra = 1

class DroitsAdmin(admin.ModelAdmin):
	model = Droits
	inlines = [ReadersInline, ]
	list_per_page = 250

admin.site.register(Droits, DroitsAdmin)



class CnilAdmin(admin.ModelAdmin):
	model = Cnil
	list_per_page = 250

admin.site.register(Cnil, CnilAdmin)



class AdherentInline(admin.TabularInline):
	# For each feature, display development projects that can improve it
	model = Adherent
	list_per_page = 50
	fk_name = 'fichier'
	extra = 0
	fields = ("genre", "nom", "prenom", "federation", "ville", "email", "tel_portable", "num_adherent",)
	readonly_fields = fields

	class Media:
		css = { "all" : ("css/hide_admin_original.css",) }

class FichierAdherentsAdmin(admin.ModelAdmin):
	model = FichierAdherents
	list_per_page = 50
	inlines = [AdherentInline, ]
	list_display = ("pk", "date_d_import", "date", "importateur", "fichier_csv", )

admin.site.register(FichierAdherents, FichierAdherentsAdmin)