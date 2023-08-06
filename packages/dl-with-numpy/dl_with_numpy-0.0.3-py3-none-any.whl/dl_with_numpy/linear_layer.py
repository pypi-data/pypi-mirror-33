"""Linear layer for neural network."""

import numpy as np
from dl_with_numpy.layer import Layer


class LinearLayer(Layer):
    """A linear layer for a neural network."""

    def __init__(self, n_in, n_out, seed=0):
        """
        Initialise object.

        Args:
            n_in (integer): Size of input to this layer.  This layer accepts
                            inputs with dimension [batch_size, n_in].

            n_out (integer): Size of output of this layer.  This layer creates
                             outputs with dimension [batch_size, n_out]

            seed (integer): Random seed for initialising the linear layer's
                            parameters.

        """
        super(LinearLayer, self).__init__(n_in=n_in, n_out=n_out)

        np.random.seed(seed)

        # Initialise weights with fan-in approach.
        self.weights = np.random.normal(0.0, n_in ** -0.5, (n_in, n_out))

        # derivative of loss w.r.t. parameter weights
        self.dloss_dweights = None

    def forward_pass(self):
        """
        Perform forward pass of autodiff algorithm on this layer.

        Calculate the output of this layer from its input and store the result.

        Returns:
            Nothing

        """
        self.output = np.dot(self.input, self.weights)

    def backward_pass(self):
        """
        Perform backward pass of autodiff algorithm on this layer.

        Calculate the derivative of this layer's input with respect to the
        loss from the derivative of this layer's output with respect to the
        loss.  Store the result.

        Returns:
            Nothing

        """
        self.dloss_din = np.dot(self.dloss_dout, self.weights.T)

    def calc_param_grads(self):
        """
        Calculate the gradients of the parameters of this layer.

        This is the gradient of the network's loss with respect to this layer's
        parameters, if there are any.  The result is stored.

        Returns:
            Nothing

        """
        self.dloss_dweights = np.dot(self.input.T, self.dloss_dout)

    def update_params(self, learning_rate):
        """
        Update this layer's parameters, if there are any.

        Args:
            learning_rate (float): Learning rate

        Returns:
            Nothing

        """
        self.weights -= self.dloss_dweights * learning_rate
