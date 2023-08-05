from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np

from art.classifiers import Classifier


class MXClassifier(Classifier):
    def __init__(self, clip_values, input_ph, logits, nb_classes, ctx, channel_index=1, defences=None):
        """
        Initialize a `Classifier` object.

        :param clip_values: Tuple of the form `(min, max)` representing the minimum and maximum values allowed
               for features.
        :type clip_values: `tuple`
        :param input_ph: The input placeholder.
        :type input_ph: `mxnet.symbol.Variable`
        :param logits: The logits layer of the model.
        :type logits: `mxnet.symbol.Symbol`
        :param nb_classes: The number of classes of the model.
        :type nb_classes: `int`
        :param ctx: The device on which the model runs (CPU or GPU).
        :type ctx: `mxnet.context.Context`
        :param channel_index: Index of the axis in data containing the color channels or features.
        :type channel_index: `int`
        :param defences: Defences to be activated with the classifier.
        :type defences: `str` or `list(str)`
        """
        import mxnet as mx
        super(MXClassifier, self).__init__(clip_values, channel_index, defences)

        self._input_ph = input_ph
        self._logits = logits
        self._nb_classes = nb_classes
        self._input_shape = input_ph.shape
        self._device = ctx

        self._label_ph = mx.symbol.Variable('label')
        self._loss = mx.symbol.softmax_cross_entropy(logits, self._label_ph)

    def fit(self, x, y, batch_size=128, nb_epochs=20):
        """
        Fit the classifier on the training set `(inputs, outputs)`.

        :param x: Training data.
        :type x: `np.ndarray`
        :param y: Labels.
        :type y: `np.ndarray`
        :param batch_size: Size of batches.
        :type batch_size: `int`
        :param nb_epochs: Number of epochs to use for trainings.
        :type nb_epochs: `int`
        :return: `None`
        """
        # Apply defences
        x, y = self._apply_defences_fit(x, y)

        batch_size = 256

        train_data = gluon.data.DataLoader(
            mnist_train, batch_size=batch_size, shuffle=True, num_workers=4)
        for data, label in train_data:
            print(data.shape, label.shape)  # this is a batch of 256
            break
        pass

    def predict(self, x, logits=False):
        """
        Perform prediction for a batch of inputs.

        :param x: Test set.
        :type x: `np.ndarray`
        :param logits: `True` if the prediction should be done at the logits layer.
        :type logits: `bool`
        :return: Array of predictions of shape `(nb_inputs, self.nb_classes)`.
        :rtype: `np.ndarray`
        """
        import mxnet as mx

        # Apply defences
        inputs_ = self._apply_defences_predict(x)

        inputs_ = mx.nd.array(inputs_, ctx=self._device)
        # args_map[self._input_ph] = inputs_
        mod = mx.mod.Module(self._logits)

        preds = np.empty((x.shape[0], self.nb_classes), dtype=float)
        pred_iter = mx.io.NDArrayIter(data=inputs_, batch_size=128)
        if logits is True:
            for preds_i, i, batch in mod.iter_predict(pred_iter):
                pred_label = preds_i[0].asnumpy()
        else:
            for preds_i, i, batch in mod.iter_predict(pred_iter):
                pred_label = preds_i[0].softmax().asnumpy()

        return preds

    def class_gradient(self, x, logits=False):
        """
        Compute per-class derivatives w.r.t. `x`.

        :param x: Sample input with shape as expected by the model.
        :type x: `np.ndarray`
        :param logits: `True` if the prediction should be done at the logits layer.
        :type logits: `bool`
        :return: Array of gradients of input features w.r.t. each class in the form
                 `(batch_size, nb_classes, input_shape)`.
        :rtype: `np.ndarray`
        """
        pass

    def loss_gradient(self, x, y):
        """
        Compute the gradient of the loss function w.r.t. `x`.

        :param x: Sample input with shape as expected by the model.
        :type x: `np.ndarray`
        :param y: Correct labels, one-vs-rest encoding.
        :type y: `np.ndarray`
        :return: Array of gradients of the same shape as `x`.
        :rtype: `np.ndarray`
        """
        pass
