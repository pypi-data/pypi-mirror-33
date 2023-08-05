import csv
import os

import numpy as np
import pandas
from keras import applications
from keras.applications.resnet50 import preprocess_input
from keras.preprocessing import image
from keras.engine.training import Model


class ModelWorker(object):
    """
    Given an image as a pixels array and a model, ouput the extracted features
    """

    def __init__(self, model: Model, verbose: bool=False):
        """
        :param img_path:
        :param model:
        :param verbose:
        """
        self.model = model
        self.verbose = verbose

    def extract_feature(self, img_path: str) -> list[float]:
        """

        :return: the extracted feature array of the given image.
        :rtype list[double]
        """
        # Load the image as the size of 224 x 224
        # TODO: Adjust img size by selected model input requirements
        img = image.load_img(img_path, target_size=(224, 224))


        # Convert image to numpy array
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)

        # Extract the features
        features = self.model.predict(x)

        features = features[0]

        # Convert from np array to list[float]
        res = np.char.mod('%f', features)

        if self.verbose:
            print("[ExtractFeature] Predict feature shape: %d, %d" % (features.shape[0], features.shape[1]))
            print(len(res))

        return res


def __get_model(model: str):
    # include_top=False removes the fully connected layer at the end/top of the network
    # This allows us to get the feature vector as opposed to a classification
    if model == 'Xception':
        return applications.xception.Xception(weights='imagenet', include_top=False, pooling='avg')

    if model == 'VGG16':
        return applications.vgg16.VGG16(weights='imagenet', include_top=False, pooling='avg')

    if model == 'VGG19':
        return applications.vgg19.VGG19(weights='imagenet', include_top=False, pooling='avg')

    if model == 'InceptionV3':
        return applications.inception_v3.InceptionV3(weights='imagenet', include_top=False, pooling='avg')

    if model == 'MobileNet':
        return applications.mobilenet.MobileNet(weights='imagenet', include_top=False, pooling='avg')

    return applications.resnet50.ResNet50(weights='imagenet', include_top=False, pooling='avg')


def extract_worker_factory(model: str="ResNet50", verbose=False) -> ModelWorker:
    """
    :param model: the name of pre-trained model to use
    :return:
    """
    model = __get_model(model)
    return ModelWorker(model, verbose)