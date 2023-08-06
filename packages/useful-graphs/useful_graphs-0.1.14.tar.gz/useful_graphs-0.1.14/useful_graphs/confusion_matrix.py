import numpy as np
import matplotlib.pyplot as plt
import itertools
import math


class ConfusionMatrix:
    """Plot confusion matrix.

    Examples
    --------
    >>> import numpy as np
    >>> cm = np.array([
                        [10, 3, 4],
                        [0, 9, 2],
                        [3, 2, 10],
                    ])
    >>> classes = ['test1', 'test2', 'test3']
    >>> myCM = ConfusionMat()
    >>> myCM.read_cm(cm, class_list=classes)
    >>> myCM.plot(to_normalize=True)
    """
    # define constant
    THRESHOLD = 0.5

    def __init__(self, cm, class_list=None):
        """Initialize method.

        Args:
            cm (2-dimensional numpy array): A confusion matrix which either of columns or rows are true labels, and the other ones are predicted labels. I recommend you to use confusion_matrix method in scikit-learn.
            class_list (list, optional): A list of label names. If not specified, range(len(cm)) will be used for labels.
        """
        self._cm = cm

        if class_list==None:
            self._classes = range(len(cm))
        elif class_list:
            self._classes = class_list

    @property
    def cm(self):
        return self._cm

    def _normalize_cm(self, cm):
        sums = cm.sum(axis=1)[:, np.newaxis]

        return cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

    def _calculate_luminance(self, rgb_tuple):
        """Calculate luminance.

        Note:
            Refered to [https://en.wikipedia.org/wiki/Relative_luminance](https://en.wikipedia.org/wiki/Relative_luminance).
        Args:
            rgb_tuple (tuple): A tuple o rgb color (r_value, g_value, b_value).
        """
        return 0.298912 * rgb_tuple[0] + 0.586611 * rgb_tuple[1] + 0.114478 * rgb_tuple[2]

    def plot(self,
                    to_normalize=False,
                    title=None,
                    to_show_colorbar=True,
                    colorbar_label=None,
                    to_show_label=True,
                    to_show_number_label=False,
                    cmap=plt.cm.Reds,
                    save_path=None,
                    xlabel='Predicted label',
                    ylabel='True label',
                    text_font_size=10,
                    figsize=None):
        """Plot confusion matrix.

        Args:
            to_normalize (bool, optional): If true, normalize confusion matrix for each row. (default False)
            title (str, optional): If specified, set a title to a figure. If none, title is not set. (default None)
            to_show_colorbar (bool, optional): If true, show colorbar to a figure. (default True)
            colorbar_label (str, optional): If specified, show label next to colorbar. (default None)
            to_show_label (bool, optional): If true, show label in a figure. (default True)
            to_show_number_label (bool, optional): If true, show number of data under the label. (default False)
            cmap (matplotlib colormap object, optional): Set colormap. See [matplotlib](https://matplotlib.org/users/colormaps.html) for available colormaps. (default matplotlib.pyplot.cm.Reds)
            save_path (str, optional): If specified, save graph to specified path and not show the graph. (default None)
            xlabel (str, optional): If specified, change xlabel. (default 'Predicted label')
            ylabel (str, optional): If specified, change ylabel.  (default 'True label')
            text_font_size (int, optional): If specified change font size.  (default 10)
            figsize (tuple of shape=(w, h), optional): If specified, change size of a figure to w, h in inches. It changes `figsize` parameter of [matplotlib.figure.Figure](https://matplotlib.org/api/_as_gen/matplotlib.figure.Figure.html#matplotlib-figure-figure). (default None)
        """

        # normalize if to_normalize is True
        if to_normalize:
            cm = self._normalize_cm(self._cm)
        else:
            cm = self._cm

        # set figuresize if specified
        if figsize:
            plt.figure(figsize=figsize)

        plt.imshow(cm, interpolation='nearest', cmap=cmap)

        # set color range when to_normalize is True
        if to_normalize:
            plt.clim(0,100)

        if title:
            plt.title(title, fontsize=15)
        if to_show_colorbar:
            cbar = plt.colorbar()
            if colorbar_label:
                cbar.set_label(colorbar_label)

        labels = np.arange(len(self._classes))
        plt.xticks(labels, self._classes, rotation=45)
        plt.yticks(labels, self._classes)

        plt.xlabel(xlabel, fontsize=13)
        plt.ylabel(ylabel, fontsize=13)

        max_of_cm = cm.max()

        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            if not math.isnan(cm[i, j]):
                if to_normalize:
                    if to_show_number_label:
                        string = '{:.1f}\n({})'.format(cm[i, j], self._cm[i, j])
                    else:
                        string = r'{:.1f}'.format(cm[i, j])
                else:
                    string = '{}'.format(cm[i, j])

                # get color of this cell
                cell_color = cmap(cm[i, j]/max_of_cm)
                rgb_tuple = (cell_color[0], cell_color[1], cell_color[2])
                # calculate luminance
                luminance = self._calculate_luminance(rgb_tuple)

                # set font color
                if luminance < self.THRESHOLD:
                    color = 'white'
                else:
                    color = 'black'

                # Show label if to_show_label is True
                if to_show_label:
                    plt.text(j, i, string,
                             horizontalalignment="center",
                             verticalalignment="center",
                             color=color,
                             fontsize=text_font_size)

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, transparent=True)
        else:
            plt.show()


if __name__ == '__main__':
    cm = np.array([
                     [4, 5, 9, 7, 0, 0],
                     [5, 22, 43, 24, 0, 0],
                     [9, 35, 133, 137, 10, 0],
                     [6, 40, 212, 209, 4, 0],
                     [2, 10, 24, 47, 3, 0],
                     [1, 20, 20, 50, 30, 80]
                 ])

    classes = ['label1', 'label2', 'label3', 'label4', 'label5', 'label6']
    plot_cm = ConfusionMatrix(cm, class_list=classes)
    plot_cm.plot(to_normalize=True, to_show_number_label=True)
    print(plot_cm.cm)
