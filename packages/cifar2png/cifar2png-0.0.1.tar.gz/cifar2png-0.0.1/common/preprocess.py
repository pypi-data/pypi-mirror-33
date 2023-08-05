#!/usr/bin/env python
# coding: utf-8

from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
logger.addHandler(handler)
logger.propagate = False

import hashlib
import math
import numpy as np
import os
import six
import sys
import tarfile
import requests

try:
   import cPickle as pickle
except:
   import pickle

from collections import defaultdict
from pathlib import Path
from PIL import Image
from tqdm import tqdm

from common.spinner import Spinner

CIFAR10_URL  = 'https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz'
CIFAR100_URL = 'https://www.cs.toronto.edu/~kriz/cifar-100-python.tar.gz'
CIFAR10_TAR_FILENAME  = 'cifar-10-python.tar.gz'
CIFAR100_TAR_FILENAME = 'cifar-100-python.tar.gz'
CIFAR10_TAR_MD5  = 'c58f30108f718f92721af3b95e74349a'
CIFAR100_TAR_MD5 = 'eb9058c3a382ffc7106e4002c42a8d85'

CIFAR10_TRAIN_DATA_NAMES = [
    'cifar-10-batches-py/data_batch_1',
    'cifar-10-batches-py/data_batch_2',
    'cifar-10-batches-py/data_batch_3',
    'cifar-10-batches-py/data_batch_4',
    'cifar-10-batches-py/data_batch_5'
]
CIFAR10_TEST_DATA_NAMES   = ['cifar-10-batches-py/test_batch']
CIFAR100_TRAIN_DATA_NAMES = ['cifar-100-python/train']
CIFAR100_TEST_DATA_NAMES  = ['cifar-100-python/test']

CIFAR10_LABELS_LIST = [
    'airplane', 'automobile', 'bird', 'cat', 'deer',
    'dog', 'frog', 'horse', 'ship', 'truck'
]
CIFAR100_LABELS_LIST = [
    'apple', 'aquarium_fish', 'baby', 'bear', 'beaver', 'bed', 'bee', 'beetle',
    'bicycle', 'bottle', 'bowl', 'boy', 'bridge', 'bus', 'butterfly', 'camel',
    'can', 'castle', 'caterpillar', 'cattle', 'chair', 'chimpanzee', 'clock',
    'cloud', 'cockroach', 'couch', 'crab', 'crocodile', 'cup', 'dinosaur',
    'dolphin', 'elephant', 'flatfish', 'forest', 'fox', 'girl', 'hamster',
    'house', 'kangaroo', 'keyboard', 'lamp', 'lawn_mower', 'leopard', 'lion',
    'lizard', 'lobster', 'man', 'maple_tree', 'motorcycle', 'mountain', 'mouse',
    'mushroom', 'oak_tree', 'orange', 'orchid', 'otter', 'palm_tree', 'pear',
    'pickup_truck', 'pine_tree', 'plain', 'plate', 'poppy', 'porcupine',
    'possum', 'rabbit', 'raccoon', 'ray', 'road', 'rocket', 'rose', 'sea',
    'seal', 'shark', 'shrew', 'skunk', 'skyscraper', 'snail', 'snake', 'spider',
    'squirrel', 'streetcar', 'sunflower', 'sweet_pepper', 'table', 'tank',
    'telephone', 'television', 'tiger', 'tractor', 'train', 'trout', 'tulip',
    'turtle', 'wardrobe', 'whale', 'willow_tree', 'wolf', 'woman', 'worm'
]


def unpickle(dump):
    if six.PY2:
        data = pickle.loads(dump.read())
    elif six.PY3:
        data = pickle.loads(dump.read(), encoding='latin1')
    return data


def check_output_path(output):
    outputdir = Path(output)
    if outputdir.exists():
        logger.error("output dir `{}` already exists. Please specify a different output path".format(output))
        sys.exit(1)


# Reference: https://stackoverflow.com/questions/37573483/progress-bar-while-download-file-over-http-with-requests/37573701
def download_with_progress(url, filename):
    logger.warning("Downloading {}".format(filename))
    r = requests.get(url, stream=True)
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024
    wrote = 0
    with open(filename, 'wb') as f:
        for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size//block_size) , unit='KB', unit_scale=True):
            wrote = wrote  + len(data)
            f.write(data)
    if total_size != 0 and wrote != total_size:
        logger.error("ERROR, something went wrong")
        sys.exit(1)


def download_cifar(dataset):
    if dataset == 'cifar10':
        download_with_progress(CIFAR10_URL, CIFAR10_TAR_FILENAME)
    elif dataset == 'cifar100':
        download_with_progress(CIFAR100_URL, CIFAR100_TAR_FILENAME)


def check_cifar(dataset):
    if dataset == 'cifar10':
        cifar = Path(CIFAR10_TAR_FILENAME)
        md5sum = CIFAR10_TAR_MD5
    elif dataset == 'cifar100':
        cifar = Path(CIFAR100_TAR_FILENAME)
        md5sum = CIFAR100_TAR_MD5

    if not cifar.is_file():
        logger.warning("{} does not exists.".format(cifar))
        download_cifar(dataset)

    cifar_md5sum = hashlib.md5(cifar.open('rb').read()).hexdigest()
    if md5sum != cifar_md5sum:
        logger.error("File `{0}` may be corrupted (wrong md5 checksum). Please delete `{0}` and retry".format(cifar))
        sys.exit(1)

    return True


def get_data_params(dataset):
    if dataset == 'cifar10':
        TARFILE = CIFAR10_TAR_FILENAME
        label_data = 'data'
        label_labels = 'labels'
    elif dataset == 'cifar100':
        TARFILE = CIFAR100_TAR_FILENAME
        label_data = 'data'
        label_labels = 'fine_labels'
    return TARFILE, label_data, label_labels


def get_datanames(dataset, mode):
    if dataset == 'cifar10':
        if mode == 'train':
            return CIFAR10_TRAIN_DATA_NAMES
        elif mode == 'test':
            return CIFAR10_TEST_DATA_NAMES
    elif dataset == 'cifar100':
        if mode == 'train':
            return CIFAR100_TRAIN_DATA_NAMES
        elif mode == 'test':
            return CIFAR100_TEST_DATA_NAMES


def parse_cifar(dataset, mode):
    features = []
    labels = []

    TARFILE, label_data, label_labels = get_data_params(dataset)
    datanames = get_datanames(dataset, mode)

    try:
        spinner = Spinner(prefix="Loading {} data...".format(mode))
        spinner.start()
        tf = tarfile.open(TARFILE)
        for dataname in datanames:
            ti = tf.getmember(dataname)
            data = unpickle(tf.extractfile(ti))
            features.append(data[label_data])
            labels.append(data[label_labels])
        features = np.concatenate(features)
        features = features.reshape(features.shape[0], 3, 32, 32)
        features = features.transpose(0, 2, 3, 1).astype('uint8')
        labels = np.concatenate(labels)
        spinner.stop()
    except KeyboardInterrupt:
        spinner.stop()
        sys.exit(1)

    return features, labels


def save_cifar(dataset, output):
    if dataset == 'cifar10':
        LABELS = CIFAR10_LABELS_LIST
        LABELS_LIST = CIFAR10_LABELS_LIST
    elif dataset == 'cifar100':
        LABELS = CIFAR100_LABELS_LIST
        LABELS_LIST = CIFAR100_LABELS_LIST

    for mode in ['train', 'test']:
        for label in LABELS:
            dirpath = os.path.join(output, mode, label)
            os.system("mkdir -p {}".format(dirpath))

        features, labels = parse_cifar(dataset, mode)

        label_count = defaultdict(int)
        for feature, label in tqdm(zip(features, labels), total=len(labels), desc="Saving {} images".format(mode)):
            label_count[label] += 1
            filename = '%04d.png' % label_count[label]
            filepath = os.path.join(output, mode, LABELS_LIST[label], filename)
            image = Image.fromarray(feature)
            image = image.convert('RGB')
            image.save(filepath)
