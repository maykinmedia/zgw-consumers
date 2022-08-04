from rest_framework import routers, serializers, viewsets

from .models import Case


# serializers
class CaseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Case
        fields = ("url", "casetype")


# viewsets
class CaseViewSet(viewsets.ModelViewSet):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer


# URL routing
router = routers.DefaultRouter()
router.register("cases", CaseViewSet)
