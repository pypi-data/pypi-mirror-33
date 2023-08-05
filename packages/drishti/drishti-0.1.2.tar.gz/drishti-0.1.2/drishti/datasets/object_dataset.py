import cv2
import matplotlib.patches as patches
import matplotlib.patheffects as patheffects
import matplotlib.pyplot as plt


class ObjectDataset:
    """ This class serves as the base class for object detection datasets.
    It also contains methods for plotting the images and their corresponding
    bounding boxes with labels.

    @:param
        path: the path to the dataset
        disable_progressbar : Optional flag to disable the progressbar, if any.
    """
    def __init__(self, path, disable_progressbar=False):
        self.path = path
        self.data = list()
        self.disable_progressbar = disable_progressbar

    def get_images(self):
        """ Get the entire dataset as an array of objects """
        return self.data

    @staticmethod
    def load_image(filename):
        """ Use opencv to load the image """
        return cv2.cvtColor(cv2.imread(filename), cv2.COLOR_BGR2RGB)

    @staticmethod
    def draw_outline(o, lw):
        """This plotting routine has been taken from Jeremy Howard's lectures"""
        o.set_path_effects([patheffects.Stroke(
            linewidth=lw, foreground='black'), patheffects.Normal()])

    @staticmethod
    def draw_label(bboxes, ax):
        """ Draw the labels from the dataset.

        :param bboxes: List of BBox objects
        :param ax: Matplotlib axes object (mandatory parameter)
        :return: None
        """
        labels = list()
        for box in bboxes:
            text = ax.text(box.c1, box.r1, box.label, verticalalignment='top', color='white')
            ObjectDataset.draw_outline(text, 1)

    @staticmethod
    def draw_bbox(bboxes):
        """ Draw bounding boxes around objects to be detected.
        :param   bboxes:
        :return: Rectange patches for matplotblib axes
        """
        rects = list()
        for box in bboxes:
            rect = patches.Rectangle((box.c1, box.r1), box.c2 - box.c1, box.r2 - box.r1,
                                     linewidth=1, edgecolor='white', facecolor='none')
            ObjectDataset.draw_outline(rect, 4)
            rects.append(rect)
        return rects

    def plot_image(self, index, ax=None, bbox=None):
        """ Plot the image and its corresponding bounding boxes with labels using matplotlib
        @:param
            index : The index position in the dataset array
            ax : Matplotlib axes object, if none provided, this method will create the axes
                and figure and plot them. If ax is not None, it will be used to add the plot
                with no further action
            bbox (optional) : list of bounding box objects to be plotted on the image,
                if none, then dataset is used to compute.
        """
        img = self.data[index]
        img_data = self.load_image(img.path)
        standalone = False
        if ax is None:
            standalone = True
            fig, ax = plt.subplots()
        ax.imshow(img_data)

        if bbox is None: bbox = img.bboxes
        rects = self.draw_bbox(bbox)
        self.draw_label(bbox, ax)
        for rect in rects:
            ax.add_patch(rect)

        if standalone: fig.show()
