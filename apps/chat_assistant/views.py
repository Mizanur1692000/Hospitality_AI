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
        context = request.POST.get("context")

        # Session-backed chat memory (lightweight, per user/browser).
        # Stored as a list of {"role": "user"|"assistant", "content": "..."}.
        history = request.session.get("chat_history", [])
        if not isinstance(history, list):
            history = []

        response = chat_with_gpt(user_input, context, history=history)

        # Update history (bound size to prevent session bloat).
        if isinstance(user_input, str) and user_input.strip():
            history.append({"role": "user", "content": user_input.strip()})
        if isinstance(response, str) and response.strip():
            history.append({"role": "assistant", "content": response.strip()})
        history = history[-20:]
        request.session["chat_history"] = history

        return JsonResponse({"response": response})
    return JsonResponse({"error": "Invalid request"}, status=400)
