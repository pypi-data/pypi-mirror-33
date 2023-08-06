
import random
import ipywidgets as wg

from traitlets import observe
from traitlets import Unicode, Dict, List, Int, Bool

from .__meta__ import __version_js__
from .builder_widget_params import BuilderWidgetParams

from copy import deepcopy as copy


_semver_range_frontend_ = '~' + __version_js__

""" For more info on gridOptions, see https://www.ag-grid.com/documentation-main/documentation.php"""


class Grid(wg.DOMWidget):
    """
    Ag-Grid widget
    """
    _model_name = Unicode('AgGridModel').tag(sync=True)
    _view_name = Unicode('AgGridView').tag(sync=True)
    _model_module = Unicode('ipyaggrid').tag(sync=True)
    _view_module = Unicode('ipyaggrid').tag(sync=True)
    _view_module_version = Unicode(_semver_range_frontend_).tag(sync=True)
    _model_module_version = Unicode(_semver_range_frontend_).tag(sync=True)

    _id = Int(0).tag(sync=True)

    width = Int(0).tag(sync=True)
    height = Int(0).tag(sync=True)

    theme = Unicode("").tag(sync=True)
    css_rules = Unicode("").tag(sync=True)
    css_rules_use = List([]).tag(sync=True)
    license = Unicode('').tag(sync=True)

    quick_filter = Bool(True).tag(sync=True)
    export_csv = Bool(True).tag(sync=True)
    export_excel = Bool(True).tag(sync=True)
    index = Bool(False).tag(sync=True)
    keep_multiindex = Bool(True).tag(sync=True)
    hide_grid = Bool(False).tag(sync=True)
    compress_data = Bool(False).tag(sync=True)
    auto_export = Bool(True).tag(sync=True)
    grid_options = Dict({}).tag(sync=True)
    grid_options_multi = List([]).tag(sync=True)
    grid_data = List([]).tag(sync=True)
    key_delete = Bool(False).tag(sync=True)
    to_eval = List([]).tag(sync=True)

    _grid_data_json = Unicode('').tag(sync=True)
    _grid_options_json = Unicode('').tag(sync=True)
    _grid_options_multi_json = Unicode('').tag(sync=True)
    
    _counter_export = Int(0).tag(sync=True)
    _counter_update_data = Int(0).tag(sync=True)
    export_data = Dict({}).tag(sync=True)
    _export_mode = Unicode('').tag(sync=True)


    params = []

    def __init__(self, 
                 width=0,
                 height=0,
                 theme='ag-theme-fresh',
                 css_rules="",
                 quick_filter=True,
                 export_csv=True,
                 export_excel=True,
                 key_delete=False,
                 #  implicit_col_defs=None,
                 index=False,
                 keep_multiindex=True,
                 grid_data=[],
                 grid_options={},
                 grid_options_multi=[],
                 license="",
                 hide_grid=False,
                 compress_data=False,
                 auto_export=True,
                 verbose=False,
                 to_eval=[]):


        self._id = random.randint(0, int(1e9))

        self.width = width
        self.height = height
        self.theme = theme
        self.css_rules = css_rules
        self.quick_filter = quick_filter
        self.export_csv = export_csv
        self.export_excel = export_excel
        self.index = index
        self.keep_multiindex = keep_multiindex
        self.grid_data = []
        self.grid_data_in = copy(grid_data)
        self.grid_options = grid_options
        self.grid_options_multi = grid_options_multi
        self.license = license
        self.hide_grid = hide_grid
        self.compress_data = compress_data
        self.auto_export = auto_export
        self.key_delete = key_delete
        self.to_eval = to_eval

        # Checking and building correctly from the parameters given.

        bwp = BuilderWidgetParams(self, verbose=verbose)
        bwp.valid()
        bwp.build()

        super().__init__()

    # Export functions

    def getRows(self, tab):
        self._export_mode = 'rows'
        self.params = tab
        self._counter_update_data += 1

    def getColumns(self, tab):
        self._export_mode = 'columns'
        self.params = tab
        self._counter_update_data += 1

    def getSnapshot(self):
        self._export_mode = 'snapshot'
        self._counter_update_data += 1

    @observe('_counter_export')
    def exportData(self, change):
        if self._export_mode == 'rows':
            res = []
            for i in self.params:
                res.append(self.grid_data[i])
            self.export_data['rows'] = res
            return res
        elif self._export_mode == 'columns':
            res = []
            for header in self.params:
                column = []
                for row in self.grid_data:
                    column.append(row[header])
                res.append(column)
            self.export_data['columns'] = res
            return res
        elif self._export_mode == 'snapshot':
            self.export_data['snapshot'] = self.grid_data
            return self.grid_data

    # Deleting rows
    def deleteSelectedRow(self):
        self._export_mode = 'delete'
        self._counter_update_data += 1
