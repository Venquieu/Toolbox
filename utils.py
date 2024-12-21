from typing import Union, List, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm


class Struct(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @property
    def map(self):
        return self.__dict__
    
    @property
    def attri(self):
        return list(self.__dict__.keys())
    
    def __repr__(self):
        return str(self.__dict__)


def run_parallel(func: Any, args_list: Union[List, Tuple], max_workers:int = 32):
    """"
    Run a function in parallel using ThreadPoolExecutor.

    Args:
        func (Any): The function to be executed in parallel.
        args_list (Union[List, Tuple]): A list or tuple of arguments to be passed to the function.
        max_workers (int, optional): The maximum number of workers to use. Defaults to 32.

    Returns:
        List: A list of results returned by the function for each argument in the args_list.
    """
    max_workers = min(max_workers, len(args_list))
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(func, *args) for args in args_list]
        for future in tqdm(as_completed(futures), total=len(futures)):
            results.append(future.result())
    return results
