from django.contrib import admin
from .models import SiteSetting, TopicModule, SavedPreset

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'curriculum_badge', 'show_code_inspector', 'updated_at')

@admin.register(TopicModule)
class TopicModuleAdmin(admin.ModelAdmin):
    list_display = ('topic_code', 'title', 'unit', 'is_active', 'display_order')
    list_editable = ('is_active', 'display_order')
    search_fields = ('title', 'description', 'topic_code')

@admin.register(SavedPreset)
class SavedPresetAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'created_at')
    list_filter = ('topic',)
