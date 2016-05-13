from django.contrib import admin

from .models import *



class AdherentDuFichierInline(admin.TabularInline):
	# For each feature, display development projects that can improve it
	model = AdherentDuFichier
	list_per_page = 2000
	fk_name = 'fichier'
	extra = 0

class FichierAdherentsAdmin(admin.ModelAdmin):
	model = FichierAdherents
	inlines = [AdherentDuFichierInline, ]

admin.site.register(FichierAdherents, FichierAdherentsAdmin)



class AdherentDuFichierAdmin(admin.ModelAdmin):
	model = AdherentDuFichier
	list_per_page = 2000
	list_display = ("__str__", "num_adherent", "adherent", "fichier")

admin.site.register(AdherentDuFichier, AdherentDuFichierAdmin)



class AdherentAdmin(admin.ModelAdmin):
	model = Adherent
	list_per_page = 2000
	list_display = ("num_adherent", "nom", "prenom", "federation", "email", "importe_par_le_fichier")

admin.site.register(Adherent, AdherentAdmin)



class NoteAdmin(admin.ModelAdmin):
	model = Note
	list_per_page = 2000
	list_display = ("target", "author", "text", "date")

admin.site.register(Note, NoteAdmin)