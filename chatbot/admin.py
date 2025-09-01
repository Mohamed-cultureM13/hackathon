from django.contrib import admin
from .models import Topic, Question, UserSession, FollowUpOption

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1

class TopicAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [QuestionInline]

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'topic')
    list_filter = ('topic',)
    search_fields = ('question_text',)

class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'current_topic', 'question_index')
    list_filter = ('current_topic',)
    search_fields = ('phone_number',)
    
class FollowUpOptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'option_text', 'allow_user_input')

admin.site.register(Topic, TopicAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(UserSession, UserSessionAdmin)
admin.site.register(FollowUpOption, FollowUpOptionAdmin)
