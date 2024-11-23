import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import csv
from mesa.batchrunner import batch_run
from model import ForestFire

"""Batch run a mesa model with a set of parameter values.

    Args:
        model_cls (Type[Model]): The model class to batch-run
        parameters (Mapping[str, Union[Any, Iterable[Any]]]): Dictionary with model parameters over which to run the model. You can either pass single values or iterables.
        number_processes (int, optional): Number of processes used, by default 1. Set this to None if you want to use all CPUs.
        iterations (int, optional): Number of iterations for each parameter combination, by default 1
        data_collection_period (int, optional): Number of steps after which data gets collected, by default -1 (end of episode)
        max_steps (int, optional): Maximum number of model steps after which the model halts, by default 1000
        display_progress (bool, optional): Display batch run process, by default True

    Returns:
        List[Dict[str, Any]]

    Notes:
        batch_run assumes the model has a `datacollector` attribute that has a DataCollector object initialized.

    To take advantage of parallel execution of experiments, `batch_run` uses
    multiprocessing if ``number_processes`` is larger than 1. It is strongly advised
    to only run in parallel using a normal python file (so don't try to do it in a
    jupyter notebook). Moreover, best practice when using multiprocessing is to
    put the code inside an ``if __name__ == '__main__':`` code black as shown below::

    from mesa.batchrunner import batch_run

    params = {"width": 10, "height": 10, "N": range(10, 500, 10)}

    if __name__ == '__main__':
        results = batch_run(
            MoneyModel,
            parameters=params,
            iterations=5,
            max_steps=100,
            number_processes=None,
            data_collection_period=1,
            display_progress=True,
        )

        
"""

params = {
    "height": 100,
    "width": 100,
    "tree_density": 0,
    "cloud_quantity": 0,
    "rainy_season": False,
    'biome_name': "Default",
    "random_fire" : True,
    "position_fire":'Top',
    "cloud_step":15,
    'clouds_per_step':0,
    'clouds_size':3,
    "reprod_speed":1,
    "water_density":0.15,
    "num_of_lakes": 1,
    "corridor_density":0.15,
    "obstacles_density":0.15,
    "obstacles":True,
    "obstacles":True,
    "wind_intensity":True,
}

if __name__ == "__main__":
    results = batch_run(
        ForestFire,
        parameters=params,
        iterations=100,
        max_steps=100,
        number_processes=None,
        data_collection_period=1,
        display_progress=True,
    )

    keys = results[0].keys() if results else []

    with open("data.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)

# creditos ao Vinicius Maciel 