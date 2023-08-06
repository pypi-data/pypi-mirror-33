from .expressions import Value
from ..exceptions import BuilderError

def get_param_store(paramstyle):
    if paramstyle == "qmark":
        return QmarkParamStore()
    elif paramstyle == "numeric":
        return NumericParamStore()
    elif paramstyle == "named":
        return NamedParamStore()
    elif paramstyle == "format":
        return FormatParamStore()
    elif paramstyle == "pyformat":
        return PyformatParamStore()

class ParamStore(object):
    """A storage mechanism for query parameters.
    
    Using subclasses of this, query parameters can be stored,
    retrieved, and re-assigned allowing for re-use of a fully-built
    SQL statement by changing the parameter values.
    """
    
    def __init__(self):
        self._params = {}
        self._all_params = []
    
    def add_param(self, param):
        if param._param_name is None:
            param_name = self._make_param_name(param)
        else:
            param_name = param._param_name
        
        if param_name not in self._params:
            self._params[param_name] = param
        elif id(param) != id(self._params[param_name]):
            message = "Duplicate parameter added to query"
            if param._param_name is not None:
                message += ": " + param._param_name
            raise BuilderError(message)
        
        self._all_params.append(param)
        return param_name
    
    def add_params(self, params):
        for param in params:
            self.add_param(param)
    
    def get_all_params(self):
        return self._all_params[:]
    
    def get_dbapi_params(self):
        raise NotImplementedError()
    
    def get_param_marker(self, value):
        raise NotImplementedError()
    
    def get_param_value(self, key):
        return self._find_param(key).get_value()
    
    def set_param_value(self, key, value):
        self._find_param(key).set_value(value)
        return value
    
    def _find_param(self, key):
        return self._params[key]
    
    def _make_param_name(self, param):
        return str(id(param))

class OrderedParamStore(ParamStore):
    def get_dbapi_params(self):
        return [param.get_value() for param in self._all_params]

class NumberedParamStore(ParamStore):
    def __init__(self):
        super().__init__()
        self._ordered_params = []
        self._param_to_index = {}
    
    def add_param(self, param):
        param_name = super().add_param(param)
        if param_name not in self._param_to_index:
            self._ordered_params.append(param)
            # These seem to be 1-indexed from PEP 249, though I've
            # never actually used a numeric paramstyle module.
            self._param_to_index[param_name] = len(self._ordered_params)
    
    def get_dbapi_params(self):
        [param.get_value() for param in self._ordered_params]

class MappedParamStore(ParamStore):
    def add_param(self, param):
        param_name = super().add_param(param)
        if param._param_name is None:
            param._param_name = param_name
        return param_name
    
    def get_dbapi_params(self):
        return {key: param.get_value() for key, param in self._params.items()}

class QmarkParamStore(OrderedParamStore):
    def get_param_marker(self, value):
        return "?"

class NumericParamStore(NumberedParamStore):
    def get_param_marker(self, value):
        if value._param_name is None:
            param_name = self._make_param_name(param)
        else:
            param_name = value._param_name
        return ":{}".format(self._param_to_index[param_name])

class NamedParamStore(MappedParamStore):
    def get_param_marker(self, value):
        return ":{}".format(value._param_name)

class FormatParamStore(OrderedParamStore):
    def get_param_marker(self, value):
        return "%s"

class PyformatParamStore(MappedParamStore):
    def get_param_marker(self, value):
        return "%({})s".format(value._param_name)
