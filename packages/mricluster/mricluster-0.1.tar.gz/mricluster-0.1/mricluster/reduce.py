from sklearn import (
    decomposition,
    manifold,
    pipeline,
)


class ReduceWorker(object):
    """
    Given a high-dimension feature arrays, reduce into low-dimension array
    """

    def __init__(self, model: manifold.TSNE):
        self.model = model

    def reduce(self, data: list[float]):
        """

        :param data: N x 2048 arrays
        :return:
        """
        res = self.model.fit_transform(data)
        return res


def __get_model(model: str, n_component: int):
    """
    PCA: Default n_components=48
    :param model:
    :param n_component: number of components to be reduced to
    :return:
    """
    if model == 'TSNE':
        return manifold.TSNE(random_state=0, verbose=1, n_components=n_component)
    if model == 'PCA-TSNE':
        tsne = manifold.TSNE(
            random_state=0, perplexity=50, early_exaggeration=6.0, n_components=n_component)
        pca = decomposition.PCA(n_components=48)
        return pipeline.Pipeline([('reduce_dims', pca), ('tsne', tsne)])
    if model == 'PCA':
        return decomposition.PCA(n_components=48)
    raise ValueError('Unknown model name')


def reduce_worker_factory(model: str="TSNE", n_component=2):
    """

    :param model: Name of the dimension reduce model. Default 'tSNE'
    :param n_component: number of components to be reduced to
    :return:
    """
    model = __get_model(model, n_component)
    return ReduceWorker(model)