from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

from django.contrib import admin
from django.core.paginator import EmptyPage, Page, Paginator
from django.db.models import QuerySet
from django.shortcuts import render

from common import utils
from common.admin import BaseAdmin
from common.models import BaseModel

if TYPE_CHECKING:
    from collections.abc import Callable, Iterator

    from django.http import HttpRequest


M = TypeVar("M", bound=BaseModel)


class PaginatedSearchRenderer:
    def __init__(
        self,
        request: HttpRequest,
        model_type: type[M],
        admin_type: type[BaseAdmin],
        table_header: str,
        columns: list[TableColumn],
        template: str = "paginated-search-base.html",
        per_page: int = 15,
    ) -> None:
        self.request = request
        self.table_header = table_header
        self.columns = columns
        self.template = template
        self.per_page = per_page
        self.search_term = request.GET.get("q", "").strip()
        self.page_number = utils.as_int(request.GET.get("page"), 1)
        self.objects = self._get_objects(model_type, admin_type)

    def render(self):
        return render(
            self.request,
            self.template,
            {
                "table_header": self.table_header,
                "search_term": self.search_term,
                "page": self._get_model_page(),
            },
        )

    def _get_objects(
        self,
        model_type: type[M],
        admin_type: type[BaseAdmin],
    ) -> QuerySet[M]:
        if not self.search_term:
            return model_type.objects.all()
        model_admin = admin_type(model_type, admin.site)
        objects, _ = model_admin.get_search_results(
            self.request, model_type.objects, self.search_term
        )
        return objects

    def _get_model_page(self) -> WrappedPage[M]:
        paginator = Paginator(self.objects, per_page=self.per_page)
        page = paginator.get_page(self.page_number)
        try:
            page.adjusted_elided_pages = list(
                paginator.get_elided_page_range(self.page_number)
            )
        except EmptyPage:
            page.adjusted_elided_pages = list(
                paginator.get_elided_page_range(paginator.num_pages)
            )
        return WrappedPage(page, self.columns)


class WrappedPage:
    def __init__(self, page: Page, columns: list[TableColumn]) -> None:
        self.page = page
        self.columns = columns

    @property
    def column_headers(self) -> Iterator[str]:
        return (column.header for column in self.columns)

    def __getattr__(self, key: Any):
        return self.page.__getattribute__(key)

    def __getitem__(self, index: Any) -> WrappedObject:
        return WrappedObject(self.page.__getitem__(index), self.columns)

    def __len__(self) -> int:
        return len(self.page.object_list)


class WrappedObject:
    def __init__(self, obj: BaseModel, columns: list[TableColumn]) -> None:
        self.obj = obj
        self.columns = columns

    def __getitem__(self, index: Any) -> Any:
        return self.columns[index].value_of(self.obj)

    def __len__(self) -> int:
        return len(self.columns)


class TableColumn:
    def __init__(
        self,
        header: str,
        *,
        field: str | None = None,
        builder: Callable[[BaseModel], str]
        | Callable[[BaseModel, dict], str]
        | None = None,
        context: dict | None = None,
    ) -> None:
        self.header = header
        if field is None and builder is None:
            raise ValueError
        self.field = field
        self.builder = builder
        self.context = context

    def with_context(self, context: dict) -> TableColumn:
        return TableColumn(
            self.header, field=self.field, builder=self.builder, context=context
        )

    def with_header(self, header: str) -> TableColumn:
        return TableColumn(
            header, field=self.field, builder=self.builder, context=self.context
        )

    def value_of(self, obj: BaseModel) -> str:
        if self.field:
            return str(getattr(obj, self.field))
        if self.context is None:
            return self.builder(obj)
        return self.builder(obj, self.context)
