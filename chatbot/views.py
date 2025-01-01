import logging
logger = logging.getLogger(__name__)
import requests
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decouple import config

class ChatBotView(APIView):
    predefined_answers = {
        
        "what is your purpose": "My purpose is to assist you with your questions and provide information.",
        "can you help me": "Of course! What do you need help with?",
        "what can you do": "I can answer your questions, provide information, and assist with various tasks.",
        "tell me a joke": "Why don't skeletons fight each other? They don't have the guts!",
        "how old are you": "I don't have an age, I'm just a program designed to help you.",
        "where are you from": "I exist in the digital world, so I don't have a physical location.",
        "what is the weather today": "Sorry, I can't check the weather at the moment.",
        "help": "How can I assist you? Please tell me your question.",
        "what all the features this application have": "You can post jobs, apply for jobs, connect with employees and employers, build a resume, add a subscription, and more.",
        "features of this application": "You can post jobs, apply for jobs, connect with employees and employers, build a resume, add a subscription, and more.",
        "you can contact skillhunt admin at skillhuntadmin@gmail.com": "You can contact the Skillhunt admin at skillhuntadmin@gmail.com.",
        "give me an introduction of this application": "You can post a job, apply for a job, connect with employees and employers, build a resume, add a subscription, and more.",
    }

    def post(self, request):
        user_input = request.data.get("message", "").lower()  # Normalize to lowercase
        GEMINI_API_KEY = config("GEMINI_API_KEY")
        
        logger.info(f"User Input: {user_input}")
        logger.info(f"API Key: {GEMINI_API_KEY}")

        # Check if the user input matches one of the predefined answers
        reply = self.predefined_answers.get(user_input, None)
        
        if reply:
            # If a predefined answer exists, use it
            logger.info(f"Predefined answer found: {reply}")
        else:
            try:
                # Otherwise, call the Gemini API
                response = requests.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
                    json={
                        "contents": [{
                            "parts": [{"text": user_input}]
                        }]
                    },
                    headers={"Content-Type": "application/json"}
                )
                logger.info(f"API Response Status: {response.status_code}")
                logger.info(f"API Response Body: {response.text}")

                response.raise_for_status()
                response_data = response.json()

                # Extract the reply from the API response
                reply = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Sorry, I couldn't process your request.")
            except requests.exceptions.RequestException as e:
                logger.error(f"RequestException: {e}")
                reply = "Error connecting to the Gemini API."
            except Exception as e:
                logger.error(f"Unexpected Error: {e}")
                reply = "An unexpected error occurred."

        return Response({"response": reply}, status=status.HTTP_200_OK)


