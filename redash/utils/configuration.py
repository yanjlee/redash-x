import json
import jsonschema
from jsonschema import ValidationError

SECRET_PLACEHOLDER = '--------'


class ConfigurationContainer(object):
    def __init__(self, config, schema=None):
        self._config = config
        self.set_schema(schema)

    def set_schema(self, schema):
        self._schema = schema

    @property
    def schema(self):
        if self._schema is None:
            raise RuntimeError("Schema missing.")

        return self._schema

    def is_valid(self):
        try:
            self.validate()
        except (ValidationError, ValueError):
            return False

        return True

    def validate(self):
        jsonschema.validate(self._config, self._schema)

    def to_json(self):
        return json.dumps(self._config)

    def iteritems(self):
        return self._config.iteritems()

    def to_dict(self, mask_secrets=False):
        if (mask_secrets is False or 'secret' not in self.schema):
            return self._config

        config = self._config.copy()
        for key in config:
            if key in self.schema['secret']:
                config[key] = SECRET_PLACEHOLDER

        return config

    def update(self, new_config):
        jsonschema.validate(new_config, self.schema)

        config = {}
        for k, v in new_config.iteritems():
            if k in self.schema['secret'] and v == SECRET_PLACEHOLDER:
                config[k] = self[k]
            else:
                config[k] = v

        self._config = config

    def get(self, *args, **kwargs):
        return self._config.get(*args, **kwargs)

    def __getitem__(self, item):
        if item in self._config:
            return self._config[item]

        raise KeyError(item)

    def __contains__(self, item):
        return item in self._config

    @classmethod
    def from_json(cls, config_in_json):
        return cls(json.loads(config_in_json))
