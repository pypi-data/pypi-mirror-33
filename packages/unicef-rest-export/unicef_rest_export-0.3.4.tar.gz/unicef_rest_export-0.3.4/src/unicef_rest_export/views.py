from django.conf import settings
from rest_framework.generics import ListAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.settings import perform_import
from rest_framework.viewsets import GenericViewSet

from unicef_rest_export.renderers import ExportBaseRenderer
from unicef_rest_export.serializers import ExportSerializer

DEFAULT_TEMPLATE = False
EXPORT_RENDERERS = getattr(settings, "EXPORT_RENDERERS", None)
if EXPORT_RENDERERS is None:
    EXPORT_RENDERERS = (
        "unicef_rest_export.renderers.ExportCSVRenderer",
        "unicef_rest_export.renderers.ExportJSONRenderer",
        "unicef_rest_export.renderers.ExportOpenXMLRenderer",
        "unicef_rest_export.renderers.ExportExcelRenderer",
        "unicef_rest_export.renderers.ExportPDFRenderer",
    )
    if "unicef_rest_export" in settings.INSTALLED_APPS:
        DEFAULT_TEMPLATE = True
        EXPORT_RENDERERS = (
            "unicef_rest_export.renderers.ExportHTMLRenderer",
        ) + EXPORT_RENDERERS

EXPORT_RENDERERS = perform_import(EXPORT_RENDERERS, "EXPORT_RENDERERS")


class ExportMixin(object):
    export_serializer_class = ExportSerializer

    def with_list_serializer(self, cls):
        meta = getattr(cls, 'Meta', object)
        if getattr(meta, 'list_serializer_class', None):
            return cls

        class SerializerWithListSerializer(cls):
            class Meta(meta):
                list_serializer_class = self.export_serializer_class

        return SerializerWithListSerializer

    def get_serializer_class(self):
        # c.f rest_framework.generics.GenericAPIView
        # (not using super() since this is a mixin class)
        assert self.serializer_class is not None, (
            "'%s' should either include a `serializer_class` attribute, "
            "or override the `get_serializer_class()` method."
            % self.__class__.__name__
        )

        renderer = self.request.accepted_renderer
        if isinstance(renderer, ExportBaseRenderer):
            return self.with_list_serializer(self.serializer_class)
        else:
            return self.serializer_class


class ExportViewBase(ExportMixin):
    renderer_classes = EXPORT_RENDERERS
    pagination_class = None
    if DEFAULT_TEMPLATE:
        template_name = 'rest_export.html'


class ExportView(ExportViewBase, ListAPIView):
    """Export-capable model list view"""
    pass


class ExportViewSet(ExportViewBase, ListModelMixin, GenericViewSet):
    """Export-capable model ViewSet (list only)"""
    pass
