
import pytest
import numpy as np
import numpy.testing as npt
from lenstronomy.LightModel.Profiles.nie import NIE
from lenstronomy.LightModel.Profiles.chameleon import Chameleon
import lenstronomy.Util.param_util as param_util


class TestPowerLaw(object):
    """
    class to test the Moffat profile
    """
    def setup(self):
        pass

    def test_param_name(self):
        chameleon = Chameleon()
        names = chameleon.param_names
        assert names[0] == 'amp'

    def test_function(self):
        """

        :return:
        """
        chameleon = Chameleon()
        nie = NIE()

        x = np.linspace(0.1, 10, 10)
        w_c, w_t = 0.5, 1.
        phi_G, q = 0.3, 0.8
        e1, e2 = param_util.phi_q2_ellipticity(phi_G, q)
        kwargs_light = {'amp': 1., 'w_c': .5, 'w_t': 1., 'e1': e1, 'e2': e2}
        s_scale_1 = np.sqrt(4 * w_c ** 2 / (1. + q) ** 2)
        s_scale_2 = np.sqrt(4 * w_t ** 2 / (1. + q) ** 2)
        kwargs_1 = {'amp': 1., 's_scale': s_scale_1, 'e1': e1, 'e2': e2}
        kwargs_2 = {'amp': 1., 's_scale': s_scale_2, 'e1': e1, 'e2': e2}
        flux = chameleon.function(x=x, y=1., **kwargs_light)
        flux1 = nie.function(x=x, y=1., **kwargs_1)
        flux2 = nie.function(x=x, y=1., **kwargs_2)
        npt.assert_almost_equal(flux, (flux1 - flux2) / (1. + q), decimal=5)


if __name__ == '__main__':
    pytest.main()
