from PIL import Image
from torchvision import transforms
from torchvision.datasets.utils import download_url, check_integrity

import numpy as np
import os
import tempfile
import torch.utils.data as data


class DSprites(data.Dataset):
    """
    A Dataset of 64x64 b/w images of simple shapes (elipse, heart, square) that are translated, scaled and rotated.
    The dataset is better described `here <https://github.com/deepmind/dsprites-dataset>`_.

    Arguments:
        root (string): Root directory of dataset where directory
            ``cifar-10-batches-py`` exists or will be saved to if download is set to True.
        transform (callable, optional): A function/transform that  takes in an PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        download (bool, optional): If true, downloads the dataset from the internet and
            puts it in root directory. If dataset is already downloaded, it is not
            downloaded again.

    New in 1.3.0
    """
    url = ("https://github.com/deepmind/dsprites-dataset/blob/master/"
           "dsprites_ndarray_co1sh3sc6or40x32y32_64x64.npz?raw=true")
    filename = "dsprites_ndarray_co1sh3sc6or40x32y32_64x64.npz"
    md5 = "7da33b31b13a06f4b04a70402ce90c2e"
    image_size = (64, 64)

    def __init__(self, transform=transforms.ToTensor(), target_transform=None, root=None, download=True):
        if root is None:
            root = os.path.join(tempfile.gettempdir(), self.__class__.__name__)

        self.root = root
        self.transform = transform
        self.target_transform = target_transform
        self.download = download

        if download:
            self._download()

        self._load()

    def _download(self):
        if self._check_integrity():
            return
        else:
            download_url(self.url, self.root, self.filename, self.md5)

    @property
    def raw_data_path(self):
        return os.path.join(self.root, self.filename)

    def _load(self):
        if not self._check_integrity():
            raise RuntimeError('Dataset not found or corrupted.' +
                               ' You can use download=True to download it')

        # Load dataset
        dataset_zip = np.load(self.raw_data_path)

        self.samples = dataset_zip['imgs']
        self.target_units = dataset_zip['latents_values']
        self.targets = dataset_zip['latents_classes']

    def _check_integrity(self):
        path = os.path.join(self.root, self.filename)
        return check_integrity(path, self.md5)

    def __getitem__(self, index):
        """
        Args:
            index (int): Index

        Returns:
            tuple: (sample, target) where sample is the image, and target is the
                (color, shape, scale, orientation, x-position, y-position) of the sprite in the image.
        """
        sample = Image.fromarray(self.samples[index] * 255)
        if self.transform is not None:
            sample = self.transform(sample)

        target = self.targets[index]
        if self.target_transform is not None:
            target = self.target_transform(target)

        return sample, target

    def __len__(self):
        return len(self.samples)

    def __repr__(self):
        fmt_str = 'dSprites Dataset\n'
        fmt_str += f'    Size of images: 64x64\n'
        fmt_str += f'    Number of images: {len(self)}\n'
        return fmt_str
