from importlib import reload

import pytest

from zgw_consumers import settings as zgw_settings
from zgw_consumers.constants import NLXDirectories
from zgw_consumers.models import NLXConfig


def _reload_settings():
    reload(zgw_settings)


@pytest.mark.django_db
def test_demo_directory_url_overridden_by_envvar(monkeypatch):
    custom_demo = "https://demo.custom.nlx.example/"
    monkeypatch.setenv("NLX_DIRECTORY_URL_DEMO", custom_demo)
    _reload_settings()
    config = NLXConfig.get_solo()
    config.directory = NLXDirectories.demo
    url = config.directory_url
    assert url == custom_demo


@pytest.mark.django_db
def test_prod_directory_url_default(monkeypatch):
    monkeypatch.delenv("NLX_DIRECTORY_URL_PROD", raising=False)
    _reload_settings()
    config = NLXConfig.get_solo()
    config.directory = NLXDirectories.prod
    url = config.directory_url
    assert url == "https://nlx-directory-ui.commonground.utrecht.nl/"


@pytest.mark.django_db
def test_prod_directory_url_overridden_by_envvar(monkeypatch):
    custom_prod = "https://prod.custom.nlx.example/"
    monkeypatch.setenv("NLX_DIRECTORY_URL_PROD", custom_prod)
    _reload_settings()
    config = NLXConfig.get_solo()
    config.directory = NLXDirectories.prod
    url = config.directory_url
    assert url == custom_prod
