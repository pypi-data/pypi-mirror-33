""" Widget
"""
from zope.interface import implements

from zope.schema import Field
from zope.schema.interfaces import IField

from zope.app.form.browser.interfaces import IBrowserWidget
from zope.app.form.interfaces import IInputWidget

from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from Products.Archetypes.atapi import StringWidget

from eea.geotags.field.location import GeotagsFieldMixin
from eea.geotags.field.common import get_json

from eea.geotags.widget.common import get_js_props
from eea.geotags.widget.common import get_base_url
from eea.geotags.widget.common import get_maps_api_key

from eea.geotags.widget.common import URL_DIALOG
from eea.geotags.widget.common import URL_SIDEBAR
from eea.geotags.widget.common import URL_BASKET
from eea.geotags.widget.common import URL_JSON
from eea.geotags.widget.common import URL_SUGGESTIONS
from eea.geotags.widget.common import URL_COUNTRY_MAPPING


class GeotagsWidget(StringWidget):
    """ Geotags
    """
    _properties = StringWidget._properties.copy()
    _properties.update({
        'macro': "eea.geotags",
        'dialog': URL_DIALOG,
        'sidebar': URL_SIDEBAR,
        'basket': URL_BASKET,
        'json': URL_JSON,
        'suggestions': URL_SUGGESTIONS,
        'country_mapping': URL_COUNTRY_MAPPING,
    })

    def get_geojson(self, name, context, request):
        # type: () -> str
        return (
            self.postback and request.get(name, None)
            or get_json(context)
        )

    def get_params(self, field, name, context, request):
        geojson = self.get_geojson(name, context, request)
        base_url = get_base_url(request)
        return dict(
            id=name,
            name=name,
            base_url=base_url,
            label=self.Label(context),
            geojson=geojson,
            js_props=get_js_props(field.multiline, name, name, base_url, geojson),
            api_key=get_maps_api_key(),
        )


###
# Formlib widget
######

class IGeotagSingleField(IField):
    """ The field interface
    """

class GeotagMixinField(Field, GeotagsFieldMixin):
    """ Geotag Mixin Field
    """

    def set(self, instance, value, **kwargs):
        """ Set
        """
        self.setJSON(instance.context, value, **kwargs)

class GeotagSingleField(GeotagMixinField):
    """ Geotag Single Field
    """
    implements(IGeotagSingleField)

    @property
    def multiline(self):
        """ Multiline
        """
        return False

class IGeotagMultiField(IField):
    """ The field interface
    """

class GeotagMultiField(GeotagMixinField):
    """ Geotag Multi Field
    """
    implements(IGeotagMultiField)

    @property
    def multiline(self):
        """ Multiline
        """
        return True

class FormlibGeotagWidget(object):
    """ Formlib Geotag Widget
    """
    implements(IBrowserWidget, IInputWidget)
    template = ViewPageTemplateFile("location.pt")

    # See zope.app.form.interfaces.IInputWidget
    name = None
    label = property(lambda self: self.context.title)
    hint = property(lambda self: self.context.description)
    visible = True
    required = property(lambda self: self.context.required)

    _prefix = "form."
    _value = None
    _error = None

    dialog = '@@eea.geotags.dialog'
    sidebar = '@@eea.geotags.sidebar'
    basket = '@@eea.geotags.basket'
    json = '@@eea.geotags.json'
    suggestions = '@@eea.geotags.suggestions'

    def __init__(self, field, request):
        self.context = field
        self.request = request
        self.name = self._prefix + field.__name__

    def setPrefix(self, prefix):
        """ See zope.app.form.interfaces.IWidget
        """
        # Set the prefix locally
        if not prefix.endswith("."):
            prefix += '.'
        self._prefix = prefix
        self.name = prefix + self.context.__name__

    def setRenderedValue(self, value):
        """ Set rendered value
        """
        pass

    def hasInput(self):
        """ Has input
        """
        val = self.request.form.get('location')
        if val and val.strip():
            return True

        return False

    def error(self):
        """ See zope.app.form.browser.interfaces.IBrowserWidget
        """
        if self._error:
            return "Need valid input"

    def getInputValue(self):
        """ Get input value
        """
        return self.request.form['location']

    def applyChanges(self, content):
        """ See zope.app.form.interfaces.IInputWidget
        """
        field = self.context
        new_value = self.getInputValue()
        old_value = field.query(content, self)
        # The selection has not changed
        if new_value == old_value:
            return False
        field.set(content, new_value)
        return True

    def __call__(self):
        return self.template()
