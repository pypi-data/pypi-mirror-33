# useful_graphs

This library supports to draw graph that [matplotlib](https://matplotlib.org/) does not support.
Currently we have confusion matrix.

## Install

```shell
pip install useful_graphs
```

## Examples

### Confusion Matrix

We recommend you to use scikit-learn's [confusion_matrix](http://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html) to calculate the confusion matrix.
This library helps you only to draw the graph of it.

#### Plot

```python
import numpy as np
import useful_graphs

data = np.array([
                    [10, 3, 4],
                    [0, 9, 2],
                    [3, 2, 10],
                ])
classes = ['label-1', 'label-2', 'label-3']
cm = useful_graphs.ConfusionMatrix(data, class_list=classes)
cm.plot(to_normalize=True, to_show_number_label=True)
```

![混同行列サンプル](https://raw.github.com/wiki/yuuuuwwww/useful_graphs/images/sample_1.png "混同行列サンプル")

#### Save figure

To save a figure of confusion matrix, specify path with `savepath` argument.
At this time, figure will not be shown.

```python
import numpy as np
import useful_graphs

data = np.array([
                    [10, 3, 4],
                    [0, 9, 2],
                    [3, 2, 10],
                ])
classes = ['label-1', 'label-2', 'label-3']
cm = useful_graphs.ConfusionMatrix(data, class_list=classes)
cm.plot(to_normalize=True, to_show_number_label=True, save_path="{path_to_figure.pdf}")
```

#### Options for ConfusionMatrix.plot()

- to_normalize (bool, optional): If true, normalize confusion matrix for each row. (default False)
- title (str, optional): If specified, set a title to a figure. If none, title is not set. (default None)
- to_show_colorbar (bool, optional): If true, show colorbar to a figure. (default True)
- colorbar_label (str, optional): If specified, show label next to colorbar. (default None)
- to_show_label (bool, optional): If true, show label in a figure. (default True)
- to_show_number_label (bool, optional): If true, show number of data under the label. (default False)
- cmap (matplotlib colormap object, optional): Set colormap. See [matplotlib](https://matplotlib.org/users/colormaps.html) for available colormaps. (default matplotlib.pyplot.cm.Reds)
- save_path (str, optional): If specified, save graph to specified path and not show the graph. (default None)
- xlabel (str, optional): If specified, change xlabel. (default 'Predicted label')
- ylabel (str, optional): If specified, change ylabel.  (default 'True label')
- text_font_size (int, optional): If specified change font size.  (default 10)
- figsize (tuple of shape=(w, h), optional): If specified, change size of a figure to w, h in inches. It changes `figsize` parameter of [matplotlib.figure.Figure](https://matplotlib.org/api/_as_gen/matplotlib.figure.Figure.html#matplotlib-figure-figure). (default None)
