"""
Copyright 2020 ООО «Верме»
"""

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from orgunits.api_v1.serializers import OrganizationSerializer
from orgunits.models import Organization
from wfm.views import TokenAuthMixin


class OrganizationViewSet(TokenAuthMixin, ModelViewSet):
    serializer_class = OrganizationSerializer
    queryset = Organization.objects.all()

    @action(methods=["GET"], detail=True)
    def parents(self, request, *args, **kwargs):
        """
        Возвращает родителей запрашиваемой организации
        TODO: Написать два действия для ViewSet (parents и children), используя методы модели
        """
        parents = list()
        response_data = list()
        if 'pk' in kwargs:
            org = self.queryset.get(id=kwargs['pk'])
            parents = org.parents()

        if parents:
            for parent in parents:
                data = dict()
                for key in self.serializer_class.Meta.fields:
                    data[key] = getattr(parent, key)

                response_data.append(data)

        return Response(response_data)

    @action(methods=["GET"], detail=True)
    def children(self, request, *args, **kwargs):
        children = list()
        response_data = list()
        if 'pk' in kwargs:
            org = self.queryset.get(id=kwargs['pk'])
            children = org.children()

        if children:
            for child in children:
                data = dict()
                for key in self.serializer_class.Meta.fields:
                    if key == 'parent':
                        data[key] = child.parent_id
                    else:
                        data[key] = getattr(child, key)

                response_data.append(data)

        return Response(response_data)
