import os
import logging
import logging.handlers
import base64
import json
import pickle
import numpy as np
from networkn import NdexGraph
root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
log_path = os.path.join(root, 'logs')

def get_logger(name, level=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    logger.handlers = []

    formatter = logging.Formatter('%(asctime)s.%(msecs)d ' + name + ' %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')

    handler = logging.handlers.TimedRotatingFileHandler(os.path.join(log_path, 'app.log'), when='midnight', backupCount=28)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


def load_matrix_to_ndex(X, X_cols, X_rows, server, username, password, name):
    if not isinstance(X, np.ndarray):
        raise Exception('Provided matrix is not of type numpy.ndarray')
    if not isinstance(X_cols, list):
        raise Exception('Provided column header is not in the correct format.  Please provide a list of strings')
    if not isinstance(X_rows, list):
        raise Exception('Provided row header is not in the correct format.  Please provide a list of strings')

    if not X.flags['C_CONTIGUOUS']:
        X = np.ascontiguousarray(X)

    serialized = pickle.dumps(X)  # base64.b64encode(X)

    G_cx = NdexGraph()
    G_cx.unclassified_cx.append(
        {'matrix': [{'v': serialized}]})

    G_cx.unclassified_cx.append(
        {'matrix_cols': [{'v': X_cols}]})

    G_cx.unclassified_cx.append(
        {'matrix_rows': [{'v': X_rows}]})

    G_cx.unclassified_cx.append(
        {'matrix_dtype': [{'v': X.dtype.name}]})

    node_id = G_cx.add_new_node(name=name)
    G_cx.add_edge_between(node_id, node_id)
    G_cx.set_name(name)
    G_cx.set_network_attribute('Description', 'testing sim matrix storage')

    ont_url = G_cx.upload_to(server, username, password)

    return ont_url


def get_matrix_from_ndex(server, username, password, uuid):
    print('place holder')
    X = None
    X_cols = None
    X_rows = None

    if 'http' not in server:
        server = 'http://' + server
    G_cx = NdexGraph(server=server, username=username, password=password, uuid=uuid)

    matrix = __get_v_from_aspect(G_cx, 'matrix')
    binary_data = pickle.loads(matrix)

    matrix_cols = __get_v_from_aspect(G_cx, 'matrix_cols')
    matrix_rows = __get_v_from_aspect(G_cx, 'matrix_rows')
    matrix_dtype = __get_v_from_aspect(G_cx, 'matrix_dtype')

    dtype = np.dtype(matrix_dtype)
    rows = matrix_rows
    cols = matrix_cols
    dim = (len(rows), len(cols))

    # Create a NumPy array, which is nothing but a glorified
    # pointer in C to the binary data in RAM
    X = np.frombuffer(binary_data, dtype=dtype).reshape((15, 15))

    return X, X_cols, X_rows


def __get_v_from_aspect(G, aspect_name):
    for aspect in G.unclassified_cx:
        if aspect.get(aspect_name) is not None:
            aspect_tmp = aspect.get(aspect_name)
            if len(aspect_tmp) > 0:
                return aspect_tmp[0].get('v')

    return None

