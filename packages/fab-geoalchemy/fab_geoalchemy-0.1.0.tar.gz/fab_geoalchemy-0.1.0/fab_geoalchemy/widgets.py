from wtforms.widgets import Input
from markupsafe import Markup


class LatLonWidget(Input):

    def __call__(self, field, **kwargs):
        lat = Markup('Latitude: <input type="text" %s>' %
                     self.html_params(name="%s_lat" % field.name, **kwargs))
        lon = Markup('Longitude: <input type="text" %s>' %
                     self.html_params(name="%s_lon" % field.name, **kwargs))
        return lat+lon
