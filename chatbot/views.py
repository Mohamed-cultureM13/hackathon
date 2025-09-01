import json
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .models import Topic, Question, UserSession, FollowUpOption
from .utils import send_whatsapp_message
from django.conf import settings
import random

@csrf_exempt
def whatsAppWebhook(request):
    # --- META VERIFICATION ---
    if request.method == 'GET':
        verify_token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if verify_token == settings.META_VERIFY_TOKEN:
            return HttpResponse(challenge)
        return HttpResponse("Invalid verification token", status=403)


    if request.method == 'POST':
        payload = json.loads(request.body.decode('utf-8'))
        # Nimeongeza hii print function kwa ajili ya debugging-comment it ukiwa live
        # print("📩 Incoming message payload:", json.dumps(payload, indent=2))

        try:
            entry = payload['entry'][0]
            change = entry['changes'][0]
            value = change['value']
            messages = value.get('messages')


            if not messages:
                return JsonResponse({'status': 'no messages to handle'})

            message = messages[0]
            phone = message.get('from')

            msg_text = None

            if 'text' in message:
                text = message.get("text", {})
                msg_text = text.get("body", "").strip()


            if 'interactive' in message:
                interactive = message['interactive']
                button_reply =interactive.get('button_reply', {})

                # Add this for list replies
                list_reply = interactive.get('list_reply', {})

                # Comment this for a while and handle both button and list in an else logic
                # msg_text = button_reply.get('id') or button_reply.get('title', '').strip()


                # Add this logic to handle list messages as well😎
                if list_reply:
                    msg_text = list_reply.get('id') or list_reply.get('title', '').strip()

                else:
                    msg_text = button_reply.get('id') or button_reply.get('title', '').strip()


            # Hii function ipo hapa kwa ajili ya debugging - comment it ukienda live
            # print("📝 Parsed message text:", msg_text)
            if not msg_text:
                print("⚠️ No message text found, skipping response.")


            # interactive = message.get('interactive', {})
            # if interactive:
            #     msg_text = interactive.get("button_reply", {}).get("id") or interactive.get("button_reply", {}).get("title")
            user_session, _ = UserSession.objects.get_or_create(phone_number=phone)

            # The logic to hande free text input in a list message----(Free text follow-up handler)
            if user_session.expecting_free_text_for_option:
                free_text = msg_text.strip()
                option = user_session.expecting_free_text_for_option

                #Respond with a generic and specific message
                send_whatsapp_message(phone, {
                    "type": "text",
                    "text": {"body": f"Ooh umesema: *{free_text}*👍. {option.response_text}"}
                })

                # clear flag so we dont treat next messages as free text
                user_session.expecting_free_text_for_option = None
                user_session.save()

                # Continue to the next question
                topic = user_session.current_topic
                next_q = Question.objects.filter(topic=topic).exclude(id__in=user_session.answered_questions.all()).order_by('id').first()
                if next_q:
                    send_whatsapp_message(phone, send_question(next_q))
                else:
                    # send_whatsapp_message(phone, prompt_continue_or_switch()) #Comment for a while
                    # Check if all topics are completed
                    if user_session.has_finished_all_topics():
                        send_whatsapp_message(phone, {
                            "type": "text",
                            "text": {
                                "body": f"🎉 *Hongera!* Umejifunza mada zote zilizopo kwa sasa. 🏁\n\nEndelea kutembelea chatbot yetu kwa maudhui mapya!"
                            }
                        })

                    else:
                        # Suggest choosing another topic (after completing one)
                        send_whatsapp_message(phone, {
                            "type": "text",
                            "text": {
                                "body": f"🙌 *Umehitimisha mada ya '{topic.name.title()}'*.\n\nChagua mada nyingine ili kuendelea kujifunza:"
                            }
                        })
                        send_whatsapp_message(phone, greeting_message(user_session))

                return JsonResponse({"status": "free_text_handled"})

        except (KeyError, IndexError, TypeError) as e:
            return JsonResponse({"error": f"Invalid payload structure: {str(e)}"}, status=400)


        # Option selection (follow-up option) & make a little update to handle text input as well
        if msg_text.startswith("opt_") and not user_session.expecting_free_text_for_option:
            try:
                option_id = int(msg_text.split("_")[1])
                option = FollowUpOption.objects.get(id=option_id)

                if option.allow_user_input:
                    # Mark session to expect free text input
                    user_session.expecting_free_text_for_option = option
                    user_session.save()
                    send_whatsapp_message(phone, {
                        "type": "text",
                        "text": {"body": "Tafadhali andika jibu lako hapa chini."}
                    })

                    return JsonResponse({"status": "awaiting_free_text"})

                else:
                    send_whatsapp_message(phone, {
                        "type": "text",
                        "text": {"body": option.response_text}
                    })

                    # Continue with next question after showing follow-up response
                    topic = user_session.current_topic
                    next_q = Question.objects.filter(topic=topic).exclude(id__in=user_session.answered_questions.all()).order_by('id').first()
                    if next_q:
                        send_whatsapp_message(phone, send_question(next_q))
                    else:
                        # send_whatsapp_message(phone, prompt_continue_or_switch()) # Comment for a while
                        if user_session.has_finished_all_topics():
                            send_whatsapp_message(phone, {
                                "type": "text",
                                "text": {
                                    "body": f"🎉 *Hongera!* Umejifunza mada zote zilizopo kwa sasa. 🏁\n\nEndelea kutembelea chatbot yetu kwa maudhui mapya!"
                                }
                            })

                        else:
                            # Suggest choosing another topic (after completing one)
                            send_whatsapp_message(phone, {
                                "type": "text",
                                "text": {
                                    "body": f"🙌 *Umehitimisha mada ya '{topic.name.title()}'*.\n\nChagua mada nyingine ili kuendelea kujifunza:"
                                }
                            })
                            send_whatsapp_message(phone, greeting_message(user_session))

                    return JsonResponse({"status": "follow_up_handled"})
            except FollowUpOption.DoesNotExist:
                return JsonResponse({"status": "invalid_option"}, status=404)


        # Greetings😎- Akikusalimia kwa salam yoyote usione haya kumjibu
        if msg_text and msg_text.lower() in ["hi", "hello", "karibu", "habari", "salama", "hey", "mambo", "sasa", "salamu", "nikofiti"]:
            # print("👋 Greeting detected, sending topic buttons.") # For debugging purpose

            # Update greeting logic with user-session
            # This ensures: If the current topic is done, it's cleared out.
            # Then, the greeting menu is sent as usual.
            if user_session.current_topic in user_session.finished_topics.all():
                user_session.current_topic = None
                user_session.restart_topic = None # I've added it just to be safe
                user_session.save()

            send_whatsapp_message(phone, greeting_message(user_session))
            return JsonResponse({'status': 'ok'})

        # To do:-Wakati naongeza topic tatu za ziada, itanibidi kuongeza hizi topic hapa kwenye Topic_Map
        TOPIC_MAP = {
        "akiba": "kuweka akiba",
        "wekeza": "kuwekeza",
        "bajeti": "kupangilia bajeti"
        }

        if msg_text and msg_text.lower() in TOPIC_MAP:
            topic_name = TOPIC_MAP[msg_text]
            topic = Topic.objects.filter(name=topic_name).first()
            if topic in user_session.finished_topics.all():
                user_session.restart_topic = topic
                user_session.save()

                send_whatsapp_message(phone, {
                    "type": "interactive",
                    "interactive": {
                        "type": "button",
                        "body": {"text": f"Ulishamaliza kujifunza mada ya *{topic.name.title()}*. Je, ungependa kuanza tena?"},
                        "action": {
                            "buttons": [
                                {"type": "reply", "reply": {"id": "restart_yes", "title": "Anza Tena"}},
                                {"type": "reply", "reply": {"id": "restart_no", "title": "Hapana"}}
                            ]
                        }
                    }
                })
                return JsonResponse({"status": "restart prompt sent"})

            if not topic:
                return JsonResponse({"status": "topic not found"}, status=404)
            # topic = Topic.objects.filter(name=msg_text).first()
            user_session.current_topic = topic
            user_session.question_index = 0
            user_session.answered_questions.clear()
            user_session.save()
            # question = Question.objects.filter(topic=topic).exclude(id__in=user_session.answered_questions.all()).first()

            # This is for a randomness kinda topic selection
            # question = get_random_question(topic, user_session.answered_questions.values_list('id', flat=True))

            # Make it sequential so as to avoid randomness
            question = Question.objects.filter(topic=topic).exclude(
                id__in=user_session.answered_questions.values_list('id', flat=True)
            ).order_by('id').first()

            if question is not None:
                try:
                    send_whatsapp_message(phone, send_question(question))
                except Exception as e:
                    print(f"❌ Error sending question: {e}")
            else:
                # send_whatsapp_message(phone, prompt_continue_or_switch()) # Comment for a while
                if user_session.has_finished_all_topics():
                        send_whatsapp_message(phone, {
                            "type": "text",
                            "text": {
                                "body": f"🎉 *Hongera!* Umejifunza mada zote zilizopo kwa sasa. 🏁\n\nEndelea kutembelea chatbot yetu kwa maudhui mapya!"
                            }
                        })

                else:
                    # Suggest choosing another topic (after completing one)
                    send_whatsapp_message(phone, {
                            "type": "text",
                            "text": {
                                "body": f"🙌 *Umehitimisha mada ya '{topic.name.title()}'*.\n\nChagua mada nyingine ili kuendelea kujifunza:"
                            }
                        })
                    send_whatsapp_message(phone, greeting_message(user_session))

            return JsonResponse({"status": "question sent"})


        #_________________I am trying to define a new logic here, check this out____________________________#
        if msg_text in ["restart_yes", "restart_no"] and user_session.restart_topic:
            topic = user_session.restart_topic

            if msg_text == "restart_yes":
                # Clear old answers
                user_session.answered_questions.remove(*Question.objects.filter(topic=topic))
                user_session.finished_topics.remove(topic)
                user_session.current_topic = topic
                user_session.restart_topic = None
                user_session.question_index = 0
                user_session.save()

                # For randomness-so I will comment so as to allow the chatbot to have sequential order
                #question = get_random_question(topic, user_session.answered_questions.values_list('id', flat=True))

                # For sequential order create another question variable
                question = Question.objects.filter(topic=topic).exclude(
                    id__in=user_session.answered_questions.values_list('id', flat=True)
                ).order_by('id').first()

                if question:
                    send_whatsapp_message(phone, {
                        "type": "text",
                        "text": {"body": f"🔁 Tumeanza tena mada ya *{topic.name.title()}*. Twende kazi!"}
                    })
                    send_whatsapp_message(phone, send_question(question))
                else:
                    send_whatsapp_message(phone, {
                        "type": "text",
                        "text": {"body": "⚠️ Samahani, hatuwezi kupata maswali ya kuonyesha kwa sasa."}
                    })

                return JsonResponse({"status": "restarted topic"})

            else:  # restart_no
                user_session.restart_topic = None
                user_session.save()
                send_whatsapp_message(phone, greeting_message(user_session))
                return JsonResponse({"status": "restart declined"})


        #_____________________End___________________________________________________________________________#


        # Handle yes and no response
        if msg_text in ["Ndiyo", "Hapana", "yes", "no"]:
            topic = user_session.current_topic
            unanswered_qs = Question.objects.filter(topic=topic).exclude(id__in=user_session.answered_questions.all())

            if unanswered_qs.exists():
                current_q = unanswered_qs.first()
                user_session.answered_questions.add(current_q)

                # ✅ Get answer first
                answer = current_q.answer_yes if msg_text in ["Ndiyo", "yes"] else current_q.answer_no

                # ✅ Always send the answer
                send_whatsapp_message(phone, {
                    "type": "text",
                    "text": {"body": answer}
                })

                # ✅ Then check for follow-up (Yes only)
                if msg_text in ["Ndiyo", "yes"]:
                    # Check if follow-up exists
                    if current_q.follow_up_text and current_q.follow_up_options.exists():
                        rows = [
                            {
                                "id": f"opt_{opt.id}",
                                "title": opt.option_text[:24] #truncate to 24 characters
                                # "description": opt.option_text # optional: show full label here
                            }for opt in current_q.follow_up_options.all()
                        ]

                        list_message = {
                            "type": "interactive",
                            "interactive": {
                                "type": "list",
                                "body": {
                                    "text": current_q.follow_up_text
                                },
                                "action": {
                                    "button": "Chagua",
                                    "sections": [
                                        {
                                            "title": "Chagua",
                                            "rows": rows
                                        }
                                    ]
                                }
                        }
                        }
                        send_whatsapp_message(phone, list_message)
                        return JsonResponse({"status": "follow_up_sent"})

                 # ✅ Continue to next question (regardless of follow-up)
                remaining_qs = unanswered_qs.exclude(id=current_q.id)

                # ✅ 2. Send next question (as interactive)-update to handle nested logic
                # if remaining_qs.exists() and not current_q.follow_up_options.exists(): # I've commented it for a while
                if remaining_qs.exists():
                    next_q = remaining_qs.first()
                    send_whatsapp_message(phone, send_question(next_q))

                elif not current_q.follow_up_options.exists():
                    # Mark topic as finished
                    user_session.finished_topics.add(topic)
                    user_session.save()

                    # Congratulate the user
                    send_whatsapp_message(phone, {
                        "type": "text",
                        "text": {
                            "body": f"🎉 *Hongera!* Umehitimisha mada ya '{topic.name.title()}' kikamilifu. 👏\n\nTuna mada nyingine zinazokungoja kujifunza!"
                        }
                    })

                    # And this function remains for handling change of topics
                    # send_whatsapp_message(phone, prompt_continue_or_switch())#Comment for a while
                    if user_session.has_finished_all_topics():
                        send_whatsapp_message(phone, {
                            "type": "text",
                            "text": {
                                "body": f"🎉 *Hongera!* Umejifunza mada zote zilizopo kwa sasa. 🏁\n\nEndelea kutembelea chatbot yetu kwa maudhui mapya!"
                            }
                        })

                    else:
                        # Suggest choosing another topic (after completing one)
                        send_whatsapp_message(phone, {
                            "type": "text",
                            "text": {
                                "body": f"🙌 *Umehitimisha mada ya '{topic.name.title()}'*.\n\nChagua mada nyingine ili kuendelea kujifunza:"
                            }
                        })
                        send_whatsapp_message(phone, greeting_message(user_session))

                return JsonResponse({"status": "answered"})

            else:
                if user_session.has_finished_all_topics():
                        send_whatsapp_message(phone, {
                            "type": "text",
                            "text": {
                                "body": f"🎉 *Hongera!* Umejifunza mada zote zilizopo kwa sasa. 🏁\n\nEndelea kutembelea chatbot yetu kwa maudhui mapya!"
                            }
                        })

                else:
                        # Suggest choosing another topic (after completing one)
                    send_whatsapp_message(phone, {
                            "type": "text",
                            "text": {
                                "body": f"🙌 *Umehitimisha mada ya '{topic.name.title()}'*.\n\nChagua mada nyingine ili kuendelea kujifunza:"
                            }
                        })
                    send_whatsapp_message(phone, greeting_message(user_session))
            return JsonResponse({"status": "answered"})

        # Handle Continue or Switch
        if msg_text in ["Endelea", "Badilisha Mada", "continue", "switch"]:
            if msg_text in ["Continue", "Endelea"]:
                topic = user_session.current_topic
                user_session.question_index = 0
                user_session.save()
                question = Question.objects.filter(topic=topic).exclude(id__in=user_session.answered_questions.all()).first()
                if question:
                    send_whatsapp_message(phone, send_question(question))

                else:
                    # send_whatsapp_message(phone, prompt_continue_or_switch()) # Comment for a while
                    if user_session.has_finished_all_topics():
                        send_whatsapp_message(phone, {
                            "type": "text",
                            "text": {
                                "body": f"🎉 *Hongera!* Umejifunza mada zote zilizopo kwa sasa. 🏁\n\nEndelea kutembelea chatbot yetu kwa maudhui mapya!"
                            }
                        })

                    else:
                        # Suggest choosing another topic (after completing one)
                        send_whatsapp_message(phone, {
                            "type": "text",
                            "text": {
                                "body": f"🙌 *Umehitimisha mada ya '{topic.name.title()}'*.\n\nChagua mada nyingine ili kuendelea kujifunza:"
                            }
                        })
                        send_whatsapp_message(phone, greeting_message(user_session))

            else:
                send_whatsapp_message(phone, greeting_message(user_session))
            return JsonResponse({"status": "topic handled"})

        # 🧲 Fallback: treat unknown input as greeting, hii itasaidia kama user wa Bot ataandika text ambayo haipo kwa list.
        if msg_text:
            # print("💬 Unrecognized input, treating as greeting.") # For debugging purpose
            send_whatsapp_message(phone, greeting_message(user_session))
            return JsonResponse({"status": "fallback greeting sent"})

    return JsonResponse({"status": "ignored"})

def greeting_message(user_session=None):
    available_topics = Topic.objects.all()
    finished = user_session.finished_topics.all() if user_session else []

    if user_session and available_topics.count() == finished.count():
        return {
            "type": "text",
            "text": {
                "body": "👏 Umehitimisha mada zote tulizonazo kwa sasa! Endelea kutembelea chatbot yetu kwa maudhui mapya hivi karibuni. 😊"
            }
        }



    return {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "header": {
                "type": "text",
                "text": "Karibu ASTeC FinSavvy chatbot-Elimu ya Fedha"
            },
            "body": {"text": "Habari👋, naitwa FinSavvy chatbot. Je, ni mambo gani unataka kujifunza leo?\t\n✅Chagua mada:"},
            "footer": {"text": "Powered by ASTeC ©️2025\nDeveloped by Lungombe"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "akiba", "title": "kuweka akiba"}},
                    {"type": "reply", "reply": {"id": "wekeza", "title": "kuwekeza"}},
                    {"type": "reply", "reply": {"id": "bajeti", "title": "kupangilia bajeti"}}
                ]
            }
        }
    }


def send_question(question):
    return {
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": question.question_text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "yes", "title": "Ndiyo"}},
                    {"type": "reply", "reply": {"id": "no", "title": "Hapana"}}
                ]
            }
        }
    }


# Views for Meta Privacy Policy (Home Page and Privacy Policy)
def home(request):
    return render(request, 'home.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')
