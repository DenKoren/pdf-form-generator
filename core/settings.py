from typing import List, Optional, Dict, Union, BinaryIO, TextIO, AnyStr, Any

import yaml


class FormField:
    def __init__(self,
                 name: Optional[str] = None,
                 x: Optional[float] = None,
                 y: Optional[float] = None,
                 w: Optional[float] = None,
                 h: Optional[float] = None,
                 tooltip: Optional[str] = None,
                 flags: Optional[List] = None,
                 maxlen: Optional[int] = None,
                 font_size: Optional[int] = None,
                 font_name: Optional[str] = None,
                 border_width: Optional[float] = None,
                 field_type: Optional['FormField'] = None):
        self._name: Optional[str] = name
        self._x: Optional[float] = x
        self._y: Optional[float] = y
        self._w: Optional[float] = w
        self._h: Optional[float] = h
        self._tooltip: Optional[str] = tooltip
        self._flags: Optional[List] = flags
        self._maxlen: Optional[int] = maxlen
        self._font_size: Optional[int] = font_size
        self._font_name: Optional[str] = font_name
        self._border_width: Optional[float] = border_width
        self._field_type: Optional['FormField'] = field_type

    def _get_property(self, prop_name, default_val: Any) -> Any:
        my_prop_val = getattr(self, f"_{prop_name}")
        if my_prop_val is not None:
            return my_prop_val

        if self._field_type is None:
            return default_val

        def_prop_val = getattr(self._field_type, prop_name)
        if def_prop_val is not None:
            return def_prop_val

        return default_val

    @property
    def name(self) -> str:
        return self._get_property('name', '')

    @property
    def x(self) -> float:
        return self._get_property('x', 0.0)

    @property
    def y(self) -> float:
        return self._get_property('y', 0.0)

    @property
    def w(self) -> float:
        return self._get_property('w', 0.0)

    @property
    def h(self) -> float:
        return self._get_property('h', 0.0)

    @property
    def tooltip(self) -> str:
        return self._get_property('tooltip', 0.0)

    @property
    def flags(self) -> Optional[List]:
        return self._get_property('flags', None)

    @property
    def maxlen(self) -> int:
        return self._get_property('maxlen', 0)

    @property
    def font_size(self) -> int:
        return self._get_property('font_size', 0)

    @property
    def font_name(self) -> str:
        return self._get_property('font_name', '')

    @property
    def border_width(self) -> Optional[float]:
        return self._get_property('border_width', None)

    @property
    def field_type(self) -> Optional['FormField']:
        return self._field_type


class FormGroup:
    def __init__(self, fields: Optional[List[FormField]] = None):
        if fields is None:
            fields = []

        self._fields: List[FormField] = fields

    def add_fields(self, *fields: FormField) -> 'FormGroup':
        self._fields += fields
        return self

    def _expand_field(self,
                      field: FormField,
                      name: str = '',
                      x: float = 0.0,
                      y: float = 0.0):

        new_name = f"{name}-{field.name}"
        new_x: float = x + field.x
        new_y: float = y + field.y

        return FormField(
            name=new_name,
            x=new_x,
            y=new_y,
            w=field.w,
            h=field.h,
            tooltip=field.tooltip,
            flags=field.flags,
            maxlen=field.maxlen,
            font_size=field.font_size,
            field_type=field.field_type,
        )

    def expand(self,
               name: str = '',
               x: float = 0.0,
               y: float = 0.0) -> List[FormField]:
        fields_list: List[FormField] = []
        for field in self._fields:
            fields_list.append(
                self._expand_field(field=field,
                                   name=name,
                                   x=x,
                                   y=y)
            )

        return fields_list


class FormSettings:
    def __init__(self, settings: Dict):
        self._raw_settings = settings

        self._field_types: Dict[str, FormField] = self._parse_field_types(settings)
        self._field_groups: Dict[str, FormGroup] = self._parse_field_groups(settings)
        self._forms: Dict[str, List[List[FormField]]] = self._parse_forms(settings)

    @staticmethod
    def from_stream(yaml_data: Union[BinaryIO, TextIO]) -> 'FormSettings':
        data: Dict = yaml.safe_load(yaml_data)
        return FormSettings(data.get('form_settings', {}))

    @staticmethod
    def from_file(yaml_file_path: AnyStr) -> 'FormSettings':
        with open(yaml_file_path, 'rb') as f:
            return FormSettings.from_stream(f)

    @staticmethod
    def _parse_field_types(_raw_settings: Dict) -> Dict[str, FormField]:
        field_types: Dict[str, Dict] = _raw_settings.get('types', {})
        parsed_field_types: Dict[str, FormField] = {}

        default_type_settings = field_types.get('default', {})
        parsed_field_types['default'] = FormField(**default_type_settings)

        def _init_type(type_name: str, type_settings: Dict):
            if type_name in parsed_field_types:
                # Don't init the same field type twice
                return

            parent_type_name = type_settings.get('type', 'default')

            parent_type: Optional[FormField] = parsed_field_types.get(parent_type_name, None)
            if parent_type is None:
                _init_type(parent_type_name, field_types[parent_type_name])
                parent_type = parsed_field_types[parent_type_name]

            type_settings.pop('type', None)
            parsed_field_types[type_name] = FormField(**type_settings, field_type=parent_type)

        for t_name, t_settings in field_types.items():
            _init_type(t_name, t_settings)

        return parsed_field_types

    def _expand_field(self, field_settings: Dict):
        type_name = field_settings.get('type', 'default')
        field_settings.pop('type', None)

        field_type: FormField = self._field_types[type_name]
        return FormField(**field_settings, field_type=field_type)

    def _expand_group(self, group_settings: Dict) -> List[FormField]:
        group_name: str = group_settings['group']
        group_settings.pop('group', None)

        group: FormGroup = self._field_groups[group_name]
        return group.expand(**group_settings)

    def _parse_field_groups(self, raw_settings: Dict) -> Dict[str, FormGroup]:
        field_groups: Dict[str, List[Dict]] = raw_settings.get('groups', {})
        parsed_field_groups: Dict[str, FormGroup] = {}

        def _init_group(group_name: str, group_settings: List[Dict]):
            group: FormGroup = FormGroup()

            for field_settings in group_settings:
                child_group_name: str = field_settings.get('group', '')
                is_group = child_group_name != ''

                if is_group:
                    child_group: Optional[FormGroup] = parsed_field_groups.get(child_group_name)
                    if child_group is None:
                        _init_group(child_group_name, field_groups[child_group_name])
                        child_group = parsed_field_groups[child_group_name]

                    field_settings.pop('group', None)
                    group.add_fields(*child_group.expand(**field_settings))

                else:
                    field = self._expand_field(field_settings=field_settings)
                    group.add_fields(field)

            parsed_field_groups[group_name] = group

        for gr_name, gr_settings in field_groups.items():
            _init_group(gr_name, gr_settings)

        return parsed_field_groups

    def _parse_page(self, page_settings: List[Dict]) -> List[FormField]:
        parsed_page_settings: List[FormField] = []

        for field_settings in page_settings:
            group_name: str = field_settings.get('group', '')
            if group_name != '':
                parsed_page_settings += self._expand_group(field_settings)

            else:
                parsed_page_settings += [self._expand_field(field_settings)]

        return parsed_page_settings

    def _parse_forms(self, raw_settings: Dict) -> Dict[str, List[List[FormField]]]:
        forms: Dict[str, List[List[Dict]]] = raw_settings.get('forms', {})

        parsed_forms: Dict[str, List[List[FormField]]] = {}

        for form_name, form_settings in forms.items():
            parsed_form_settings: List[List[FormField]] = []

            for page in form_settings:
                parsed_form_settings.append(
                    self._parse_page(page)
                )

            parsed_forms[form_name] = parsed_form_settings

        return parsed_forms

    def field_types(self) -> Dict[str, FormField]:
        return self._field_types

    def add_field_type(self, type_name: str, field_type: Optional[FormField]) -> 'FormSettings':
        if field_type is None:
            self._field_types.pop(type_name, None)
        else:
            self._field_types[type_name] = field_type

        return self

    def del_field_type(self, type_name: str) -> 'FormSettings':
        return self.add_field_type(type_name, None)

    def field_groups(self) -> Dict[str, FormGroup]:
        return self._field_groups

    def add_field_group(self, group_name: str, group: Optional[FormGroup]) -> 'FormSettings':
        if group is None:
            self._field_groups.pop(group_name, None)
        else:
            self._field_groups[group_name] = group

        return self

    def del_field_group(self, group_name: str) -> 'FormSettings':
        return self.add_field_group(group_name, None)

    def form(self, form_name: str) -> List[List[FormField]]:
        return self._forms[form_name]


class FieldValues:
    def __init__(self, data: Dict[str, Any]):
        self.data: Dict[str, Any] = data

    @staticmethod
    def from_stream(yaml_data: Union[BinaryIO, TextIO]) -> 'FieldValues':
        data: Dict = yaml.safe_load(yaml_data)
        return FieldValues(data.get('field_values', {}))

    @staticmethod
    def from_file(yaml_file_path: AnyStr) -> 'FieldValues':
        with open(yaml_file_path, 'rb') as f:
            return FieldValues.from_stream(f)

