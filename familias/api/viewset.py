from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils.text import slugify

from censos.models import Censo
from familias.models import Familia, MetaCensoFamiliar
from familias.api.serializers import FamiliaSerializer
from familias.reportes import datos_familias, generar_excel, generar_pdf


class FamiliaViewSet(ModelViewSet):
    permission_classes=[permissions.IsAuthenticated]
    serializer_class=FamiliaSerializer
    queryset=Familia.objects.prefetch_related('metas_censo').all()

    @action(detail=True, methods=['get'])
    def progreso(self, request, pk=None):
        familia = self.get_object()
        vigencia = request.query_params.get('vigencia', '').strip()
        if not vigencia:
            raise ValidationError({'vigencia': 'Indique la vigencia.'})
        meta = MetaCensoFamiliar.objects.filter(familia=familia, vigencia=vigencia).first()
        censados = Censo.objects.filter(
            vigencia=vigencia, persona__familida_id=familia,
        ).values('persona_id').distinct().count()
        previstos = meta.integrantes_previstos if meta else None
        return Response({
            'familia_id': familia.id,
            'vigencia': vigencia,
            'integrantes_previstos': previstos,
            'censados': censados,
            'restantes': max(previstos - censados, 0) if previstos is not None else None,
            'completo': censados >= previstos if previstos is not None else False,
        })

    @action(detail=False, methods=['get'])
    def reporte(self, request):
        formato = request.query_params.get('formato', '').lower()
        if formato not in ('pdf', 'xlsx'):
            raise ValidationError({'formato': 'Use pdf o xlsx.'})
        vigencia = request.query_params.get('vigencia', '').strip() or None
        datos = datos_familias(vigencia)
        if formato == 'pdf':
            contenido = generar_pdf(datos)
            tipo = 'application/pdf'
        else:
            contenido = generar_excel(datos)
            tipo = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        respuesta = HttpResponse(contenido, content_type=tipo)
        nombre = slugify(vigencia) if vigencia else 'todas'
        respuesta['Content-Disposition'] = f'attachment; filename="familias_{nombre}.{formato}"'
        return respuesta
