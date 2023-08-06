from rest_framework import routers


class RestRouter(routers.DefaultRouter):
    def get_default_base_name(self, viewset):
        """
        If `base_name` is not specified, attempt to automatically determine
        it from the viewset.
        """
        queryset = getattr(viewset, 'queryset', None)

        assert queryset is not None, '`base_name` argument not specified, and could ' \
            'not automatically determine the name from the viewset, as ' \
            'it does not have a `.queryset` attribute.'

        return queryset.model._meta.label_lower
