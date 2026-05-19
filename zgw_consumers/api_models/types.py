type JSONPrimitive = str | int | float | None
type JSONValue = JSONPrimitive | JSONObject | list[JSONValue]
type JSONObject = dict[str, JSONValue]
