from django.contrib import admin

from .models import *



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

admin.site.register(FichierAdherents, FichierAdherentsAdmin)



class NotesInline(admin.TabularInline):
	model = Note
	list_per_page = 1000
	fk_name = 'target'
	extra = 0

class AdherentAdmin(admin.ModelAdmin):
	model = Adherent
	inlines = [NotesInline, ]
	list_per_page = 1000
	list_display = ("num_adherent", "actuel", "nom", "prenom", "federation", "email", "fichier")
	readonly_fields = (
		"actuel", "num_adherent", "genre", "nom", "prenom", "federation", "date_premiere_adhesion", "date_derniere_cotisation",
		"adresse1", "adresse2", "adresse3", "adresse4", "code_postal", "ville", "pays", "npai", "date_de_naissance",
		"profession", "tel_portable", "tel_bureau", "tel_domicile", "email", "mandats", "commune", "canton",
		"fichier")
	# TODO : derniere date de cotis !
admin.site.register(Adherent, AdherentAdmin)



class NoteAdmin(admin.ModelAdmin):
	model = Note
	list_per_page = 2000
	list_display = ("target", "author", "text", "date")

admin.site.register(Note, NoteAdmin)



class DroitsAdmin(admin.ModelAdmin):
	model = Droits
	list_per_page = 1000

admin.site.register(Droits, DroitsAdmin)

class CnilAdmin(admin.ModelAdmin):
	model = Cnil
	list_per_page = 1000

admin.site.register(Cnil, CnilAdmin)