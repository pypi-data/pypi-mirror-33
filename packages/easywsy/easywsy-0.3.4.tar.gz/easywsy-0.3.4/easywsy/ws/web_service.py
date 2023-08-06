from suds.client import Client
from suds.xsd.sxbasic import Element
from suds import sudsobject
from ..error.ws_error import WSError
from ..check.mixin import ChecksMixin


def _setattrs(obj, attrs, lazy=False):
    """
    Set all attributes named by attrs `key` with value `attrs[key]`
    in the given `obj`. If `lazy` is set, do not override existing values.

    @param attrs: Dictionary of Attributes to Set
    @type  attrs: dict
    @param lazy: Do not set already existent attrs (Default False)
    @type  lazy: bool
    @return: None
    @rtype : NoneType
    @raise e: TypeError if ParamType is not Dict
    """
    if not isinstance(attrs, dict):
        raise TypeError('Attributes Argument should be a Dict')
    for attr_name, attr_value in attrs.items():
        if isinstance(attr_name, str):
            if lazy and hasattr(obj, attr_name):
                continue
            setattr(obj, attr_name, attr_value)
    return


class WebServiceData(object):

    def __init__(self):
        self._all_attrs = lambda: None
        self._temp_attrs = lambda: None

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        all_attrs = dir(self)
        attrs = []
        for attr in all_attrs:
            if not attr.startswith('__'):
                attrs.append(attr)
        attr_names = ''
        for attr in attrs:
            val = getattr(self, attr)
            if type(val).__name__ == 'instance':
                attr_names += '\n' + val.__str__()
            else:
                attr_names += '\n' + attr + ' = ' + str(val)
        return '(WebServiceData){%s\n}' % attr_names


class AuthInstance(object):

    def __init__(self, name):
        self._element_name = name


class WebService(ChecksMixin):

    def __init__(self, url, **kwargs):
        self.ws_url = url
        self.data = WebServiceData()
        _setattrs(self.data, kwargs, lazy=True)
        self.client = Client(self.ws_url)

    def _add_check_branch(self, elem_name, value):
        if isinstance(elem_name, str):
            if isinstance(value, dict):
                return 'object'
            elif isinstance(value, list):
                return 'array'
            else:
                return 'straight'
        else:
            raise Exception('Wrong data format near element `%s`' % elem_name)

    def _add_check_root(self, attrs):
        assert isinstance(attrs, dict) and len(attrs.keys()) == 1, \
            'WS Data should be a Dict with a Single Key'
        assert isinstance(attrs.values()[0], dict), \
            'First WS Data Value should be an Object (Dict)'
        elem = self._add_get_root_element(attrs)
        setattr(self.data._all_attrs, '_cur_root', elem)

    def _add_get_root_element(self, attrs):
        elem_name = attrs.keys()[0]
        schema = self.client.wsdl.schema
        elem = filter(lambda x: x.name == elem_name, schema.children)
        if len(elem) != 1:
            raise WSError(
                self.ws_url,
                message=('Root Element `%s` was not found in the schema' %
                         elem_name))
        return elem[0]

    def _add_get_from_schema(self, compl_name):
        schema = self.client.wsdl.schema
        compl = filter(lambda x: x.name == compl_name,
                       schema.children)
        assert len(compl) == 1, \
            ('The element `%s` was not found under ' +
             'the root element `%s`!') % (compl_name,
                                          self.data._all_attrs._cur_root)
        return compl[0]

    def _add_get_children_element_type(self, elem_name, parent=False):
        if elem_name == self.data._all_attrs._cur_root.name:
            elem = self.data._all_attrs._cur_root
            return elem.type, elem
        else:
            if not isinstance(parent, Element):
                parent = self.data._all_attrs._cur_root
            elem = filter(lambda x: x[0].name == elem_name, parent.children())
            if not elem:
                if not parent.type:
                    raise WSError(
                        self.ws_url,
                        message=('Element `%s` was not found under ' +
                                 'parent element `%s`') % (elem_name,
                                                           parent.name))
                complex_type = parent.type[0]
                compl = self._add_get_from_schema(complex_type)
                elem = filter(lambda x: x[0].name == elem_name,
                              compl.children())

        if not (len(elem) == 1 and len(elem[0]) >= 1 and
                hasattr(elem[0][0], 'type')):
            msg = ('The element `%s` was not found under the root element ' +
                   '`%s`!') % (elem_name, self.data._all_attrs._cur_root)
            raise WSError(self.ws_url, message=msg)
        return elem[0][0].type[0], elem[0][0]

    def _add_check_array_object(self, parent_el, array_obj):
        assert isinstance(array_obj, dict), \
                'Wrong format fot Array of Elements `%s`' % parent_el

    def _add(self, attrs, parent=False, elem_ref=False, all_obj=False):
        obj = parent or self.data
        all_obj = all_obj or self.data._all_attrs
        elem = False
        if not parent:
            self._add_check_root(attrs)
        for elem_name, value in attrs.items():
            item_type = self._add_check_branch(elem_name, value)
            if item_type == 'object':
                elem_type, elem_def = self._add_get_children_element_type(
                    elem_name, parent=elem_ref)
                root_name = self.data._all_attrs._cur_root.name
                if elem_name == root_name:
                    elem = self.client.factory.create(root_name)
                    all_attr_elem = self.client.factory.create(root_name)
                    setattr(all_obj, elem_name, all_attr_elem)
                    new_all_obj = getattr(all_obj, elem_name)
                else:
                    try:
                        elem = getattr(obj, elem_name)
                        new_all_obj = getattr(all_obj, elem_name)
                    except AttributeError:
                        setattr(obj, elem_name,
                                self.client.factory.create(elem_type))
                        setattr(all_obj, elem_name,
                                self.client.factory.create(elem_type))
                        elem = getattr(obj, elem_name)
                        new_all_obj = getattr(all_obj, elem_name)
                self._add(value, parent=elem, elem_ref=elem_def,
                          all_obj=new_all_obj)
                setattr(obj, elem_name, elem)

            elif item_type == 'array':
                elem_type, elem_def = self._add_get_children_element_type(
                    elem_name, parent=elem_ref)
                try:
                    elem = getattr(obj, elem_name)
                    new_all_obj = getattr(all_obj, elem_name)
                except AttributeError:
                    setattr(obj, elem_name, [])
                    elem = getattr(obj, elem_name)
                    setattr(all_obj, elem_name, [])
                    new_all_obj = getattr(all_obj, elem_name)
                for index, array_obj in enumerate(value):
                    self._add_check_array_object(elem_name, array_obj)
                    ref_str = '_array' + str(index) + '_' + elem_name
                    all_ref_str = 'all_array' + str(index) + '_' + elem_name
                    array_compl = self._add_get_from_schema(elem_name)
                    setattr(self.data._all_attrs, ref_str,
                            self.client.factory.create(array_compl.name))
                    setattr(self.data._all_attrs, all_ref_str,
                            self.client.factory.create(array_compl.name))
                    elem_ref = getattr(self.data._all_attrs, ref_str)
                    all_elem_ref = getattr(self.data._all_attrs, all_ref_str)
                    elem.append(self._add(array_obj, parent=elem_ref,
                                          elem_ref=elem_def,
                                          all_obj=all_elem_ref))
                    new_all_obj.append(all_elem_ref)

            elif item_type == 'straight':
                elem = obj
                try:
                    self._add_get_children_element_type(elem_name, elem_ref)
                except WSError:
                    # TODO Log Inexistent element in wsdl
                    pass
                else:
                    setattr(obj, elem_name, value)
                finally:
                    setattr(all_obj, elem_name, value)
        return elem

    def _has_all_attrs(self, elem):
        """
        Recursively check that all attributes and their childs
        exist in the object. Raise an exception if one does not.

        @param elem:  Root tag which contains childs to check existance
        @type  elem:  suds.sudsobject.Object
        @return:  None
        @rtype :  NoneType
        @raise e:  WSError if a required attribute does not exist
        """
        for attr_name, attr_val in elem:
            if isinstance(attr_val, sudsobject.Object):
                self._has_all_attrs(attr_val)
            elif isinstance(attr_val, list):
                for s in attr_val:
                    self._has_all_attrs(s)
            elif attr_val is None:
                raise WSError(
                    self.ws_url,
                    message=('%s\nElement %s should be filled. Check the ' +
                             'complete parent element above this message') % (
                                elem, attr_name))
        return

###############################################################################

    # Public Methods

    def login(self, elem_name, attrs):
        """
        Create a root element used as authentication with the given elem_name.
        Set the attrs given in that new root element.

        @param elem_name: Name of the auth tag
        @type  elem_name: str
        @param attrs: Dictionary of attributes to be set in the auth tag
        @type  attrs: dict
        @return: None
        @rtype : NoneType
        """
        assert isinstance(elem_name, str)
        assert isinstance(attrs, dict)
        self.auth = AuthInstance(elem_name)
        self.auth.attrs = attrs
        return

    def add(self, attrs, no_check=[], parent=False):
        """
        Creates a tree of xml elements with the given dictionary arch.
        The main parameter should be a dict with only one key
        representing the root element.
        The root element key should contain another dict with all the
        Web Service parameters required formatted as below.
        * If the key is an string and its value is a dict or list,
        those will be taken as a new branch of the tree (Tag or Array).
        * In any other way, the values are stored in the parent branch
        * The branches can be nested.
        e.g.:
        attrs = {
            'root_element': {
                'attr1': 'val1',
                'attr2': 'val2',
                'branch1': {
                    'branch_attr1': 'val3',
                    'branch2': {
                        'branch2_attr1': 'val4',
                    },
                    'branch_array': [
                        {
                            'first_array_elem_attr1': 'val5',
                            'first_array_elem_attr2': 'val6',
                        }
                        {
                            'second_array_elem_attr1': 'val7',
                            'second_array_elem_attr2': 'val8',
                        }
                    ],
                }
            }
        }

        A `no_check` parameter could be used to avoid all checks if
        it's set to 'all'.
        Also it could contain a list of fields to avoid checking.

        @param attrs: Dictionary of Attributes to check and add.
        @type  attrs: Dict
        @param no_check: Wheter to omit all checks, some or none.
        @type  no_check: str or list
        @param parent: Object used as parent element in the xml.
        @type  parent: suds.sudsobject.Object
        """
        elem = self._add(attrs, parent=parent)
        try:
            auth_instance = getattr(elem, self.auth._element_name)
            for k, v in self.auth.attrs.items():
                setattr(auth_instance, k, v)
        except AttributeError:
            auth_instance = False
        self._has_all_attrs(elem)
        if no_check != 'all':
            no_check = isinstance(no_check, list) and no_check or []
            if auth_instance:
                no_check += self.auth.attrs.keys()
            all_attr_elem = getattr(self.data._all_attrs, attrs.keys()[0])
            self._checkattrs(elem, all_attr_elem, no_check)
        return elem

    def get(self, attr_names, lazy=False, required=[]):
        """
        Return the value of the requested attributes.
        Raise an exception if the attribute does not exist and
        is not in `required` unless `lazy` is set to True.

        @param attr_names: Name of the attributes to get the values.
        @type  attr_names: list
        @param lazy: Do not raise an exception if the attr does not exist.
        @type  lazy: bool
        @param required: Raise an exception if any of the elements isn't found.
        @type required: list
        @return: Map with key=`attr_name`, val=`attr_value`.
        @rtype : dict
        @raise e: WSError if an attr is required and does not exist.
        """
        attrs = {}
        for attr_name in attr_names:
            try:
                attr = getattr(self.data._all_attrs, attr_name)
            except AttributeError:
                if not lazy and attr_name in required:
                    raise WSError(self.ws_url, attr=attr_name)
                attr = None
            attrs[attr_name] = attr
        return attrs

    def request(self, method_name):
        """
        Send a request to the Web Service calling the function `method_name`
        with the attributes it needs gathered from the object.
        Those attributes should have been added with the `add` method.

        @param method_name: Name of the WebService function to call
        @type  method_name: str
        @return: response
        @rtype : instance (suds XML element)
        @raise e:  WSError if the method is not found in the WS.
        """
        try:
            method = getattr(self.client.service, method_name)
        except AttributeError:
            raise WSError(self.ws_url, method=method_name)

        param_name = method.method.soap.input.body.parts[0].element[0]
        try:
            param_elem = getattr(self.data, param_name)
        except AttributeError:
            msg = ("Error Requesting %s:\n" +
                   "Perhaps you forgot to add the `%s` tag") % \
                   (method_name, param_name)
            raise WSError(self.ws_url, message=msg)

        method_args = [elem[1] for elem in param_elem]
        response = method(*method_args)
        self.last_request = {
            'response': response,
            'method': method_name,
            'args': method_args,
        }
        return response
