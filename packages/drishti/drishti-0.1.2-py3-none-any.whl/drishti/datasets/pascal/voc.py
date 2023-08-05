import glob
import os

import untangle
from tqdm import tqdm

from drishti.datasets.bbox import BBox
from drishti.datasets.image import Image
from drishti.datasets.object_dataset import ObjectDataset


class PascalVOC(ObjectDataset):
    """ This class serves as a standard way of accessing the pascal object detection datasets,
    along with various plotting routines for visibility.

    The dataset can be downloaded from:
        https://pjreddie.com/projects/pascal-voc-dataset-mirror/

    @:param
        path: The path on the disk where the extracted PascalVOC dataset is present.
        e.g - ~/data/VOCdevkit/VOC2007.

    """
    ANNOTATIONS, JPEGImages, extn = ['Annotations', 'JPEGImages', '*.xml']

    def __init__(self, path, disable_progressbar=False):
        super().__init__(path, disable_progressbar)

    def prepare_dataset(self):
        """ Parse the annotations of all the images in the dataset
            and prepare the dataset for training using various algorithms. """
        print('Processing dataset ... ')
        for f in tqdm(glob.glob(os.path.join(self.path, PascalVOC.ANNOTATIONS, PascalVOC.extn)),
                      disable=self.disable_progressbar):
            filename = os.path.split(f)[-1]
            self.data.append(self.parse_annotation(filename))

    def parse_annotation(self, xml_file):
        """ Parse the xml file in PascalVOC for training/plotting etc.

        :param xml_file: filename of xml to be parsed.
        :return: Drishti's Image object with filename and bounding box information.
        """
        obj = untangle.parse(os.path.join(self.path, PascalVOC.ANNOTATIONS, xml_file))
        filename = obj.annotation.filename.cdata
        bboxes = self.extract_bboxes(obj)
        return Image(path=os.path.join(self.path, PascalVOC.JPEGImages, filename), bboxes=bboxes)

    def extract_bboxes(self, obj):
        """ Parse the Pascal Bounding Box to Drishti's bounding box object format."""
        boxes = list()
        for box in obj.annotation.object:
            bbox = BBox(float(box.bndbox.ymin.cdata), float(box.bndbox.xmin.cdata), float(box.bndbox.ymax.cdata),
                        float(box.bndbox.xmax.cdata), box.name.cdata)
            boxes.append(bbox)
        return boxes


if __name__ == '__main__':
    voc_path = input('Enter path for Pascal VOC dataset: ')
    PV = PascalVOC(voc_path)
    PV.prepare_dataset()
    PV.plot_image(789)