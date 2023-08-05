from plone.schema import _
from zope.interface import Attribute
from zope.interface import implementer
from zope.schema import Field
from zope.schema._bootstrapinterfaces import WrongType
from zope.schema.interfaces import IField
from zope.schema.interfaces import WrongContainedType
from zope.schema.interfaces import IFromUnicode

import json
import jsonschema


DEFAULT_JSON_SCHEMA = json.dumps({
    'type': 'object',
    'properties': {}
})


class IJSONField(IField):
    """A text field that stores A JSON."""

    schema = Attribute(
        "schema",
        _("The JSON schema string serialization.")
    )


@implementer(IJSONField, IFromUnicode)
class JSONField(Field):

    def __init__(self, schema=DEFAULT_JSON_SCHEMA, **kw):
        if not isinstance(schema, str):
            raise WrongType

        try:
            self.json_schema = json.loads(schema)
        except ValueError:
            raise WrongType
        super(JSONField, self).__init__(**kw)

    def _validate(self, value):
        super(JSONField, self)._validate(value)

        try:
            jsonschema.validate(value, self.json_schema)
        except jsonschema.ValidationError as e:
            raise WrongContainedType(e.message, self.__name__)

    def fromUnicode(self, value):
        v = json.loads(value)
        self.validate(v)
        return v
