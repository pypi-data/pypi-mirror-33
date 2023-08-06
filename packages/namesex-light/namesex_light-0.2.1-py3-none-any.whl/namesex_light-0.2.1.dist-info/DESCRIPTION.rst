namesex_light
-------------

Namesex_light is a lighweight package that predicts the gender tendency of Chinese given names. This module comes with a L2 regularized logistic regression trained on 10,730 Chinese given names (in traditional Chinese) with reliable gender lables collected from public data. The predict() function takes a list of names and output predicted gender tendency (1 for male and 0 for female) or probability of being a male name. Namesex_light has a sister project, namesex, that performs similar tasks with higher accuracy.

Additional information about namesex and namesex_light can be found `in another document (in Chinese) <https://github.com/hsinmin/namesex/blob/master/vignettee_namesex_exp1.ipynb>`_.

The prediction performance evaluated by ten-fold cross validation is:

========= =========== =====================
Metric    Performance Performance Std. Dev.
--------- ----------- ---------------------
Accuracy  0.8957      0.007327
F1        0.8920      0.007873
Precision 0.8852      0.012238
Recall    0.8991      0.008936
Logloss   114.35      6.413972
========= =========== =====================


Use pip/pip3 to install namesex_light.::

    pip install namesex_light

To use namesex_light, pass in an array or list of given names to predict(). For each element in the input list, predict() returns 1 or 0 for male or female prediction. Set "predprob = True" to return probability of being a male name. The following is a simple sample code.::


    >>> import namesex_light
    >>> nsl = namesex_light.namesex_light()
    >>> nsl.predict(['民豪', '愛麗', '志明'])
    array([1, 0, 1])
    >>> nsl.predict(['民豪', '愛麗', '志明'], predprob=True)
    array([0.99968932, 0.00530066, 0.9938986 ])

Note that namesex_light was trained using Chinese given names only. However, it may be used to classifier translated names as well::

    >>> nsl.predict(['阿波羅', '阿波羅', '雷', '艾美', '布蘭妮', '阿曼達'])
    array([1, 1, 1, 0, 0, 1])

This module is intended for a quick plug-and-play. The original training dataset is not included.

Testing Dataset
---------------

This package comes with a small testing dataset that was not used for model training. The following sample code illustrate a simple usage.::

    >>> testdata = namesex_light.testdata()
    >>> nsl = namesex_light.namesex_light()
    >>> pred = nsl.predict(testdata.gname)
    >>> print("The first 5 given names are: {}".format(testdata.gname[0:5]))
    The first 5 given names are: ['翊如', '妤庭', '諆璋', '大閎', '和維']
    >>> print("    and their sex:          {}".format(testdata.sex[0:5]))
        and their sex:          [0, 0, 1, 1, 1]
    >>> print("    and their predicted sex:{}".format(pred[0:5]))
        and their predicted sex:[0 0 1 1 1]
    >>> accuracy = np.sum(pred == testdata.sex) / len(pred)
    >>> print(" Prediction accuracy = {}".format(accuracy))
     Prediction accuracy = 0.8627450980392157

Note that the accuracy is slightly lower compared to the accuracy of ten-fold cross valudation. I guess this is normal since this testset is collected from a source that is different from the training dataset.

