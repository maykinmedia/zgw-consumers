from __future__ import annotations

from typing import TypeAlias

JSONPrimitive: TypeAlias = str | int | None | float
JSONValue: TypeAlias = "JSONPrimitive | JSONObject | list[JSONValue]"
JSONObject: TypeAlias = dict[str, JSONValue]
