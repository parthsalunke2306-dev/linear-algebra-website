from django.db import models
from django.contrib.auth.models import User

class SiteSetting(models.Model):
    site_title = models.CharField(max_length=200, default="Linear Algebra & Field Theory Explorer")
    hero_subtitle = models.TextField(default="Interactive step-by-step LaTeX matrix solvers, 3D vector graphics, dynamic matrix resizers, Light/Dark theme toggle, and LaTeX formula copy.")
    curriculum_badge = models.CharField(max_length=100, default="DATA SCIENCE MATHEMATICS CURRICULUM")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return f"Site Configuration ({self.site_title})"


class TopicModule(models.Model):
    UNIT_CHOICES = [
        ('UNIT 1', 'Unit 1: Linear Systems, Fields & Vectors'),
        ('UNIT 2', 'Unit 2: Inner Products, Determinants & Diagonalization'),
    ]

    slug = models.SlugField(unique=True, help_text="Unique URL identifier e.g. gaussian, gf2, vectors")
    topic_code = models.CharField(max_length=20, default="TOPIC 1.1")
    title = models.CharField(max_length=150)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='UNIT 1')
    description = models.TextField()
    icon_class = models.CharField(max_length=50, default="bi-grid-3x3", help_text="Bootstrap icon class e.g. bi-grid-3x3, bi-shield-check")
    icon_color_class = models.CharField(max_length=50, default="text-info", help_text="Color class e.g. text-info, text-warning, text-success")
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=1)

    class Meta:
        ordering = ['display_order']
        verbose_name = "Topic Module"
        verbose_name_plural = "Topic Modules"

    def __str__(self):
        return f"[{self.topic_code}] {self.title}"


class SavedPreset(models.Model):
    topic = models.ForeignKey(TopicModule, on_delete=models.CASCADE, related_name='presets')
    title = models.CharField(max_length=100)
    matrix_data = models.TextField(help_text="Matrix values formatted as space/newline separated text")
    notes = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.topic.title} - {self.title}"


class UserCalculationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calculations')
    topic_slug = models.CharField(max_length=50)
    topic_title = models.CharField(max_length=150)
    input_summary = models.TextField()
    result_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "User Calculation History"
        verbose_name_plural = "User Calculation Histories"

    def __str__(self):
        return f"{self.user.username} - {self.topic_title} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
