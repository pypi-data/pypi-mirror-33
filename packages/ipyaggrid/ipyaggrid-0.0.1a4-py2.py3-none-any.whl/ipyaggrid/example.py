import ipywidgets as widgets
from traitlets import Unicode, Dict, List, Int

@widgets.register
class aggrid_widget(widgets.DOMWidget):
    """Static AgGrid view in a widget."""
    _view_name = Unicode('AgGridView').tag(sync=True)
    _model_name = Unicode('AgGridModel').tag(sync=True)
    _view_module = Unicode('ipyaggrid').tag(sync=True)
    _model_module = Unicode('ipyaggrid').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    _data = List([]).tag(sync=True)
    _options = Dict({}).tag(sync=True)
    _counter = Int(0).tag(sync=True)

def __init__(self, df_data=None):
    
    print('before init')
    super().__init__()

    #Initializing options, normally many to initialize, 
    # but can use the initialization through the grid creation.
    print('init done')

    _data = df_data

    