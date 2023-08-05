

class Pool:

  def __init__(self, config = {}):
    self._models = {}
    self._config = config

  def get(self, model_class):
    if model_class not in self._models:
      self._create_model(model_class)
    return self._models[model_class]

  def add_model(self, cls, model):
    self._models[cls] = model

  def _create_model(self, model_class):
    model = model_class.create(self, self._config)
    self.add_model(model_class, model)

  def __contains__(self, model_class):
    return model_class in self._models


DEFAULT_POOL_NAME = 'global'


shared_pools = {
    DEFAULT_POOL_NAME: Pool()
}


def configure(config, poolname=DEFAULT_POOL_NAME):
  """Sets the configuration for the global pool.

  NOTE: if the global pool has been used, this is a *destructive* operation
  and will create an entirely new pool. This is necessary to ensure that all
  objects created from the pool will be consistent with the new config.

  :param  config:   a dictionary containing the configuration parameters
  :param  poolname: which pool to configure (defaults to the global pool)
  """
  global shared_pools
  pool = Pool(config)
  shared_pools[poolname] = pool


def get(poolname=DEFAULT_POOL_NAME):
  """Gets a pool with the specified name, or the global pool."""
  global shared_pools
  return shared_pools[poolname]

