from controllers import configuration


async def init_config():
    from controllers import cluster, docker_controller
    cluster.init_from_config(configuration.active_config)
    docker_controller.init_from_config(configuration.active_config)
    return None


async def init_cluster(config_folder=None):
    configuration.active_config = configuration.ConfigurationInstance(config_folder)
    return await  init_config()
