import ipywidgets as widgets
from IPython.display import display, HTML

class UQValue(object):

    def __init__(self, name, **kwargs):
        # print("INIT:%s" % name)
        self._width = kwargs.get('width', 'auto')
        self._cb = kwargs.get('cb')
        self._desc = kwargs.get('desc', '')
        if self._desc == '':
            self._desc = kwargs.get('description', '')
        self.default = self.dd.value
        self.disabled = kwargs.get('disabled', False)
        units = kwargs.get('units')
        self.units = self.find_unit(units)
        self.valid = widgets.Valid(value=True, layout=widgets.Layout(flex='0 1 0'))
        try:
            self.dd.on_submit(lambda x: self.cb(None))
        except:
            pass
        self.dd.observe(lambda x: self.cb(x['new']), names='value')
        self.oldval = None
        self.no_cb = False
        self.name = name
        self._format = kwargs.get('format', '')
        self._min = kwargs.get('min')
        self._max = kwargs.get('max')