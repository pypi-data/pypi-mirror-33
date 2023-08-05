from wtforms.fields import Field
from wtforms.utils import unset_value
from .widgets import LatLonWidget
import logging

log = logging.getLogger(__name__)


class GeometryField(Field):
    pass


class PointField(GeometryField):
    widget = LatLonWidget()

    def __init__(self, *args, srid=4326, **kwargs):
        self.srid = srid
        super(PointField, self).__init__(*args, **kwargs)

    def _getpoint(self, lat, lon):
        point = "SRID={srid};POINT({lon} {lat})".format(
            lat=lat, lon=lon, srid=self.srid)
        log.debug("returning point for {lat}, {lon}: {point}".format(
            lat=lat, lon=lon, point=point))
        return point

    def process(self, formdata, data=unset_value):
        latname = self.name+'_lat'
        lonname = self.name+'_lon'
        self.process_errors = []
        log.debug("Processing field with data: {} and formdata: {}".format(
            data, formdata))
        if data is unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default
        else:
            if lonname in data and latname in data:
                data[self.name] = self._getpoint(data[latname], data[lonname])

        self.object_data = data

        try:
            self.process_data(data)
        except ValueError as e:
            self.process_errors.append(e.args[0])

        if formdata is not None:
            if lonname in formdata and latname in formdata:
                self.raw_data = [self._getpoint(formdata.get(latname),
                                                formdata.get(lonname))]
            else:
                self.raw_data = []

            try:
                self.process_formdata(self.raw_data)
            except ValueError as e:
                self.process_errors.append(e.args[0])

        try:
            for filter in self.filters:
                self.data = filter(self.data)
        except ValueError as e:
            self.process_errors.append(e.args[0])
