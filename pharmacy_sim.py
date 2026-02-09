import simpy
import numpy as np
import pandas as pd
import itertools
from distributions import (
    Exponential,
    Lognormal,
    Weibull,
    Uniform,
    Bernoulli
)

# -----------------------------------------------------------------------------------------------
# Simulation constants
VERBOSE = False
SEED = 42
N_RNG_STREAMS = 5

# Customer arrivals - exponentional distribution
ARRIVAL_LAMBDA = 1.6

# Service time - lognormal distribution
SERVICE_MU = 1.25
SERVICE_SIGMA = 0.25

# Customer patience - Weibull distribution
PATIENCE_SHAPE = 4.5
PATIENCE_SCALE = 6

# Choise parameters - Uniform distribution
CHOICE_LOW = 1
CHOICE_HIGH = 3
CHOICE_P = 0.6 # prescription chance

# Travel time parameters - Constant value + Uniform noise
TRAVEL_TIME = 30
TRAVEL_NOISE = 10

STOCK_INIT = 250 # Initial medicine stock for each medicine type
N_COUNTERS = 3 

MED_THRESH = 100
RESTOCK_CHECK_INTERVAL = 30

# Time constants
SIM_HOURS = 24
SIM_TIME = SIM_HOURS * 60 # total simulation time in minutes
WARMUP_TIME = 60 # additional time for warming up the simulation

# -----------------------------------------------------------------------------------------------

class Experiment:
    """Pharmacy simulation experiment configuration and execution.
    This class manages the setup and execution of the DES.
    
    Attributes
    ----------
    seed : int
        Random seed for reproducibility.
    n_rng_streams : int
        Number of independent random number streams.
    n_counters : int
        Number of service counters in the pharmacy.
    med_thresh : int
        Restock threshold for medicine inventory.
    stock_init : int
        Initial and maximum stock level for each medicine type.
    arrival_lambda : float
        Rate parameter for exponential customer arrival distribution.
    service_mu : float
        Mean parameter for lognormal service time distribution.
    service_sigma : float
        Std dev parameter for lognormal service time distribution.
    patience_shape : float
        Shape parameter for Weibull patience distribution.
    patience_scale : float
        Scale parameter for Weibull patience distribution.
    choice_low : int
        Lower bound for uniform medicine quantity distribution.
    choice_high : int
        Upper bound for uniform medicine quantity distribution.
    choice_p : float
        Probability of prescription medicine choice.
    travel_time : float
        Base travel time for restocking deliveries.
    travel_noise : float
        Maximum noise added to travel time. Generated as Uniform(-travel_noise, +travel_noise).
    results : dict
        Dictionary storing simulation results.
    """
    
    def __init__(
        self, 
        seed = SEED,
        n_rng_streams = N_RNG_STREAMS,
        n_counters = N_COUNTERS,
        med_thresh = MED_THRESH,
        stock_init = STOCK_INIT,
        arrival_lambda = ARRIVAL_LAMBDA,
        service_mu = SERVICE_MU,
        service_sigma = SERVICE_SIGMA,
        patience_shape = PATIENCE_SHAPE,
        patience_scale = PATIENCE_SCALE,
        choice_low = CHOICE_LOW,
        choice_high = CHOICE_HIGH,
        choice_p = CHOICE_P,
        travel_time = TRAVEL_TIME,
        travel_noise = TRAVEL_NOISE,
        restock_check_interval = RESTOCK_CHECK_INTERVAL
    ):
        self.seed = seed
        self.n_rng_streams = n_rng_streams
        self.n_counters = n_counters
        self.med_thresh = med_thresh
        self.stock_init = stock_init
        self.arrival_lambda = arrival_lambda
        self.service_mu = service_mu
        self.service_sigma = service_sigma
        self.patience_shape = patience_shape
        self.patience_scale = patience_scale
        self.choice_low = choice_low
        self.choice_high = choice_high
        self.choice_p = choice_p
        self.travel_time = travel_time
        self.travel_noise = travel_noise
        self.restock_check_interval = restock_check_interval
        
        self.counters = None
        self.otc_stock = None
        self.prescription_stock = None
        
        self.init_results_vars()
        self.init_sampling()
        
    def set_seed(self, seed):
        """Set the random seed and reinitialize sampling distributions.
        
        Parameters
        ----------
        seed : int
            The random seed to use for all RNG streams.
        """
        self.seed = seed
        self.init_sampling()
        
    def init_sampling(self):
        """Initialize all random number generators and sampling distributions.
        
        Creates independent RNG streams for arrival times, service times,
        customer patience, medicine choice, and travel times using numpy's
        SeedSequence.
        """
        seed_sequence = np.random.SeedSequence(self.seed)
        self.seeds = seed_sequence.spawn(self.n_rng_streams)
        
        self.arrival_dist = Exponential(1/self.arrival_lambda, self.seeds[0])
        self.service_dist = Lognormal(self.service_mu, self.service_sigma, self.seeds[1])
        self.patience_dist = Weibull(self.patience_shape, self.patience_scale, self.seeds[2])
        self.choice_rng = Uniform(self.choice_low, self.choice_high, self.seeds[3])
        self.med_choice_rng = Bernoulli(self.choice_p, self.seeds[3])
        self.travel_dist = Uniform(-self.travel_noise, self.travel_noise, self.seeds[4])
        
    def init_results_vars(self):
        """Initialize or reset results tracking variables.
        
        Creates empty containers for queue waiting times, service times,
        and counters for reneging customers and total arrivals.
        """
        self.results = {}
        self.results["queue_waiting_times"] = []
        self.results["total_service_time"] = 0.0
        self.results["total_leavers"] = 0
        self.results["total_customers"] = 0
        
        
        
def log(msg):
    """Print a debug message if verbose mode is enabled.
    
    Parameters
    ----------
    msg : str
        The message to print.
    """
    if VERBOSE:
        print(msg)
        
        
def restock(med_info, env, args):
    """Process a medicine restock delivery.
    
    Simulates travel time for restocking and updates the appropriate
    medicine inventory container upon arrival.
    
    Parameters
    ----------
    med_info : dict
        Dictionary with 'med_type' (0=OTC, 1=prescription) and 'quantity'.
    env : simpy.Environment
        The simulation environment.
    args : Experiment
        The experiment instance containing distributions and containers.
    """
    travel_time = args.travel_time + args.travel_dist.sample()
    yield env.timeout(travel_time)
    log(f"Restock arrived. Travel time: {travel_time:.2f}")
    if med_info["med_type"] == 0:
        yield args.otc_stock.put(med_info["quantity"])
        log(f"{env.now:.2f}: Restocked {med_info['quantity']} OTC medicines.")
    else:
        yield args.prescription_stock.put(med_info["quantity"])
        log(f"{env.now:.2f}: Restocked {med_info['quantity']} prescription medicines.")
       
        
def restock_check(env, args):
    """Continuously monitor and request medicine restocking.
    
    Checks inventory levels every `args.restock_check_interval` minutes and initiates restock
    processes when inventory falls below the threshold.
    
    Parameters
    ----------
    env : simpy.Environment
        The simulation environment.
    args : Experiment
        The experiment instance containing stock levels and thresholds.
    """
    while True:
        if args.otc_stock.level <= args.med_thresh:
            med_info = {
                "med_type": 0,
                "quantity": args.stock_init - args.otc_stock.level
            }
            log(f"{env.now:.2f}: Restock requested for OTCs!")
            yield env.process(restock(med_info, env, args))
            
        elif args.prescription_stock.level <= args.med_thresh:
            med_info = {
                "med_type": 1,
                "quantity": args.stock_init - args.prescription_stock.level
            }
            log(f"{env.now:.2f}: Restock requested for Prescriptions!")
            yield env.process(restock(med_info, env, args))
            
        yield env.timeout(args.restock_check_interval) 
        
        
def customer(id, patience, med_info, env, args):
    """Simulate a customer's journey through the pharmacy.
    
    Handles queue arrival, waiting with reneging, service at
    the counter, medicine dispensing.
    
    Parameters
    ----------
    id : int
        Unique customer identifier.
    patience : float
        Maximum time (in minutes) the customer will wait in queue before reneging.
    med_info : dict
        Dictionary with 'med_type' (0=OTC, 1=prescription) and 'quantity'.
    env : simpy.Environment
        The simulation environment.
    args : Experiment
        The experiment instance containing resources and distributions.
    """
    log(f"{env.now:.2f}: Customer #{id} arrived at the pharmacy.")
    start_queue_wait = env.now
  
    with args.counters.request() as req:
        result = yield req | env.timeout(patience)
        
        if req not in result:
            log(f"{env.now:.2f}: Customer #{id} left after waiting too long (waited for {(env.now - start_queue_wait):.2f} minutes).")
            args.results["total_leavers"] += 1
            return
        
        queue_waiting_time = env.now - start_queue_wait
        args.results["queue_waiting_times"].append(queue_waiting_time)
        log(f"{env.now:.2f}: Customer #{id} is at the counter and is being serviced. Queue wait time: {queue_waiting_time:.2f}")
        
        if med_info["med_type"] == 0:
           yield  args.otc_stock.get(med_info["quantity"])
        else:
           yield args.prescription_stock.get(med_info["quantity"])
        
        service_duration = args.service_dist.sample()    
        yield env.timeout(service_duration)
        
        args.results["total_service_time"] += service_duration
        
        log(f"{env.now:.2f}: Customer #{id} has received their medication and left. Service time: {service_duration:.2f}")
        
 
def generate_customers(env, args):
    """Generate customer arrivals throughout the simulation.
    
    Continuously creates customers with exponentially distributed inter-arrival
    times. Each customer's patience, medicine type, and quantity are sampled
    from their respective distributions.
    
    Parameters
    ----------
    env : simpy.Environment
        The simulation environment.
    args : Experiment
        The experiment instance containing arrival and choice distributions.
    """
    for customer_count in itertools.count(start=1):
        args.results["total_customers"] += 1
        inter_arrival_time = args.arrival_dist.sample()
        yield env.timeout(inter_arrival_time)
        patience = args.patience_dist.sample()
        med_type = args.med_choice_rng.sample()  # 0 (OTC) or 1 (prescription)
        quantity = int(args.choice_rng.sample()) 
        med_info = {
            "med_type": med_type,
            "quantity": quantity
        }
        env.process(customer(customer_count, patience, med_info, env, args)) 
        
        
def warmup(warmup_time, env, args):
    """Execute the warmup phase to reach steady state.
    
    Runs the simulation for a specified warmup period, then resets
    results tracking to exclude warmup data.
    
    Parameters
    ----------
    warmup_time : float
        Duration of warmup period in minutes.
    env : simpy.Environment
        The simulation environment.
    args : Experiment
        The experiment instance whose results will be reset.
    """
    yield env.timeout(warmup_time)
    log(f"{env.now:.2f}: --- Warm up complete. ---")
    args.init_results_vars()
    
    
def run(experiment, rep=SEED, stock_init=STOCK_INIT, warmup_time=WARMUP_TIME, sim_time=SIM_TIME):
    """Execute a single simulation run.
    
    Initializes the simulation environment, runs the simulation,
    computes performance metrics.
    
    Parameters
    ----------
    experiment : Experiment
        The experiment configuration object.
    rep : int, optional
        Random seed for this run (default: SEED).
    stock_init : int, optional
        Initial stock level for medicine (default: STOCK_INIT).
    warmup_time : float, optional
        Warmup period duration in minutes (default: WARMUP_TIME).
    sim_time : float, optional
        Actual simulation time in minutes (default: SIM_TIME).
    
    Returns
    -------
    dict
        Dictionary containing computed metrics:
        - 'mean_queue_waiting_time': Average customer queue wait time
        - 'counter_util': Counter utilization percentage
        - 'reneging_rate': Percentage of customers who left without service
    """
    run_results = {}
    experiment.init_results_vars()
    experiment.set_seed(rep)
    env = simpy.Environment()
    experiment.otc_stock = simpy.Container(env, stock_init, stock_init)
    experiment.prescription_stock = simpy.Container(env, stock_init, stock_init)
    experiment.counters = simpy.Resource(env, capacity=experiment.n_counters)
    env.process(generate_customers(env, experiment))
    env.process(restock_check(env, experiment))
    env.process(warmup(warmup_time, env, experiment))
    env.run(until=warmup_time+sim_time)
    
    run_results["mean_queue_waiting_time"] = np.mean(experiment.results["queue_waiting_times"]) if experiment.results["queue_waiting_times"] else 0
    run_results["counter_util"] = (experiment.results["total_service_time"] / (sim_time * experiment.n_counters)) * 100
    run_results["reneging_rate"] = experiment.results["total_leavers"] / experiment.results["total_customers"] * 100
    
    return run_results


def n_runs(experiment, warmup_time=WARMUP_TIME, sim_time=SIM_TIME, n=10):
    """Execute multiple independent simulation runs.
    
    Runs the simulation n times with different random seeds and aggregates
    results into a pandas DataFrame.
    
    Parameters
    ----------
    experiment : Experiment
        The experiment configuration object.
    warmup_time : float, optional
        Warmup period duration in minutes (default: WARMUP_TIME).
    sim_time : float, optional
        Actual simulation time in minutes (default: SIM_TIME).
    n : int, optional
        Number of independent runs (default: 10).
    
    Returns
    -------
    pd.DataFrame
        Results dataframe with rows indexed by run number (1 to n),
        columns for each metric computed by run().
    """
    results = [
        run(experiment=experiment, rep=rep, warmup_time=warmup_time, sim_time=sim_time)
        for rep in range(n)
    ]
    
    df_results = pd.DataFrame(results)
    df_results.index = np.arange(1, len(df_results)+1)
    df_results.index.name = "run"
    return df_results       