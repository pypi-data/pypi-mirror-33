"""Activation functions for neural network."""

import numpy as np
from dl_with_numpy.layer import Layer


class SigmoidActivation(Layer):
    """Sigmoid activation layer of a neural network."""

    def __init__(self, n):
        """
        Create activation layer.

        Args:
            n (integer): Size of input and output data.  This layer accepts
                         inputs with dimension [batch_size, n] and produces
                         an output of the same dimensions.
        """
        super(SigmoidActivation, self).__init__(n_in=n, n_out=n)

    @staticmethod
    def sigmoid(x):
        """
        Calculate the sigmoid function of the input.

        Args:
            x: Input

        Returns:
            Sigmoid(x_in)

        """
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, x):
        """
        Calculate the derivative of the sigmoid of the input.

        Derivative is with respect to the input.

        Args:
            x: Input

        Returns:
            Derivative of sigmoid(x_in)

        """
        sig = self.sigmoid(x)
        return sig * (1 - sig)

    def forward_pass(self):
        """
        Perform forward pass of autodiff algorithm on this layer.

        Calculate the output of this layer from its input and store the result.

        Returns:
            Nothing

        """
        self.output = self.sigmoid(self.input)

    def backward_pass(self):
        """
        Perform backward pass of autodiff algorithm on this layer.

        Calculate the derivative of this layer's input with respect to the
        loss from the derivative of this layer's output with respect to the
        loss.  Store the result.

        Returns:
            Nothing

        """
        self.dloss_din = self.dloss_dout * self.sigmoid_derivative(self.input)
