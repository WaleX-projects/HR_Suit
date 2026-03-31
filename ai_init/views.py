from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .services.ai_agent import run_agent


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_chat(request):
    message = request.data.get("message")

    if not message:
        return Response({"error": "Message is required"}, status=400)

    reply = run_agent(request.user, message)

    return Response({
        "reply": reply
    })