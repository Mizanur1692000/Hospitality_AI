# chat_assistant/views.py
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json

from .openai_utils import chat_with_gpt


def chat_ui(request):
    return render(request, "chat_assistant/chat_ui.html")


@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        user_input = request.POST.get("message")
        response = chat_with_gpt(user_input)
        return JsonResponse({"response": response})
    return JsonResponse({"error": "Invalid request"}, status=400)
