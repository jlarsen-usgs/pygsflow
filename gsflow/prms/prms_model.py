from ..control import ControlFile
from .prms_parameter import PrmsParameters
from .prms_data import PrmsData
from ..output import StatVar
from ..utils import io
import warnings
warnings.simplefilter('always', PendingDeprecationWarning)
warnings.simplefilter('always', UserWarning)


class Prms(object):
    def __new__(cls, control=None, parameters=None, control_file=None):
        err = "Prms is deprecated; calling PrmsModel()"
        warnings.warn(err, PendingDeprecationWarning)

        if isinstance(control, ControlFile):
            if isinstance(parameters, PrmsParameters):
                return PrmsModel(control, parameters=parameters)
            return PrmsModel(control)
        else:
            return PrmsModel.load_from_file(control)


class PrmsModel(object):
    """
    PrmsModel loading class

    Parameters
    ----------
    control : ControlFile object
    parameters : PrmsParameters object
    data : PrmsData object

    Examples
    --------

    load from file

    >>> prms = gsflow.prms.PrmsModel.load_from_file("gsflow.control")

    create new object

    >>> control = gsflow.ControlFile.load_from_file("gsflow.control")
    >>> prms = gsflow.prms.PrmsModel(control, parmaters=None, data=None)

    """
    def __init__(self, control, parameters=None, data=None):
        self.control = control
        self._control_file = control.control_file

        self.parameters = parameters
        if parameters is None:
            parameter_files = control.get_values("param_file")
            self.parameters = PrmsModel._load_parameters(parameter_files)

        self.data = data
        if data is None:
            data_file = control.get_values("data_file")
            self.data = PrmsModel._load_data(data_file)

    def export_nc(self, f, modflow, **kwargs):
        """
        Method to export input data to a NetCdf file

        Parameters
        ----------
        f : str or fp.export.NetCdf
            filename to write the parameter to (*.nc)
        modflow : object
            fp.modflow.Modflow or gsflow.modflow.Modflow object

        Notes
        -----
        NetCdf export relies on flopy, so at the moment will
        only work for GSFLOW models where PRMS has the same
        discretization as the modflow grid

        """
        if self.parameters is not None:
            f = self.parameters.export_nc(f, modflow, **kwargs)

        return f

    @property
    def Data(self):
        err = "Data is depreciated, calling data"
        warnings.warn(err, PendingDeprecationWarning)
        return self.data

    @staticmethod
    def load_from_file(control_file):
        """
        PrmsModel load method from a control file

        Parameters
        ----------
        control_file : str
            control file path and name

        Returns
        -------
            PrmsModel object

        """
        print("Prms model loading ...")
        control = ControlFile.load_from_file(control_file)
        parameter_files = control.get_values("param_file")
        parameter_files = [io.get_file_abs(control_file, pfn) for pfn in parameter_files]
        parameters = PrmsModel._load_parameters(parameter_files)
        data_file = control.get_values("data_file")[0]
        data_file = io.get_file_abs(control_file, data_file)
        data = PrmsModel._load_data(data_file)
        print("PRMS model loaded ...")
        return PrmsModel(control=control, parameters=parameters, data=data)

    @staticmethod
    def _load_parameters(parameter_files):
        """
        Method to load parameter files

        Parameters
        ----------
        parameter_files : list
            list of parameter files

        Returns
        -------
            PrmsParameters object

        """
        return PrmsParameters.load_from_file(parameter_files)

    @staticmethod
    def _load_data(data_file):
        """
        Method to load a data file

        Parameters
        ----------
        data_file : str
            data file name

        Returns
        -------
            PrmsData object

        """
        try:
            return PrmsData.load_from_file(data_file)
        except:
            err = "PrmsData load error, Skipping parameter files"
            warnings.warn(err, UserWarning)
            return

    def get_statVar(self):
        """
        Deprecated method to get statvar output

        Returns
        -------
            pd.DataFrame of the stat_var file

        """
        err = "get_statVar is Deprecated, use get_StatVar()"
        warnings.warn(err, PendingDeprecationWarning)
        return self.get_StatVar()

    def get_StatVar(self):
        """
        Method to get statvar output

        Returns
        -------
            pd.DataFrame of the stat_var file

        """
        self.stat = StatVar.load_from_control_object(self.control)
        return self.stat.stat_df

    @property
    def control_file(self):
        """
        Returns
        -------
            control file path
        """
        return self._control_file

    @control_file.setter
    def control_file(self, new_values):
        self._control_file = new_values
        self.control.control_file = self._control_file
