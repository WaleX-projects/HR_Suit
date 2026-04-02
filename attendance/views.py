from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Attendance, Shift, EmployeeShift, Holiday
from .serializers import AttendanceSerializer, ShiftSerializer, EmployeeShiftSerializer,HolidaySerializer
from .utils import model, read_image, collection,client

from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from employees.models import Employee 

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters

class AttendanceViewSet(viewsets.ModelViewSet):
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    search_fields = [
        "employee__first_name",
        "employee__last_name"
    ]

    filterset_fields = ["status"]

    def get_queryset(self):
        user = self.request.user

        queryset = Attendance.objects.all().order_by("-date")

        # ================= ROLE BASED ACCESS =================
        if user.role in ["company_admin", "hr"]:
            queryset = queryset.filter(employee__company=user.company)
        else:
            queryset = queryset.filter(employee__user=user)

        # ================= EMPLOYEE FILTER =================
        employee_id = self.request.query_params.get("employee_id")
        if employee_id:
            employee_id = employee_id.strip("/")
            queryset = queryset.filter(employee_id=employee_id)

        # ================= DATE FILTER =================
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")

        if start_date:
            queryset = queryset.filter(date__gte=start_date)

        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset
        
class ShiftViewSet(viewsets.ModelViewSet):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]
    queryset = Shift.objects.all()

class EmployeeShiftViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return EmployeeShift.objects.filter(employee__company=self.request.user.company)
        




import uuid
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from employees.models import Employee
from .models import Attendance
from .utils import model, read_image, collection

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    try:
        employee_id = request.data.get("employee_id")
       
        file = request.FILES.get("file")

        if not employee_id or not file:
            return Response({"success": False, "message": "employee_id and file required"}, status=400)

        # -------- validate employee UUID --------
        try:
            employee_uuid = uuid.UUID(str(employee_id))
        except ValueError:
            return Response({"success": False, "message": "Invalid employee_id"}, status=400)

        
        # -------- fetch employee --------
        try:
            employee = Employee.objects.get(id=employee_uuid)
        except Employee.DoesNotExist:
            return Response(
                {"success": False, "message": "Employee not found"},
                status=404
            )
        # -------- image --------
        try:
            img = read_image(file)
        except Exception:
            return Response({"success": False, "message": "Invalid image"}, status=400)

        faces = model.get(img)

        if len(faces) != 1:
            return Response({"success": False, "message": "Exactly one face required"}, status=400)

        embedding = faces[0].embedding.tolist()

        # -------- duplicate check --------
        try:
            results = collection.query(
                query_embeddings=[embedding],
                n_results=1
            )

            if results.get("distances") and results["distances"][0]:
                if results["distances"][0][0] < 0.4:
                    return Response({"success": False, "message": "Face already registered"}, status=409)

        except Exception as e:
            logger.warning(f"Chroma query failed: {str(e)}")

        # -------- save --------
        collection.add(
            ids=[str(employee_uuid)],
            embeddings=[embedding],
            metadatas=[{"employee_id": str(employee_uuid)}]
        )
        employee.face_verified = True
        return Response({"success": True, "message": "Face registered"}, status=201)

    except Exception as e:
        logger.exception(e)
        return Response({"success": False, "error": str(e)}, status=500)  
        
        
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


import uuid
import logging
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from employees.models import Employee
from .models import Attendance
from .utils import model, read_image, collection

logger = logging.getLogger(__name__)


@api_view(["POST"])
@permission_classes([AllowAny])
def recognize(request):
    try:
        file = request.FILES.get("file")

        if not file:
            return Response({"success": False, "message": "Image required"}, status=400)

        # -------- image --------
        try:
            img = read_image(file)
        except Exception:
            return Response({"success": False, "message": "Invalid image"}, status=400)

        faces = model.get(img)

        if len(faces) == 0:
            return Response({"success": False, "message": "No face detected"}, status=400)

        embedding = faces[0].embedding.tolist()

        # -------- search --------
        try:
            results = collection.query(
                query_embeddings=[embedding],
                n_results=1
            )
        except Exception as e:
            logger.exception(e)
            return Response({"success": False, "message": "Face DB error"}, status=500)

        if not results.get("ids") or not results["ids"][0]:
            return Response({"success": False, "message": "No registered faces"}, status=200)

        employee_id = results["ids"][0][0]
        distance = results["distances"][0][0]

        THRESHOLD = 0.6

        if distance > THRESHOLD:
            return Response({
                "success": False,
                "message": "Face not recognized",
                "distance": distance
            }, status=200)

        # -------- UUID safe --------
        try:
            employee_uuid = uuid.UUID(str(employee_id))
        except ValueError:
            return Response({"success": False, "message": "Invalid stored ID"}, status=500)

        employee = Employee.objects.filter(id=employee_uuid).first()

        if not employee:
            return Response({"success": False, "message": "Employee not found"}, status=404)

        # -------- prevent duplicate attendance --------
        today = now().date()

        already_marked = Attendance.objects.filter(
            employee=employee,
            created_at__date=today
        ).exists()

        if already_marked:
            return Response({
                "success": True,
                "status": "already_marked",
                "message": "Already marked today",
                "name": employee.first_name
            }, status=200)

        # -------- mark attendance --------
        Attendance.objects.create(
            employee=employee,
            status="present"
        )

        return Response({
            "success": True,
            "status": "verified",
            "name": employee.first_name,
            "distance": distance
        }, status=200)

    except Exception as e:
        logger.exception(e)
        return Response({"success": False, "error": str(e)}, status=500)
        
        
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Holiday
from .serializers import HolidaySerializer


class HolidayViewSet(viewsets.ModelViewSet):
    serializer_class = HolidaySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # 👑 Super admin → sees everything
        if user.role == "super_admin":
            return Holiday.objects.all().order_by("-date")

        # 🏢 Company users → global + their own
        return Holiday.objects.filter(
            Q(is_global=True) | Q(company=user.company)
        ).order_by("-date")

    def perform_create(self, serializer):
        user = self.request.user
        is_global = serializer.validated_data.get("is_global", False)

        # ❌ Prevent non-super-admin from creating global holidays
        if is_global and user.role != "super_admin":
            raise PermissionDenied("Only super admin can create global holidays")

        # ✅ Save correctly
        if is_global:
            serializer.save(company=None, is_global=True)
        else:
            serializer.save(company=user.company, is_global=False)
        def perform_update(self, serializer):
            instance = self.get_object()
            user = self.request.user
        
            if instance.is_global and user.role != "super_admin":
                raise PermissionDenied("You cannot edit global holidays")
        
            serializer.save()
        
        
        def perform_destroy(self, instance):
            user = self.request.user
        
            if instance.is_global and user.role != "super_admin":
                raise PermissionDenied("You cannot delete global holidays")
        
            instance.delete()    