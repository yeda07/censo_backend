from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.http import HttpResponse
from django.utils.text import slugify

from censos.models import Censo
from censos.api.serializers import CensoSerializer
from censos.reportes import datos_censos, generar_excel, generar_pdf
from censo_actividades.models import CensoActividad
from censo_actividades.services import actualizar_actividades_vencidas


class CensoViewSet(ModelViewSet):
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=CensoSerializer
    queryset=Censo.objects.all()

    @action(detail=False, methods=['get'])
    def reporte(self, request):
        formato = request.query_params.get('formato', '').lower()
        if formato not in ('pdf', 'xlsx'):
            raise ValidationError({'formato': 'Use pdf o xlsx.'})
        vigencia = request.query_params.get('vigencia', '').strip() or None
        censos = datos_censos(vigencia)
        if formato == 'pdf':
            contenido = generar_pdf(censos, vigencia)
            tipo = 'application/pdf'
        else:
            contenido = generar_excel(censos, vigencia)
            tipo = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        respuesta = HttpResponse(contenido, content_type=tipo)
        nombre = slugify(vigencia) if vigencia else 'todas'
        respuesta['Content-Disposition'] = f'attachment; filename="censo_poblacional_{nombre}.{formato}"'
        return respuesta

    @action(detail=True, methods=['get'], url_path='paz-y-salvo')
    def paz_y_salvo(self, request, pk=None):
        censo = self.get_object()
        actualizar_actividades_vencidas(censo_id=censo.id)
        sin_realizar = CensoActividad.objects.filter(censo=censo).exclude(
            estado=CensoActividad.TERMINADA
        ).select_related('actividad')
        return Response({
            'habilitado': not sin_realizar.exists(),
            'actividades': [
                {
                    'id': item.id,
                    'descripcion': item.actividad.descripcion if item.actividad else 'Actividad sin definir',
                    'estado': item.get_estado_display(),
                }
                for item in sin_realizar
            ],
        })
