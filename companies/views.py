from rest_framework import generics
from rest_framework.response import Response
from .models import Company
from .serializers import CompanySerializer, CompanySignupSerializer


class CompanySignupView(generics.CreateAPIView):
    serializer_class = CompanySignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()

        return Response({
            "message": "Company created successfully",
            "company_id": result["company"].id,
            "admin_email": result["user"].email
        })


class CompanyListView(generics.ListAPIView):
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.filter(id=self.request.user.company_id)