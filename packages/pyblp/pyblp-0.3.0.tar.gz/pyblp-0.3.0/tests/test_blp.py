"""Primary tests."""

import pytest
import numpy as np
import scipy.optimize

from pyblp import options, build_matrix, Problem, Iteration, Optimization, Formulation


@pytest.mark.usefixtures('simulated_problem')
@pytest.mark.parametrize('solve_options', [
    pytest.param({'steps': 1}, id="one step"),
    pytest.param({'linear_fp': False}, id="nonlinear fixed point"),
    pytest.param({'delta_behavior': 'first'}, id="conservative starting delta values"),
    pytest.param({'error_behavior': 'punish', 'error_punishment': 1e10}, id="error punishment"),
    pytest.param({'center_moments': False, 'se_type': 'unadjusted'}, id="simple covariance matrices")
])
def test_accuracy(simulated_problem, solve_options):
    """Test that starting parameters that are half their true values give rise to errors of less than 10%."""
    simulation, _, problem, _ = simulated_problem

    # solve the problem
    sigma = 0.5 * simulation.sigma
    pi = 0.5 * simulation.pi if simulation.pi is not None else None
    results = problem.solve(sigma, pi, linear_costs=simulation.linear_costs, **solve_options)

    # test the accuracy of the estimated parameters
    for key in ['gamma', 'beta', 'sigma', 'pi']:
        estimate = getattr(results, key, None)
        if estimate is not None:
            np.testing.assert_allclose(getattr(simulation, key), estimate, atol=0, rtol=0.1, err_msg=key)


@pytest.mark.usefixtures('simulated_problem')
@pytest.mark.parametrize(['solve_options1', 'solve_options2'], [
    pytest.param({'processes': 1}, {'processes': 2}, id="single process and multiprocessing"),
    pytest.param({'costs_bounds': (-np.inf, np.inf)}, {'costs_bounds': (-1e10, 1e10)}, id="non-binding costs bounds")
])
def test_trivial_changes(simulated_problem, solve_options1, solve_options2):
    """Test that solving a problem with arguments that shouldn't give rise to meaningful differences doesn't give rise
    to any differences.
    """
    simulation, _, problem, _ = simulated_problem

    # solve the problem with both sets of options
    results = []
    for solve_options in [solve_options1, solve_options2]:
        results.append(problem.solve(
            simulation.sigma, simulation.pi, steps=1, linear_costs=simulation.linear_costs, **solve_options
        ))

    # test that all arrays in the results are essentially identical
    for key, result1 in results[0].__dict__.items():
        if isinstance(result1, np.ndarray) and result1.dtype != np.object:
            result2 = getattr(results[1], key)
            np.testing.assert_allclose(result1, result2, atol=1e-14, rtol=0, err_msg=key)


@pytest.mark.usefixtures('simulated_problem')
@pytest.mark.parametrize(['ED', 'ES'], [
    pytest.param(1, 0, id="1 demand-side FE"),
    pytest.param(0, 1, id="1 supply-side FE"),
    pytest.param(1, 1, id="1 demand- and 1 supply-side FE"),
    pytest.param(2, 0, id="2 demand-side FEs"),
    pytest.param(0, 2, id="2 supply-side FEs"),
    pytest.param(2, 2, id="2 demand- and 2 supply-side FEs"),
    pytest.param(3, 0, id="3 demand-side FEs"),
    pytest.param(0, 3, id="3 supply-side FEs"),
    pytest.param(3, 3, id="3 demand- and 3 supply-side FEs"),
    pytest.param(2, 1, id="2 demand- and 1 supply-side FEs"),
    pytest.param(1, 2, id="1 demand- and 2 supply-side FEs"),
])
def test_fixed_effects(simulated_problem, ED, ES):
    """Test that absorbing different numbers of demand- and supply-side fixed effects gives rise to essentially
    identical first-stage results as including indicator variables. Also test that results that should be equal when
    there aren't any fixed effects are indeed equal.
    """
    simulation, product_data, problem, results = simulated_problem

    # test that results that should be equal when there aren't any fixed effects are indeed equal
    for key in ['delta', 'tilde_costs', 'xi', 'omega', 'xi_jacobian', 'omega_jacobian']:
        result = getattr(results, key)
        true_result = getattr(results, f'true_{key}')
        assert (result is not None) == (true_result is not None)
        if result is not None:
            np.testing.assert_allclose(result, true_result, atol=1e-14, rtol=0, err_msg=key)

    # there cannot be supply-side fixed effects if there isn't a supply side
    if problem.K3 == 0:
        ES = 0
    if ED == ES == 0:
        return

    # add fixed effect IDs to the data
    np.random.seed(0)
    demand_names = []
    supply_names = []
    product_data = {k: product_data[k] for k in product_data.dtype.names}
    for side, count, names in [('demand', ED, demand_names), ('supply', ES, supply_names)]:
        for index in range(count):
            name = f'{side}_ids{index}'
            ids = np.random.choice(['a', 'b', 'c'], product_data['market_ids'].size, [0.7, 0.2, 0.1])
            product_data[name] = ids
            names.append(name)

    # remove constants
    product_formulations = list(problem.product_formulations).copy()
    if ED > 0:
        product_formulations[0] = Formulation(f'{product_formulations[0]._formula} - 1')
        product_data['demand_instruments'] = product_data['demand_instruments'][:, 1:]
    if ES > 0:
        product_formulations[2] = Formulation(f'{product_formulations[2]._formula} - 1')
        product_data['supply_instruments'] = product_data['supply_instruments'][:, 1:]

    # build formulas for the IDs
    demand_formula = ' + '.join(demand_names)
    supply_formula = ' + '.join(supply_names)

    # solve the first stage of a problem in which the fixed effects are absorbed
    product_formulations1 = product_formulations.copy()
    if ED > 0:
        product_formulations1[0] = Formulation(product_formulations[0]._formula, demand_formula)
    if ES > 0:
        product_formulations1[2] = Formulation(product_formulations[2]._formula, supply_formula)
    problem1 = Problem(product_formulations1, product_data, problem.agent_formulation, simulation.agent_data)
    results1 = problem1.solve(simulation.sigma, simulation.pi, steps=1)

    # solve the first stage of a problem in which fixed effects are included as indicator variables
    product_data2 = product_data.copy()
    product_formulations2 = product_formulations.copy()
    if ED > 0:
        demand_indicators = build_matrix(Formulation(demand_formula), product_data)
        product_data2['demand_instruments'] = np.c_[product_data['demand_instruments'], demand_indicators]
        product_formulations2[0] = Formulation(f'{product_formulations[0]._formula} + {demand_formula}')
    if ES > 0:
        supply_indicators = build_matrix(Formulation(supply_formula), product_data)
        product_data2['supply_instruments'] = np.c_[product_data['supply_instruments'], supply_indicators]
        product_formulations2[2] = Formulation(f'{product_formulations[2]._formula} + {supply_formula}')
    problem2 = Problem(product_formulations2, product_data2, problem.agent_formulation, simulation.agent_data)
    results2 = problem2.solve(simulation.sigma, simulation.pi, steps=1)

    # test that all arrays expected to be identical are identical
    keys = [
        'theta', 'sigma', 'pi', 'beta', 'gamma', 'sigma_se', 'pi_se', 'beta_se', 'gamma_se', 'true_delta',
        'true_tilde_costs', 'true_xi', 'true_omega', 'true_xi_jacobian', 'true_omega_jacobian', 'objective', 'gradient',
        'sigma_gradient', 'pi_gradient'
    ]
    for key in keys:
        result1 = getattr(results1, key)
        if result1 is not None:
            result2 = getattr(results2, key)
            if 'beta' in key or 'gamma' in key:
                result2 = result2[:result1.size]
            np.testing.assert_allclose(result1, result2, atol=1e-8, rtol=1e-5, err_msg=key)


@pytest.mark.usefixtures('simulated_problem')
@pytest.mark.parametrize('solve_options', [
    pytest.param({'iteration': Iteration('simple')}, id="configured iteration"),
    pytest.param({'processes': 2}, id="multiprocessing")
])
def test_merger(simulated_problem, solve_options):
    """Test that prices and shares simulated under changed firm IDs are reasonably close to prices and shares computed
    from the results of a solved problem. In particular, test that unchanged prices and shares are farther from their
    simulated counterparts than those computed by approximating a merger, which in turn are farther from their simulated
    counterparts than those computed by fully solving a merger. Also test that simple acquisitions increase HHI. These
    inequalities are only guaranteed because of the way in which the simulations are configured.
    """
    simulation, _, _, results = simulated_problem

    # get changed prices and shares
    changed_product_data = simulation.solve(firms_index=1)

    # solve for approximate and actual changed prices and shares
    approximated_prices = results.solve_approximate_merger()
    estimated_prices = results.solve_merger(**solve_options)
    approximated_shares = results.compute_shares(approximated_prices)
    estimated_shares = results.compute_shares(estimated_prices)

    # test that estimated prices are closer to changed prices than approximate prices
    approximated_prices_error = np.linalg.norm(changed_product_data.prices - approximated_prices)
    estimated_prices_error = np.linalg.norm(changed_product_data.prices - estimated_prices)
    np.testing.assert_array_less(estimated_prices_error, approximated_prices_error, verbose=True)

    # test that estimated shares are closer to changed shares than approximate shares
    approximated_shares_error = np.linalg.norm(changed_product_data.shares - approximated_shares)
    estimated_shares_error = np.linalg.norm(changed_product_data.shares - estimated_shares)
    np.testing.assert_array_less(estimated_shares_error, approximated_shares_error, verbose=True)

    # test that HHI increases
    hhi = results.compute_hhi()
    changed_hhi = results.compute_hhi(firms_index=1, shares=estimated_shares)
    np.testing.assert_array_less(hhi, changed_hhi, verbose=True)


@pytest.mark.usefixtures('simulated_problem')
def test_markup_positivity(simulated_problem):
    """Test that simulated markups are positive."""
    _, _, _, results = simulated_problem
    markups = results.compute_markups()
    np.testing.assert_array_less(0, markups, verbose=True)


@pytest.mark.usefixtures('simulated_problem')
@pytest.mark.parametrize('factor', [pytest.param(0.01, id="large"), pytest.param(0.0001, id="small")])
def test_elasticity_aggregates_and_means(simulated_problem, factor):
    """Test that the magnitude of simulated aggregate elasticities is less than the magnitude of mean elasticities, both
    for prices and for other characteristics.
    """
    simulation, _, _, results = simulated_problem

    # test that demand for an entire product category is less elastic for prices than for individual products
    np.testing.assert_array_less(
        np.abs(results.compute_aggregate_elasticities(factor)),
        np.abs(results.extract_diagonal_means(results.compute_elasticities())),
        verbose=True
    )

    # test the same inequality but for all non-price characteristics
    for name in {n for f in simulation._X1_formulations + simulation._X2_formulations for n in f.names} - {'prices'}:
        np.testing.assert_array_less(
            np.abs(results.compute_aggregate_elasticities(factor, name)),
            np.abs(results.extract_diagonal_means(results.compute_elasticities(name))),
            err_msg=name,
            verbose=True
        )


@pytest.mark.usefixtures('simulated_problem')
def test_diversion_ratios(simulated_problem):
    """Test simulated diversion ratio magnitudes and row sums."""
    simulation, _, _, results = simulated_problem

    # test that price-based ratios are between zero and one and that ratio matrix rows sum to one
    for compute in [results.compute_diversion_ratios, results.compute_long_run_diversion_ratios]:
        ratios = compute()
        np.testing.assert_array_less(0, ratios, err_msg=compute.__name__, verbose=True)
        np.testing.assert_array_less(ratios, 1, err_msg=compute.__name__, verbose=True)
        np.testing.assert_allclose(ratios.sum(axis=1), 1, atol=1e-14, rtol=0, err_msg=compute.__name__)

    # test that rows sum to one even when computing ratios for non-price characteristics
    for name in {n for f in simulation._X1_formulations + simulation._X2_formulations for n in f.names} - {'prices'}:
        ratios = results.compute_diversion_ratios(name)
        np.testing.assert_allclose(ratios.sum(axis=1), 1, atol=1e-14, rtol=0, err_msg=name)


@pytest.mark.usefixtures('simulated_problem')
def test_second_step(simulated_problem):
    """Test that results from two-step GMM on simulated data are identical to results from one-step GMM configured with
    results from a first step.
    """
    simulation, _, problem, _ = simulated_problem

    # remove sigma bounds so that it can't get stuck at zero
    unbounded_sigma_bounds = (np.full_like(simulation.sigma, -np.inf), np.full_like(simulation.sigma, +np.inf))

    # get two-step GMM results
    results = problem.solve(simulation.sigma, simulation.pi, unbounded_sigma_bounds, steps=2)
    assert results.step == 2 and results.last_results.step == 1 and results.last_results.last_results is None

    # manually get the same results
    results1 = problem.solve(simulation.sigma, simulation.pi, unbounded_sigma_bounds, steps=1)
    results2 = problem.solve(
        results1.sigma, results1.pi, unbounded_sigma_bounds, delta=results1.delta, WD=results1.updated_WD,
        WS=results1.updated_WS, steps=1
    )
    assert results1.step == results2.step == 1 and results1.last_results is None and results2.last_results is None

    # test that results are essentially identical
    for key, result in results.__dict__.items():
        if 'cumulative' not in key and isinstance(result, np.ndarray) and result.dtype != np.object:
            result2 = getattr(results2, key)
            np.testing.assert_allclose(result, result2, atol=1e-14, rtol=0, err_msg=key)


@pytest.mark.usefixtures('simulated_problem')
@pytest.mark.parametrize('scipy_method', [
    pytest.param('l-bfgs-b', id="L-BFGS-B"),
    pytest.param('slsqp', id="SLSQP")
])
def test_gradient_optionality(simulated_problem, scipy_method):
    """Test that the option of not computing the gradient for simulated data does not affect estimates when the gradient
    isn't used.
    """
    simulation, _, problem, _ = simulated_problem

    # define a custom optimization method that doesn't use gradients
    def custom_method(initial, bounds, objective_function, _):
        wrapper = lambda x: objective_function(x)[0]
        results = scipy.optimize.minimize(wrapper, initial, method=scipy_method, bounds=bounds)
        return results.x, results.success

    # solve the problem when not using gradients and when not computing them
    optimization1 = Optimization(custom_method)
    optimization2 = Optimization(scipy_method, compute_gradient=False)
    results1 = problem.solve(simulation.sigma, simulation.pi, steps=1, optimization=optimization1)
    results2 = problem.solve(simulation.sigma, simulation.pi, steps=1, optimization=optimization2)

    # test that all arrays are essentially identical
    for key, result1 in results1.__dict__.items():
        if isinstance(result1, np.ndarray) and result1.dtype != np.object:
            result2 = getattr(results2, key)
            np.testing.assert_allclose(result1, result2, atol=1e-14, rtol=0, err_msg=key)


@pytest.mark.usefixtures('simulated_problem')
@pytest.mark.parametrize('method', [
    pytest.param('l-bfgs-b', id="L-BFGS-B"),
    pytest.param('tnc', id="TNC"),
    pytest.param('slsqp', id="SLSQP"),
    pytest.param('knitro', id="Knitro")
])
def test_bounds(simulated_problem, method):
    """Test that non-binding bounds on parameters in simulated problems do not affect estimates and that binding bounds
    are respected.
    """
    simulation, _, problem, _ = simulated_problem

    # all problems will be solved with the same optimization method starting as close to the true parameters as possible
    solve = lambda s, p: problem.solve(
        np.minimum(np.maximum(simulation.sigma, s[0]), s[1]),
        np.minimum(np.maximum(simulation.pi, p[0]), p[1]) if simulation.pi is not None else None,
        sigma_bounds=s,
        pi_bounds=p,
        steps=1,
        optimization=Optimization(method)
    )

    # solve the problem when unbounded
    unbounded_sigma_bounds = (np.full_like(simulation.sigma, -np.inf), np.full_like(simulation.sigma, +np.inf))
    unbounded_pi_bounds = None
    if simulation.pi is not None:
        unbounded_pi_bounds = (np.full_like(simulation.pi, -np.inf), np.full_like(simulation.pi, +np.inf))
    unbounded_results = solve(unbounded_sigma_bounds, unbounded_pi_bounds)

    # choose an element in each parameter matrix and identify its estimated value
    sigma_index = (simulation.sigma.nonzero()[0][0], simulation.sigma.nonzero()[1][0])
    sigma_value = unbounded_results.sigma[sigma_index]
    pi_index = None
    if simulation.pi is not None:
        pi_index = (simulation.pi.nonzero()[0][0], simulation.pi.nonzero()[1][0])
        pi_value = unbounded_results.pi[pi_index]

    # use different types of binding bounds and skip types that fix all parameters
    for lb_scale, ub_scale in [(+np.inf, -0.1), (-0.1, +np.inf), (+1, -0.1), (-0.1, +1), (0, 0)]:
        binding_sigma_bounds = (np.full_like(simulation.sigma, -np.inf), np.full_like(simulation.sigma, +np.inf))
        binding_sigma_bounds[0][sigma_index] = sigma_value - lb_scale * np.abs(sigma_value)
        binding_sigma_bounds[1][sigma_index] = sigma_value + ub_scale * np.abs(sigma_value)
        if simulation.pi is None:
            binding_pi_bounds = None
            if np.array_equal(*map(np.abs, binding_sigma_bounds)):
                continue
        else:
            binding_pi_bounds = (np.full_like(simulation.pi, -np.inf), np.full_like(simulation.pi, +np.inf))
            binding_pi_bounds[0][pi_index] = pi_value - lb_scale * np.abs(pi_value)
            binding_pi_bounds[1][pi_index] = pi_value + ub_scale * np.abs(pi_value)
            if np.array_equal(*map(np.abs, binding_sigma_bounds)) and np.array_equal(*map(np.abs, binding_pi_bounds)):
                continue

        # solve the problem with binding bounds and test that they are essentially respected
        binding_results = solve(binding_sigma_bounds, binding_pi_bounds)
        assert_array_less = lambda a, b: np.testing.assert_array_less(a, b + 1e-14, verbose=True)
        assert_array_less(binding_sigma_bounds[0], binding_results.sigma)
        assert_array_less(binding_results.sigma, binding_sigma_bounds[1])
        if simulation.pi is not None:
            assert_array_less(binding_pi_bounds[0], binding_results.pi)
            assert_array_less(binding_results.pi, binding_pi_bounds[1])

    # for methods other than TNC, which works differently with bounds, test that non-binding bounds furnish results that
    #   are similar to their unbounded counterparts
    if method != 'tnc':
        unbinding_sigma_bounds = (
            simulation.sigma - 1e10 * np.abs(simulation.sigma),
            simulation.sigma + 1e10 * np.abs(simulation.sigma)
        )
        unbinding_pi_bounds = None
        if simulation.pi is not None:
            unbinding_pi_bounds = (
                simulation.pi - 1e10 * np.abs(simulation.pi),
                simulation.pi + 1e10 * np.abs(simulation.pi)
            )
        unbinding_results = solve(unbinding_sigma_bounds, unbinding_pi_bounds)
        np.testing.assert_allclose(unbounded_results.sigma, unbinding_results.sigma, atol=0, rtol=0.1)
        if simulation.pi is not None:
            np.testing.assert_allclose(unbounded_results.pi, unbinding_results.pi, atol=0, rtol=0.1)


@pytest.mark.usefixtures('simulated_problem')
def test_extra_nodes(simulated_problem):
    """Test that agents in a simulated problem are identical to agents in a problem created with agent data built
    according to the same integration specification but containing unnecessary columns of nodes.
    """
    simulation, product_data, problem1, _ = simulated_problem

    # reconstruct the problem with unnecessary columns of nodes
    agent_data2 = {k: simulation.agent_data[k] for k in simulation.agent_data.dtype.names}
    agent_data2['nodes'] = np.c_[agent_data2['nodes'], agent_data2['nodes']]
    problem2 = Problem(problem1.product_formulations, product_data, problem1.agent_formulation, agent_data2)

    # test that the agents are essentially identical
    for key in problem1.agents.dtype.names:
        if np.issubdtype(problem1.agents.dtype[key], options.dtype):
            values1 = problem1.agents[key]
            values2 = problem2.agents[key]
            np.testing.assert_allclose(values1, values2, atol=1e-14, rtol=0, err_msg=key)


@pytest.mark.usefixtures('simulated_problem')
def test_extra_demographics(simulated_problem):
    """Test that agents in a simulated problem are identical to agents in a problem created with agent data built
    according to the same integration specification and but containing unnecessary rows of demographics.
    """
    simulation, product_data, problem1, _ = simulated_problem

    # skip simulations without demographics
    if simulation.D == 0:
        return

    # reconstruct the problem with unnecessary rows of demographics
    problem2 = Problem(
        problem1.product_formulations,
        product_data,
        problem1.agent_formulation,
        {k: np.r_[simulation.agent_data[k], simulation.agent_data[k]] for k in simulation.agent_data.dtype.names},
        simulation.integration
    )

    # test that the agents are essentially identical
    for key in problem1.agents.dtype.names:
        if np.issubdtype(problem1.agents.dtype[key], options.dtype):
            values1 = problem1.agents[key]
            values2 = problem2.agents[key]
            np.testing.assert_allclose(values1, values2, atol=1e-14, rtol=0, err_msg=key)


@pytest.mark.usefixtures('simulated_problem')
@pytest.mark.parametrize('solve_options', [
    pytest.param({}, id="default"),
    pytest.param({'linear_fp': False}, id="nonlinear fixed point")
])
def test_objective_gradient(simulated_problem, solve_options):
    """Implement central finite differences in a custom optimization routine to test that analytic gradient values
    are within 1% of estimated values.
    """
    simulation, _, problem, _ = simulated_problem

    # define a custom optimization routine that tests central finite differences around starting parameter values
    def test_finite_differences(*args):
        theta, _, objective_function, _ = args
        exact = objective_function(theta)[1]
        estimated = np.zeros_like(exact)
        change = np.sqrt(np.finfo(np.float64).eps)
        for index in range(theta.size):
            theta1 = theta.copy()
            theta2 = theta.copy()
            theta1[index] += change / 2
            theta2[index] -= change / 2
            estimated[index] = (objective_function(theta1)[0] - objective_function(theta2)[0]) / change
        np.testing.assert_allclose(exact, estimated, atol=0, rtol=0.001)
        return theta, True

    # test the gradient at parameter values slightly different from the true ones so that the objective is sizable
    problem.solve(
        0.9 * simulation.sigma,
        0.9 * simulation.pi if simulation.pi is not None else None,
        steps=1,
        linear_costs=simulation.linear_costs,
        optimization=Optimization(test_finite_differences),
        iteration=Iteration('squarem', {'tol': 1e-15 if solve_options.get('linear_fp') is False else 1e-14}),
        **solve_options
    )


@pytest.mark.usefixtures('knittel_metaxoglou_2014')
def test_knittel_metaxoglou_2014(knittel_metaxoglou_2014):
    """Replicate estimates created by replication code for Knittel and Metaxoglou (2014)."""
    results = knittel_metaxoglou_2014['problem'].solve(
        knittel_metaxoglou_2014.get('initial_sigma'),
        knittel_metaxoglou_2014.get('initial_pi'),
        optimization=Optimization('knitro', {'opttol': 1e-8, 'xtol': 1e-8}),
        iteration=Iteration('simple', {'tol': 1e-12}),
        steps=1
    )

    # test closeness of primary results
    for key, expected in knittel_metaxoglou_2014.items():
        computed = getattr(results, key, None)
        if isinstance(computed, np.ndarray):
            np.testing.assert_allclose(expected, computed, atol=1e-8, rtol=1e-5, err_msg=key)

    # structure post-estimation outputs
    elasticities = results.compute_elasticities()
    changed_prices = results.solve_approximate_merger()
    changed_shares = results.compute_shares(changed_prices)
    post_estimation = {
        'elasticities': elasticities,
        'costs': results.compute_costs(),
        'changed_prices': changed_prices,
        'changed_shares': changed_shares,
        'own_elasticities': results.extract_diagonals(elasticities),
        'profits': results.compute_profits(),
        'changed_profits': results.compute_profits(changed_prices, changed_shares),
        'consumer_surpluses': results.compute_consumer_surpluses(),
        'changed_consumer_surpluses': results.compute_consumer_surpluses(changed_prices)
    }

    # test closeness of post-estimation outputs
    for key, computed in post_estimation.items():
        expected = knittel_metaxoglou_2014[key]
        np.testing.assert_allclose(expected, computed, atol=1e-8, rtol=1e-4, err_msg=key)
