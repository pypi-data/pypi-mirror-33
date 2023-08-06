
import gzip
import base64

import simplejson as json
import pandas as pd

from copy import deepcopy as copy

from .util import Util


class BuilderWidgetParams:
    """
    Validating input parameters and building jsons for gridOptions and gridData
    """

    def __init__(self,
                 obj,
                 verbose=False):
        """
        """
        self.obj = obj
        self.verbose = verbose

    def valid(self):
        """
        """

        msg = 'width must be a number of pixels'
        assert isinstance(self.obj.width, int), msg

        msg = 'height must be a number of pixels'
        assert isinstance(self.obj.height, int), msg

        li_theme = ['ag-theme-fresh',
                    'ag-theme-dark',
                    'ag-theme-blue',
                    'ag-theme-material',
                    'ag-theme-bootstrap',
                    'ag-theme-balham']
        msg = 'theme must be one of {}'.format(li_theme)
        assert self.obj.theme in li_theme, msg

        msg = 'css_rules must be a string'
        assert isinstance(self.obj.css_rules, str), msg

        msg = 'quick_filter must be a boolean'
        assert isinstance(self.obj.quick_filter, bool), msg

        msg = 'export_csv must be a boolean'
        assert isinstance(self.obj.export_csv, bool), msg

        msg = 'export_excel must be a boolean'
        assert isinstance(self.obj.export_excel, bool), msg

        msg = 'license must be a string'
        assert isinstance(self.obj.license, str), msg

        msg = 'hide_grid must be a boolean'
        assert isinstance(self.obj.hide_grid, bool), msg

        msg = 'keep_multiindex must be a boolean'
        assert isinstance(self.obj.keep_multiindex, bool), msg

        msg = 'auto_export must be a boolean'
        assert isinstance(self.obj.auto_export, bool), msg

        msg = 'key_delete must be a boolean'
        assert isinstance(self.obj.key_delete, bool), msg

        msg = 'edit_mode must be a boolean'
        assert isinstance(self.obj.edit_mode, bool), msg

        msg = 'to_eval must be a list'
        assert isinstance(self.obj.to_eval, list), msg
        if isinstance(self.obj.to_eval, list):
            msg = 'each element of to_eval must be a string'
            for e in self.obj.to_eval:
                assert isinstance(e, str), msg

        msg = 'grid_data must be a list or a dataframe'
        assert isinstance(self.obj.grid_data_in, (list, pd.core.frame.DataFrame)), msg
        if isinstance(self.obj.grid_data, list):
            msg = 'each element of grid_data must be a dict'
            for e in self.obj.grid_data:
                assert isinstance(e, dict), msg
            self.obj._is_df = False
        else:
            self.obj._is_df = True

        msg = 'both grid_options and grid_options_multi cannot be set'
        assert ((self.obj.grid_options == {}) or
                (self.obj.grid_options_multi == [])), msg

        msg = 'one exactly of grid_options or grid_options_multi mut be set'
        assert not((self.obj.grid_options == {}) and
                   (self.obj.grid_options_multi == [])), msg

        if self.obj.grid_options != {}:
            msg = 'grid_options must be a dict'
            assert isinstance(self.obj.grid_options, dict), msg

        if self.obj.grid_options_multi != []:
            msg = 'grid_options_multi must be a list or a tuple'
            assert isinstance(self.obj.grid_options_multi, (list, tuple)), msg
            msg1 = 'each element of grid_options_multi must be a list or tuple of length 2'
            msg2 = 'in each grid_options_multi element of length 2, the first one must be a string'
            msg3 = 'in each grid_options_multi element of length 3, the second one must be a dict'
            for e in self.obj.grid_options_multi:
                assert isinstance(e, (list, tuple)) and len(e) == 2, msg1
                assert isinstance(e[0], str), msg2
                assert isinstance(e[1], dict), msg3

    def build(self):
        """
        """

        self.obj.license = Util.encode_b64(self.obj.license)
        self.obj.css_rules_use = Util.build_css_rules(self.obj.css_rules)

        is_multi = True if self.obj.grid_options_multi != [] else False

        if self.obj.auto_export:
            self.obj.export_data = {'auto': True}
        else:
            self.obj.export_data = {'auto': False}

        if is_multi:
            grid_options_multi_2 = []
            for name, options in self.obj.grid_options_multi:
                self.obj._grid_data_down, options_2 = self.preprocess_input(
                    self.obj.grid_data_in,
                    options,
                    index=self.obj.index,
                    keep_multiindex=self.obj.keep_multiindex,
                    verbose=self.verbose)
                grid_options_multi_2.append((name, options_2))
            self.obj.grid_options_multi_json = grid_options_multi_2

        else:
            self.obj._grid_data_down, self.obj.grid_options = self.preprocess_input(
                self.obj.grid_data_in,
                self.obj.grid_options,
                index=self.obj.index,
                keep_multiindex=self.obj.keep_multiindex,
                verbose=self.verbose)

        if is_multi:
            self.obj._grid_options_multi_json = Util.build_options(
                {'data': self.obj.grid_options_multi})
        else:
            self.obj._grid_options_json = Util.build_options(self.obj.grid_options)

    def preprocess_input(self,
                         grid_data,
                         grid_options,
                         index,
                         keep_multiindex,
                         verbose=False):
        """
        """
        if Util.is_df(grid_data):
            self.obj._is_df = True
        else:
            self.obj._is_df = False

        if Util.is_multiindex_df(grid_data):
            grid_data_2, grid_options_2 = Util.prepare_multiindex_df(
                grid_data,
                grid_options,
                index=index,
                keep_multiindex=keep_multiindex,
                verbose=verbose)

        elif Util.is_df(grid_data):
            grid_data_2, grid_options_2 = Util.prepare_singleindex_df(
                grid_data,
                grid_options,
                index=index,
                verbose=verbose)

        else:
            grid_data_2, grid_options_2 = grid_data, grid_options

        grid_options_2 = Util.update_columnTypes(
            grid_options_2,
            verbose=verbose)

        return Util.build_data(grid_data_2), grid_options_2

    def to_dict(self):
        """
        """
        d = copy(self.__dict__)
        d = {k: v for k, v in d.items() if v is not None}
        return d

    def pprint(self, indent=2):
        """
        """
        d = json.dumps(self.to_dict(),
                       sort_keys=True,
                       indent=indent)
        print(d)

    def __repr__(self):
        return str(self.to_dict())
