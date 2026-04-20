# settings/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from .models import CompanySettings
from .serializers import CompanySettingsSerializer

class CompanySettingsView(generics.RetrieveUpdateAPIView):
    queryset = CompanySettings.objects.all()
    serializer_class = CompanySettingsSerializer

    def get_object(self):
        # Always return the first (and only) settings object
        obj, created = CompanySettings.objects.get_or_create()
        return obj

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)