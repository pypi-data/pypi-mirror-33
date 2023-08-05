from matplotlib import pyplot as plt
import pandas
from sklearn.cluster import DBSCAN
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.datasets.samples_generator import make_blobs
import csv
import os
import shutil
import sys

class DBSCANWorker(object):
    """
    Cluster worker
    """

    def __init__(self, eps, min_samples):
        self.db = DBSCAN(eps=eps, min_samples=min_samples, n_jobs=-1)

    def fit(self, X) -> DBSCAN:
        """

        :param X: list[float]
        :return:
        """
        return self.db.fit(X)

    def labels(self):
        return self.db.labels_


def cluster_worker_factory(eps, min_samples):
    return DBSCAN(eps, min_samples)



