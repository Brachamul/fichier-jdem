from django.contrib import admin

from .models import *



class NoteAdmin(admin.ModelAdmin):
	model = Note
	list_per_page = 250
	list_display = ("member", "author", "text", "date")

admin.site.register(Note, NoteAdmin)



class NotesInline(admin.TabularInline):
	model = Note
	extra = 1

class MemberAdmin(admin.ModelAdmin):
	model = Member
	readonly_fields = ("id",)
	list_display = ("id", "__unicode__")
	inlines = [NotesInline, ]

admin.site.register(Member, MemberAdmin)