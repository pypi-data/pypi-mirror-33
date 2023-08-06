"""Abstract class for layers of neural network."""

import abc


class Layer(metaclass=abc.ABCMeta):
    """
    Base class for a single layer of neural network.

    'Layer' here is broader than the standard meaning and includes activation
    and loss layers.
    """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, n_in, n_out):
        """
        Initialise attributes of base class.

        Args:
            n_in (integer): Size of input to this layer.  This layer accepts
                            inputs with dimension [batch_size, n_in].
            n_out (integer): Size of output of this layer.  This layer creates
                             outputs with dimension [batch_size, n_out]

        """
        self.input = None
        self.output = None

        self.input_size = n_in
        self.output_size = n_out

        self.dloss_din = None  # derivative of loss w.r.t. input
        self.dloss_dout = None  # derivative of loss w.r.t. output

        self.next = None  # next node in the computation graph
        self.prev = None  # previous node in the computation graph

    @abc.abstractmethod
    def forward_pass(self):
        """
        Perform forward pass of autodiff algorithm on this layer.

        Calculate the output of this layer from its input and store the result.

        Returns:
            Nothing

        """

    @abc.abstractmethod
    def backward_pass(self):
        """
        Perform backward pass of autodiff algorithm on this layer.

        Calculate the derivative of this layer's input with respect to the
        loss from the derivative of this layer's output with respect to the
        loss.  Store the result.

        Returns:
            Nothing

        """

    def calc_param_grads(self):
        """
        Calculate the gradients of the parameters of this layer.

        This is the gradient of the network's loss with respect to this layer's
        parameters, if there are any.  The result is stored.

        Returns:
            Nothing

        """

    def update_params(self, learning_rate):
        """
        Update this layer's parameters, if there are any.

        Args:
            learning_rate (float): Learning rate

        Returns:
            Nothing

        """
