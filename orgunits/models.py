"""
Copyright 2020 ООО «Верме»
"""

from django.db import models
from django.db.models.expressions import RawSQL
from django.db.models import Q


class OrganizationQuerySet(models.QuerySet):
    def tree_downwards(self, root_org_id):
        """
        Возвращает корневую организацию с запрашиваемым root_org_id и всех её детей любого уровня вложенности
        TODO: Написать фильтр с помощью ORM или RawSQL запроса или функций Python

        :type root_org_id: int
        """

        finall_children = [root_org_id]
        check_parent = {root_org_id, }
        checked = list()
        while check_parent:
            for parent in check_parent:
                results = self.filter(parent=parent)
                if not results:
                    continue

                for result in results:
                    finall_children.append(result.id)
            checked.extend(check_parent)
            check_parent = set(finall_children) - set(checked)

        return self.filter(id__in=finall_children)

    def tree_upwards(self, child_org_id):
        """
        Возвращает корневую организацию с запрашиваемым child_org_id и всех её родителей любого уровня вложенности
        TODO: Написать фильтр с помощью ORM или RawSQL запроса или функций Python

        :type child_org_id: int
        """

        parent_child_org_id = self.filter(id=child_org_id)[0].parent_id
        finall_parent = [child_org_id, parent_child_org_id]
        check_parent = {parent_child_org_id, }
        checked = [child_org_id]
        while check_parent:
            for parent in check_parent:
                results = self.filter(id=parent)
                if not results:
                    continue

                for result in results:
                    result_parent = result.parent_id
                    if result_parent:
                        finall_parent.append(result_parent)
            checked.extend(check_parent)
            check_parent = set(finall_parent) - set(checked)
        return self.filter(id__in=finall_parent)


class Organization(models.Model):
    """ Организаци """

    objects = OrganizationQuerySet.as_manager()

    name = models.CharField(max_length=1000, blank=False, null=False, verbose_name="Название")
    code = models.CharField(max_length=1000, blank=False, null=False, unique=True, verbose_name="Код")
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, verbose_name="Вышестоящая организация",
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Организация"
        verbose_name = "Организации"

    def __str__(self):
        return self.name

    def parents(self):
        """
        Возвращает всех родителей любого уровня вложенности
        TODO: Написать метод, используя ORM и .tree_upwards()

        :rtype: django.db.models.QuerySet
        """
        id_org = self.get_id()
        res_parents = Organization.objects.tree_upwards(id_org)
        return res_parents.filter(~Q(id=id_org))

    def children(self):
        """
        Возвращает всех детей любого уровня вложенности
        TODO: Написать метод, используя ORM и .tree_downwards()

        :rtype: django.db.models.QuerySet
        """
        id_org = self.get_id()
        res_children = Organization.objects.tree_downwards(id_org)

        return res_children.filter(~Q(id=id_org))

    def get_id(self):
        org = Organization.objects.get(code=self.code)
        return org.id
