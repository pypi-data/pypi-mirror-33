from django.forms.widgets import Select


class CosmicSelectAutocomplete(Select):
    def __init__(self, url='', attrs=None, *args, **kwargs):
        if attrs is None:
            attrs = {}
        attrs['data-autocomplete-url'] = url
        attrs['class'] = 'search selection'
        super().__init__(attrs, *args, **kwargs)

