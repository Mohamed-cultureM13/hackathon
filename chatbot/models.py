from django.db import models

class Topic(models.Model):
    name = models.CharField(max_length=100)
    # Add these fields to just change the logic with a recap of learned  content & tip
    recap_text = models.TextField(blank=True, null=True)
    bonus_tip = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return self.name

class Question(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    question_text = models.TextField()
    answer_yes = models.TextField()
    answer_no = models.TextField()
    
    #New feature to handle follow-up questions (nested logic)
    follow_up_text = models.TextField(blank=True, null=True) # If any

    def __str__(self):
        return self.question_text
    
    
class FollowUpOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='follow_up_options')
    option_text = models.CharField(max_length=255)
    response_text = models.TextField()
    allow_user_input = models.BooleanField(default=False) # This field handles free_text_input for follow-up questions
    
    def __str__(self):
        return f"{self.option_text} -> {self.response_text}"

class UserSession(models.Model):
    phone_number = models.CharField(max_length=20, unique=True)
    current_topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, related_name='current_topic_sessions')
    question_index = models.IntegerField(default=0)
    answered_questions = models.ManyToManyField(Question, blank=True)
    
    # Add this field to change the logic about topics
    finished_topics = models.ManyToManyField('Topic', related_name='finished_by_users', blank=True)
    
    # Add this field to help restart the topics selection
    restart_topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.SET_NULL, related_name='restart_topic_sessions')

    
    #Add this for paginated button, I'll comment it for a while, nitatumia kama approach ya pili.
    # topic_page = models.IntegerField(default=1)
    
    # Track if user is expected to send free text as follow-up input
    expecting_free_text_for_option = models.ForeignKey(
        FollowUpOption, null=True, blank=True, on_delete=models.SET_NULL
    )
    
    def has_finished_all_topics(self):
        return Topic.objects.exclude(id__in=self.finished_topics.values_list('id', flat=True)).count() == 0

