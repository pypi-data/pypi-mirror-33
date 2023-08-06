from suds import sudsobject
from ..error.check_error import CheckError


_check_attr_method_map = {
}


class ChecksMixin(object):

    def _checkattrs(self, elem, all_attr_elem, no_check=[], call_dict=False,
                    first=True):
        """
        Call check methods mapped to attrs `key` and raise if those fail.

        @param elem: Main element to check.
        @type  elem: suds.sudsobject.Object
        @param no_check: (Optional) Fields to avoid checking
        @type  no_check: list
        @return: None
        @rtype : NoneType
        @raise e: CheckError (Either Method was not found, or it failed)
        """
        all_attrs_parent = all_attr_elem or self.data._all_attrs
        if first:
            call_dict = {}
        for attr_name, attr_value in elem:
            if hasattr(self, 'auth') and attr_name == self.auth._element_name:
                continue
            if isinstance(attr_value, sudsobject.Object):
                all_attrs_value = getattr(all_attrs_parent, attr_name)
                self._checkattrs(attr_value, all_attrs_value,
                                 no_check=no_check, call_dict=call_dict,
                                 first=False)
            elif isinstance(attr_value, list):
                for i, s in enumerate(attr_value):
                    all_ref_str = 'all_array' + str(i) + '_' + attr_name
                    all_attrs_value = getattr(self.data._all_attrs,
                                              all_ref_str)
                    self._checkattrs(s, all_attrs_value, no_check=no_check,
                                     call_dict=call_dict, first=False)
            else:
                if attr_name in no_check:
                    continue
                if attr_name not in _check_attr_method_map:
                    raise CheckError(attr=attr_name, not_found=True)
                methodins = _check_attr_method_map[attr_name][0]
                param_names = _check_attr_method_map[attr_name][1]
                args = param_names[0]
                kwargs = param_names[1]
                sequence = _check_attr_method_map[attr_name][2]
                if len(args) < 1:
                    msg = ("Method `%s` should expect a positional " +
                           "Value to check at least.\n" +
                           "Received `%s` instead. (*args, **kwargs)") % \
                           (methodins.func.func_name, param_names)
                    raise CheckError(message=msg)
                p_args = []
                kw_args = {}
                for p_name in args[1:]:
                    try:
                        p_val = getattr(all_attr_elem, p_name)
                    except AttributeError:
                        msg = ("Custom Parameter `%s` was not found in: " +
                               "\n%s\n for method `%s`") % \
                              (p_name, all_attr_elem, methodins.func.func_name)
                        raise CheckError(message=msg)
                    p_args.append(p_val)
                for p_name in kwargs:
                    try:
                        p_val = getattr(all_attr_elem, p_name)
                        kw_args[p_name] = p_val
                    except AttributeError:
                        pass
                if sequence in call_dict:
                    call_dict[sequence].append({
                        'method': methodins,
                        'args': [attr_value] + p_args,
                        'kwargs': kw_args,
                        'attr_name': attr_name,
                    })
                else:
                    call_dict[sequence] = [{
                        'method': methodins,
                        'args': [attr_value] + p_args,
                        'kwargs': kw_args,
                        'attr_name': attr_name,
                    }]
        if first:
            for sequence, calls in call_dict.items():
                for call_data in calls:
                    method = call_data['method']
                    try:
                        res = method(*call_data['args'],
                                     **call_data['kwargs'])
                    except Exception:
                        if method.reraise:
                            raise
                        raise CheckError(attr=call_data['attr_name'],
                                         method=method.func.func_name,
                                         value=call_data['args'][0])
                    else:
                        if not res:
                            raise CheckError(attr=call_data['attr_name'],
                                             method=method.func.func_name,
                                             value=call_data['args'][0])
        return

    _check_attr_method_map = _check_attr_method_map
