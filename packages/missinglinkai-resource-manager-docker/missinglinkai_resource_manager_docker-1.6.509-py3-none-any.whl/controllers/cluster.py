import logging
import uuid


def init_from_config(conf):
    id_ = conf.general.get('cluster_id')
    if id_ is None:
        id_ = uuid.uuid4().hex
        logging.info('Setting Cluster ID to %s', id_)
        conf.general.cluster_id = id_
        conf.general.save()
