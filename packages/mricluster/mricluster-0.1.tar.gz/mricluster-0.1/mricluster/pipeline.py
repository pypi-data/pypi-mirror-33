from mricluster.extractor import extract_worker_factory
from mricluster.reduce import reduce_worker_factory
from mricluster.cluster import cluster_worker_factory

import os
from multiprocessing import Process, Pool
import multiprocessing


class PipeLineMaser(object):
    """
    Note:
        Use this class with Tensorflow-CPU version as backend.
        Not compatible with Tensorflow-GPU version.
    """
    def __init__(self, query_dir, out_dir):
        """
        
        :param query_dir: The directory that contains the query images
        :param out_dir: The direcotry that outputs the result
        """
        self.train_set = self.populate_train_set(query_dir)
        self.out_dir = out_dir

    def populate_train_set(self, query_dir):
        """
        Search through the query directory and collects the image files into
        train data set.
        :param query_dir:
        :return:
        """
        res = []
        for root, dirs, files in os.walk(query_dir):
            for file in files:
                if file.endswith("jpg") or file.endswith("png"):
                    res.append(os.path.join(root, file))
        return res

    def pipe_line_worker(self, workload, verbose):

        extractWorker = extract_worker_factory(verbose=verbose)

        if verbose:
            print("[PipWorker] (pid=%d) Instantiate extract worker. workload: %d"
                  % (multiprocessing.current_process().pid, len(workload)))

        res = []
        for img in workload:
            features = extractWorker.extract_feature(img)
            res.append(features)

        return res


    def run(self, n_worker=-1, verbose=False):
        """

        :param n_worker:
        :return:
        """

        # Default setting: let number of workers equal to number of cpus
        if n_worker==-1:
            n_worker = multiprocessing.cpu_count()
        
        workload_count = len(self.train_set)

        """
            Extract Features
        """
        # Map
        process_pool = Pool(n_worker)
        extract_feature = process_pool.map(self.pipe_line_worker, self.train_set)

        if verbose:
            print ("Finish extracting features. Result matrix shape: (%d x %d)" % (len(extract_feature), len(extract_feature[0])))

        """
            Dimension Reduction
        """
        # TODO:



        """
            Clustering
        """
        # TODO:


def pipeline(input_dir, output_dir):
    """

    :param input_dir:
    :param output_dir:
    :return:
    """
    return PipeLineMaser(input_dir, output_dir)
