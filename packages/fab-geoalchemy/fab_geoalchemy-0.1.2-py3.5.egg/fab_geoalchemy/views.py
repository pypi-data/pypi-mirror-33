from flask_appbuilder.views import ModelView
from flask_appbuilder.forms import GeneralModelConverter, FieldConverter
from .widgets import LatLonWidget
from .fields import GeometryField, PointField
from wtforms import validators
from flask_appbuilder.validators import Unique
from flask_appbuilder.fields import EnumField
from flask_appbuilder.fieldwidgets import Select2Widget
from flask_appbuilder.forms import DynamicForm
from shapely import wkb
import logging

log = logging.getLogger(__name__)


class GeoFieldConverter(FieldConverter):
    conversion_table = tuple(
        [('is_point', PointField, LatLonWidget)] +
        list(FieldConverter.conversion_table))

    def convert(self):
        # sqlalchemy.types.Enum inherits from String, therefore `is_enum` must
        # be checked before checking for `is_string`:
        col = self.datamodel.list_columns[self.colname]
        if getattr(self.datamodel, 'is_enum')(self.colname):
            col_type = col.type
            return EnumField(enum_class=col_type.enum_class,
                             enums=col_type.enums,
                             label=self.label,
                             description=self.description,
                             validators=self.validators,
                             widget=Select2Widget(),
                             default=self.default)
        for type_marker, field, widget in self.conversion_table:
            if getattr(self.datamodel, type_marker)(self.colname):
                log.debug("Converting {}".format(self.colname))
                if widget:
                    if issubclass(field, GeometryField):
                        log.debug("We've got a GeometryField")
                        return field(self.label,
                                     srid=col.type.srid,
                                     description=self.description,
                                     validators=self.validators,
                                     widget=widget(),
                                     default=self.default)
                    else:
                        return field(self.label,
                                     description=self.description,
                                     validators=self.validators,
                                     widget=widget(),
                                     default=self.default)
                else:
                    return field(self.label,
                                 description=self.description,
                                 validators=self.validators,
                                 default=self.default)
        log.error('Column %s Type not supported' % self.colname)


class GeoModelConverter(GeneralModelConverter):
    def __init__(self, *args, **kwargs):
        log.debug('Instantiating GeoModelConverter')
        super(GeoModelConverter, self).__init__(*args, **kwargs)

    def _convert_simple(self, col_name, label, description, lst_validators,
                        form_props):
        log.debug('Using GeoModelConverter _convert_simple')
        # Add Validator size
        max = self.datamodel.get_max_length(col_name)
        min = self.datamodel.get_min_length(col_name)
        if max != -1 or min != -1:
            lst_validators.append(validators.Length(max=max, min=min))
        # Add Validator is null
        if not self.datamodel.is_nullable(col_name):
            lst_validators.append(validators.InputRequired())
        else:
            lst_validators.append(validators.Optional())
        # Add Validator is unique
        if self.datamodel.is_unique(col_name):
            lst_validators.append(Unique(self.datamodel, col_name))
        default_value = self.datamodel.get_col_default(col_name)
        fc = GeoFieldConverter(self.datamodel, col_name, label, description,
                               lst_validators, default=default_value)
        form_props[col_name] = fc.convert()
        log.debug("Form_props: {}".format(form_props[col_name]))
        return form_props

#     def create_form(self, label_columns=None, inc_columns=None,
                    # description_columns=None, validators_columns=None,
                    # extra_fields=None, filter_rel_fields=None):
        # """
            # Converts a model to a form given
            # :param label_columns:
                # A dictionary with the column's labels.
            # :param inc_columns:
                # A list with the columns to include
            # :param description_columns:
                # A dictionary with a description for cols.
            # :param validators_columns:
                # A dictionary with WTForms validators ex::
                    # validators={'personal_email':EmailValidator}
            # :param extra_fields:
                # A dictionary containing column names and a WTForm
                # Form fields to be added to the form, these fields do not
                 # exist on the model itself ex::
                    # extra_fields={'some_col':BooleanField('Some Col',
                                                          # default=False)}
            # :param filter_rel_fields:
                # A filter to be applied on relationships
        # """
        # label_columns = label_columns or {}
        # inc_columns = inc_columns or []
        # description_columns = description_columns or {}
        # validators_columns = validators_columns or {}
        # extra_fields = extra_fields or {}
        # form_props = {}
        # for col_name in inc_columns:
            # if col_name in extra_fields:
                # form_props[col_name] = extra_fields.get(col_name)
            # else:
                # self._convert_col(col_name,
                                  # self._get_label(col_name, label_columns),
                                  # self._get_description(col_name,
                                                        # description_columns),
                                  # self._get_validators(col_name,
                                                       # validators_columns),
                                  # filter_rel_fields, form_props)
        # return type('GeoDynamicForm', (GeoDynamicForm,), form_props)


# class GeoDynamicForm(DynamicForm):
    # """
        # Refresh method will force select field to refresh
    # """

    # @classmethod
    # def refresh(self, obj=None):
        # data = {}
        # log.debug("Refreshing form {} with attributes {}".format(self,
                                                                 # dir(self)))
        # return super().refresh(obj=obj)
        # for field in self():
            # if hasattr(obj, field.name):
                # val = getattr(obj, field.name)
                # if isinstance(field, PointField):
                    # log.debug("Got a point field {}: {}".format(field.name,
                                                                # val))
                    # lonname = '{}_lon'.format(field.name)
                    # latname = '{}_lat'.format(field.name)
                    # if val is not None:
                        # geom = wkb.loads(bytes(val.data))
                        # x = geom.x
                        # y = geom.y
                    # else:
                        # x, y = None, None
                    # data[lonname] = x
                    # data[latname] = y
                # else:
                    # data[field.name] = val
        # log.debug('Form with data: {}'.format(data))
        # form = self(data=data)
        # return form


class GeoModelView(ModelView):

    def _init_forms(self):
        log.debug('Calling _init_forms')
        conv = GeoModelConverter(self.datamodel)
        if not self.search_form:
            log.debug("Getting search form")
            self.search_form = conv.create_form(
                self.label_columns,
                self.search_columns,
                extra_fields=self.search_form_extra_fields,
                filter_rel_fields=self.search_form_query_rel_fields)
        if not self.add_form:
            log.debug("Getting add form")
            self.add_form = conv.create_form(
                self.label_columns,
                self.add_columns,
                self.description_columns,
                self.validators_columns,
                self.add_form_extra_fields,
                self.add_form_query_rel_fields)
        if not self.edit_form:
            log.debug("Getting edit form")
            self.edit_form = conv.create_form(self.label_columns,
                                              self.edit_columns,
                                              self.description_columns,
                                              self.validators_columns,
                                              self.edit_form_extra_fields,
                                              self.edit_form_query_rel_fields)
        # super(GeoModelView, self)._init_forms()
