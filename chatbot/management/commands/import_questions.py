# For Production!!!!!!!!!!!!!!!!!!!#Run this------python manage.py import_questions --file=chatbot/new_questions_format.json-----#

import json
import os
from django.core.management.base import BaseCommand
from chatbot.models import Topic, Question, FollowUpOption
from django.db import transaction

class Command(BaseCommand):
    help = 'Import questions and topics from a JSON file ith optional follow-up logic'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='chatbot/new_logic.json',
            help='Path to the JSON file containing questions and topics'
        )


    @transaction.atomic
    def handle(self, *args, **options):
        file_path = options['file']

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"❌ File not found: {file_path}"))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for topic_data in data:
            topic_name = topic_data["topic"]
            topic, _ = Topic.objects.get_or_create(name=topic_name)

            for q in topic_data["questions"]:
                question_text = q.get("question", "").strip()
                
                # Handle "answer_yes" being a string or dictionary
                raw_yes = q.get("answer_yes")
                answer_no = q.get("answer_no", "").strip()
                
                if isinstance(raw_yes, str):
                    # Flat yes/no logic
                    question = Question.objects.create(
                        topic = topic,
                        question_text = question_text,
                        answer_yes = raw_yes.strip(),
                        answer_no = answer_no
                    )
                    
                elif isinstance(raw_yes, dict):
                    follow_up_text = raw_yes.get("follow_up", "").strip()
                    question = Question.objects.create(
                        topic = topic,
                        question_text = question_text,
                        answer_yes = "", # leave flat answer blank
                        answer_no = answer_no,
                        follow_up_text = follow_up_text
                        
                    )
                    
                    for opt in raw_yes.get("options", []):
                        FollowUpOption.objects.create(
                            question=question,
                            option_text = opt.get("option", "").strip(),
                            response_text= opt.get("response", "").strip(),
                            allow_user_input=opt.get("allow_user_input", False)
                        )

        self.stdout.write(self.style.SUCCESS("✅ Questions nested logic imported successfully!"))
