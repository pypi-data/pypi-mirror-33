from lenstronomy.ImSim.psf_fitting import PsfFitting
from lenstronomy.Workflow.fitting import Fitting
from lenstronomy.MCMC.alignment_matching import AlignmentFitting
import lenstronomy.Util.class_creator as class_creator
from lenstronomy.Workflow.parameters import Param


class FittingSequence(object):
    """
    class to define a sequence of fitting applied, inherite the Fitting class
    """
    def __init__(self, multi_band_list, kwargs_model, kwargs_constraints, kwargs_likelihood, kwargs_params, verbose=True):
        self.multi_band_list = multi_band_list
        self.kwargs_model = kwargs_model
        self.kwargs_constraints = kwargs_constraints
        self.kwargs_likelihood = kwargs_likelihood
        self.kwargs_params = kwargs_params
        self._verbose = verbose
        self.fitting = Fitting(multi_band_list=multi_band_list, kwargs_model=kwargs_model,
                               kwargs_constraints=kwargs_constraints, kwargs_likelihood=kwargs_likelihood,
                               kwargs_params=kwargs_params)
        self._param = Param(kwargs_model, kwargs_constraints, fix_lens_solver=True)

    def fit_sequence(self, fitting_kwargs_list, bijective=True):
        """

        :param fitting_kwargs_list: list of kwargs specify the fitting routine to be executed
        :return:
        """
        chain_list = []
        param_list = []
        samples_mcmc, param_mcmc, dist_mcmc = [], [], []
        lens_temp, source_temp, lens_light_temp, ps_temp, cosmo_temp = self.fitting.init_kwargs()
        for fitting_kwargs in fitting_kwargs_list:
            fitting_routine = fitting_kwargs['fitting_routine']
            if fitting_routine in ['MCMC']:
                samples_mcmc, param_mcmc, dist_mcmc = self.mcmc(fitting_kwargs, lens_temp, source_temp, lens_light_temp, ps_temp, cosmo_temp)
            elif fitting_routine in ['PSO']:
                lens_temp, source_temp, lens_light_temp, ps_temp, cosmo_temp, chain, param = self.pso(fitting_kwargs,
                                                                                            lens_temp, source_temp, lens_light_temp, ps_temp, cosmo_temp)
                chain_list.append(chain)
                param_list.append(param)
            elif fitting_routine in ['psf_iteration']:
                self.psf_iteration(fitting_kwargs, lens_temp, source_temp, lens_light_temp, ps_temp, cosmo_temp)
            elif fitting_routine in ['align_images']:
                self.align_images(fitting_kwargs, lens_temp, source_temp, lens_light_temp, ps_temp, cosmo_temp)
        if bijective is False:
            lens_temp = self._param._update_lens_scaling(cosmo_temp, lens_temp, inverse=False)
            source_temp = self._param.image2source_plane(lens_temp, source_temp)
        return lens_temp, source_temp, lens_light_temp, ps_temp, cosmo_temp, chain_list, param_list, samples_mcmc, param_mcmc, dist_mcmc

    def mcmc(self, fitting_kwargs, lens_input, source_input, lens_light_input, ps_input, cosmo_input):
        """

        :param fitting_kwargs:
        :param lens_input:
        :param source_input:
        :param lens_light_input:
        :param ps_input:
        :return:
        """
        n_burn = fitting_kwargs['n_burn']
        n_run = fitting_kwargs['n_run']
        walkerRatio = fitting_kwargs['walkerRatio']
        mpi = fitting_kwargs.get('mpi', False)
        sigma_scale = fitting_kwargs['sigma_scale']
        compute_bool = fitting_kwargs.get('compute_bands', None)

        gamma_fixed = fitting_kwargs.get('gamma_fixed', False)
        fix_lens = fitting_kwargs.get('fix_lens', False)
        fix_source = fitting_kwargs.get('fix_source', False)
        fix_lens_light = fitting_kwargs.get('fix_lens_light', False)
        fix_point_source = fitting_kwargs.get('fix_point_source', False)
        samples, param, dist = self.fitting.mcmc_run(
                                  lens_input, source_input, lens_light_input, ps_input, cosmo_input,
                                  n_burn, n_run, walkerRatio, threadCount=1, mpi=mpi, init_samples=None,
                                  sigma_factor=sigma_scale, gamma_fixed=gamma_fixed, compute_bool=compute_bool,
                                  fix_lens=fix_lens, fix_source=fix_source, fix_lens_light=fix_lens_light,
                                  fix_point_source=fix_point_source)
        return samples, param, dist

    def pso(self, fitting_kwargs, lens_input, source_input, lens_light_input, ps_input, cosmo_input):
        """

        :param fitting_kwargs:
        :param lens_input:
        :param source_input:
        :param lens_light_input:
        :param ps_input:
        :return:
        """
        mpi = fitting_kwargs.get('mpi', False)
        sigma_scale = fitting_kwargs.get('sigma_scale', 1)
        n_particles = fitting_kwargs.get('n_particles', 10)
        n_iterations = fitting_kwargs.get('n_iterations', 10)
        compute_bool = fitting_kwargs.get('compute_bands', [True]*len(self.multi_band_list))

        gamma_fixed = fitting_kwargs.get('gamma_fixed', False)
        fix_lens = fitting_kwargs.get('fix_lens', False)
        fix_source = fitting_kwargs.get('fix_source', False)
        fix_lens_light = fitting_kwargs.get('fix_lens_light', False)
        fix_point_source = fitting_kwargs.get('fix_point_source', False)
        print_key = fitting_kwargs.get('print_key', 'PSO')
        lens_result, source_result, lens_light_result, ps_result, cosmo_result, chain, param_list = self.fitting.pso_run(
                lens_input, source_input, lens_light_input, ps_input, cosmo_input,
                n_particles, n_iterations, mpi=mpi, sigma_factor=sigma_scale, compute_bool=compute_bool,
                gamma_fixed=gamma_fixed, fix_lens=fix_lens, fix_source=fix_source, fix_lens_light=fix_lens_light,
                fix_point_source=fix_point_source, print_key=print_key)
        return lens_result, source_result, lens_light_result, ps_result, cosmo_result, chain, param_list

    def psf_iteration(self, fitting_kwargs, lens_input, source_input, lens_light_input, ps_input, cosmo_input):
        #lens_temp = copy.deepcopy(lens_input)
        lens_updated = self._param._update_lens_scaling(cosmo_input, lens_input)
        source_updated = self._param.image2source_plane(lens_updated, source_input)
        psf_iter_factor = fitting_kwargs['psf_iter_factor']
        psf_iter_num = fitting_kwargs['psf_iter_num']
        compute_bool = fitting_kwargs.get('compute_bands', [True] * len(self.multi_band_list))
        for i in range(len(self.multi_band_list)):
            if compute_bool[i] is True:
                kwargs_data = self.multi_band_list[i][0]
                kwargs_psf = self.multi_band_list[i][1]
                kwargs_numerics = self.multi_band_list[i][2]
                psf_symmetry = kwargs_psf.get('psf_symmetry', 1)
                image_model = class_creator.creat_image_model(kwargs_data=kwargs_data,
                                                                  kwargs_psf=kwargs_psf,
                                                                  kwargs_numerics=kwargs_numerics,
                                                                  kwargs_model=self.kwargs_model)
                psf_iter = PsfFitting(image_model_class=image_model)
                kwargs_psf = psf_iter.update_iterative(kwargs_psf, lens_updated, source_updated,
                                                       lens_light_input, ps_input,
                                                       factor=psf_iter_factor, num_iter=psf_iter_num,
                                                       symmetry=psf_symmetry, verbose=self._verbose,
                                                       no_break=True)
                self.multi_band_list[i][1] = kwargs_psf
        return 0

    def align_images(self, fitting_kwargs, lens_input, source_input, lens_light_input, ps_input, cosmo_input):
        lens_updated = self._param._update_lens_scaling(cosmo_input, lens_input)
        source_updated = self._param.image2source_plane(lens_updated, source_input)
        mpi = fitting_kwargs.get('mpi', False)
        compute_bool = fitting_kwargs.get('compute_bands', [True] * len(self.multi_band_list))
        n_particles = fitting_kwargs.get('n_particles', 10)
        n_iterations = fitting_kwargs.get('n_iterations', 10)
        lowerLimit = fitting_kwargs.get('lower_limit_shift', -0.2)
        upperLimit = fitting_kwargs.get('upper_limit_shift', 0.2)

        for i in range(len(self.multi_band_list)):
            if compute_bool[i] is True:
                    kwargs_data = self.multi_band_list[i][0]
                    kwargs_psf = self.multi_band_list[i][1]
                    kwargs_numerics = self.multi_band_list[i][2]
                    alignmentFitting = AlignmentFitting(kwargs_data, kwargs_psf, kwargs_numerics, self.kwargs_model, lens_updated, source_updated,
                                                        lens_light_input, ps_input, compute_bool=compute_bool)

                    kwargs_data, chain = alignmentFitting.pso(n_particles, n_iterations, lowerLimit, upperLimit,
                                                              threadCount=1, mpi=mpi,
                                                              print_key='Alignment fitting for band %s ...' % i)
                    print('Align completed for band %s.' % i)
                    self.multi_band_list[i][0] = kwargs_data
        return 0
