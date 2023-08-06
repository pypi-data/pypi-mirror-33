"""Loss layers for neural network."""

import numpy as np
from dl_with_numpy.layer import Layer


class MeanSquareLoss(Layer):
    """Mean square loss layer for neural network."""

    def __init__(self):
        """Create mean square loss layer."""
        # n_in and n_out not used
        super(MeanSquareLoss, self).__init__(n_in=0, n_out=0)

        # output of loss layer is the loss, so its derivative w.r.t. loss is 1
        self.dloss_dout = 1
        self.mean_sq_loss = None

        self.y = None  # true output

    def forward_pass(self):
        """
        Perform forward pass of autodiff algorithm on this layer.

        Calculate the output of this layer from its input and store the result.

        Returns:
            Nothing

        """
        # Input to loss layer is the output of the previous layer
        self.mean_sq_loss = 0.5 * np.mean(np.square(self.input - self.y))

    def backward_pass(self):
        """
        Perform backward pass of autodiff algorithm on this layer.

        Calculate the derivative of this layer's input with respect to the
        loss from the derivative of this layer's output with respect to the
        loss.  Store the result.

        Returns:
            Nothing

        """
        self.dloss_din = (self.input - self.y) / self.y.size
