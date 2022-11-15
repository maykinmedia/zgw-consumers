from django.db.utils import IntegrityError

import pytest

from testapp.models import Case
from zgw_consumers.constants import APITypes
from zgw_consumers.models import Service

pytestmark = pytest.mark.django_db

CASETYPE_API_ROOT = "https://casetype.example.org/api/v1/"


def test_model_create():
    service = Service.objects.create(api_type=APITypes.ztc, api_root=CASETYPE_API_ROOT)
    case = Case.objects.create(casetype=f"{CASETYPE_API_ROOT}casetype/1")

    assert case.pk is not None
    assert case._casetype_api == service
    assert case._casetype_relative == "casetype/1"


def test_model_create_empty():
    case = Case.objects.create(casetype="")

    assert case.pk is not None
    assert case._casetype_api is None
    assert case._casetype_relative is None


def test_model_create_no_base():
    with pytest.raises(ValueError):
        Case.objects.create(casetype=f"{CASETYPE_API_ROOT}casetype/1")


def test_model_create_base_filled_relative_empty():
    service = Service.objects.create(api_type=APITypes.ztc, api_root=CASETYPE_API_ROOT)

    with pytest.raises(IntegrityError) as exc_info:
        Case.objects.create(_casetype_api=service)

    assert (
        "testapp_case__casetype_api_and__casetype_relative_filled"
        in exc_info.value.args[0]
    )


def test_model_create_base_empty_relative_filled():
    with pytest.raises(IntegrityError) as exc_info:
        Case.objects.create(_casetype_relative="casetype/1")

    assert (
        "testapp_case__casetype_api_and__casetype_relative_filled"
        in exc_info.value.args[0]
    )


def test_model_access():
    Service.objects.create(api_type=APITypes.ztc, api_root=CASETYPE_API_ROOT)
    case = Case.objects.create(casetype=f"{CASETYPE_API_ROOT}casetype/1")

    assert case.casetype == "https://casetype.example.org/api/v1/casetype/1"


def test_model_access_empty():
    case = Case.objects.create(casetype=None)

    assert case.casetype is None


def test_queryset_eq():
    Service.objects.create(api_type=APITypes.ztc, api_root=CASETYPE_API_ROOT)
    case1 = Case.objects.create(casetype=f"{CASETYPE_API_ROOT}casetype/1")
    case2 = Case.objects.create(casetype=f"{CASETYPE_API_ROOT}casetype/2")

    qs = Case.objects.filter(casetype=f"{CASETYPE_API_ROOT}casetype/1")

    assert qs.count() == 1
    assert qs.get() == case1


def test_queryset_eq_no_base():
    Case.objects.create()

    qs = Case.objects.filter(casetype=f"{CASETYPE_API_ROOT}casetype/1")

    assert qs.count() == 0


def test_queryset_in():
    Service.objects.create(api_type=APITypes.ztc, api_root=CASETYPE_API_ROOT)
    case1 = Case.objects.create(casetype=f"{CASETYPE_API_ROOT}casetype/1")
    case2 = Case.objects.create(casetype=f"{CASETYPE_API_ROOT}casetype/2")

    qs = Case.objects.filter(
        casetype__in=[
            f"{CASETYPE_API_ROOT}casetype/1",
            f"{CASETYPE_API_ROOT}casetype/3",
        ]
    )

    assert qs.count() == 1
    assert qs.get() == case1


def test_queryset_in_no_base():
    Case.objects.create()

    qs = Case.objects.filter(casetype__in=[f"{CASETYPE_API_ROOT}casetype/1"])

    assert qs.count() == 0


def test_queryset_subquery():
    """
    test that ServiceUrlField can be safely used in subqueries
    """
    service = Service.objects.create(api_type=APITypes.ztc, api_root=CASETYPE_API_ROOT)
    Case.objects.create(casetype=f"{CASETYPE_API_ROOT}casetype/1")

    service_ids = Case.objects.filter(
        casetype=f"{CASETYPE_API_ROOT}casetype/1"
    ).values_list("_casetype_api", flat=True)
    qs = Service.objects.filter(id__in=service_ids)

    assert qs.count() == 1
    assert qs.get() == service
