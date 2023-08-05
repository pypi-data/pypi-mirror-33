from abc import ABC, abstractmethod
from typing import List

import modmod.pool
from modmod.pool import DEFAULT_POOL_NAME


class Model(ABC):
  def __init__(self, pool, config) -> None:
    """Store the pool and config by default."""
    self.pool = pool
    self.config = config

  @classmethod
  def create(cls, pool, config) -> 'Model':
    """Creates an instance of this model.

    :param  config: the options for this environment (data location, etc.)
    :return:  an instance of this Model
    """
    return cls(pool, config)

  def __call__(self, *args):
    return self.call(*args)

  @staticmethod
  def _dependencies() -> List['Model']:
    return []

  @classmethod
  def get(cls, poolname: str = DEFAULT_POOL_NAME) -> 'Model':
    """Fetches an instance of this model from the shared pool.

    :param  poolname: which pool to fetch from (defaults to global)
    """
    pool = modmod.pool.get(poolname)
    return pool.get(cls)
