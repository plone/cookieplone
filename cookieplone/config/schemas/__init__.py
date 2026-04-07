"""JSONSchema definitions for cookieplone configuration formats.

Defines JSON Schemas and validation helpers for:

- **Repository config** (``cookieplone-config.json``): the root file that
  lists available templates, groups, global versions, and optional
  repository extension.
- **Template config** (``cookieplone.json`` v2): the per-template file that
  describes form fields and generator settings.
"""

from cookieplone.config.schemas._types import SubTemplate
from cookieplone.config.schemas._types import TemplateEntry
from cookieplone.config.schemas._types import TemplateGroup
from cookieplone.config.schemas.repository import REPOSITORY_CONFIG_SCHEMA
from cookieplone.config.schemas.repository import validate_repository_config
from cookieplone.config.schemas.template import COOKIEPLONE_CONFIG_SCHEMA
from cookieplone.config.schemas.template import validate_cookieplone_config


__all__ = [
    "COOKIEPLONE_CONFIG_SCHEMA",
    "REPOSITORY_CONFIG_SCHEMA",
    "SubTemplate",
    "TemplateEntry",
    "TemplateGroup",
    "validate_cookieplone_config",
    "validate_repository_config",
]
