import tensorflow as tf
from tensorflow.contrib import slim
import sonnet as snt

__all__ = ['LayerNormalization', 'SpatialDropout', 'CausalConv2D']


class LayerNormalization(snt.AbstractModule):
    def __init__(self,
                 eps=1e-5,
                 initializers=None,
                 partitioners=None,
                 regularizers=None,
                 name="layer_normalization"):
        super(LayerNormalization, self).__init__(name=name)
        with self._enter_variable_scope():
            self._layer_norm = snt.LayerNorm(eps=eps,
                                             initializers=initializers,
                                             partitioners=partitioners,
                                             regularizers=regularizers,
                                             name=f'{name}_core')

    def _build(self, inputs):
        """Connects the LayerNorm module into the graph.

        Args:
            inputs: a Tensor of shape `[batch_size, ..., layer_dim]`.

        Returns:
            normalized: layer normalized outputs with same shape as inputs.
        """

        inputs_shape = inputs.get_shape().as_list()
        hidden_size = inputs_shape[-1]
        reshaped_inputs = tf.reshape(inputs, shape=[-1, hidden_size])
        reshaped_normalized = self._layer_norm(reshaped_inputs)
        normalized = tf.reshape(reshaped_normalized, shape=[-1] + inputs_shape[1:])
        return normalized


class SpatialDropout(snt.AbstractModule):
    def __init__(self,
                 keep_prob,
                 name='spatial_dropout'):
        super(SpatialDropout, self).__init__(name=name)
        self._keep_prob = keep_prob

    def _build(self, x, is_training):
        x_shape = tf.shape(x)
        noise_shape = [x_shape[0]] + [1] * (len(x.get_shape()) - 2) + [x_shape[-1]]
        result = slim.dropout(x, self._keep_prob, noise_shape=noise_shape, is_training=is_training)
        return result


class CausalConv2D(snt.AbstractModule):
    def __init__(self, output_channels, kernel_shape, stride=1, rate=1,
                 use_bias=True, initializers=None,
                 partitioners=None, regularizers=None, mask=None,
                 data_format="NHWC", custom_getter=None,
                 name="causal_conv_2d"):
        super(CausalConv2D, self).__init__(name=name)
        with self._enter_variable_scope():
            self._conv = snt.Conv2D(output_channels, kernel_shape, stride, rate,
                                    'VALID', use_bias, initializers, partitioners, regularizers,
                                    mask, data_format, custom_getter)

    def _build(self, inputs):
        kernel_shape = self._conv.kernel_shape
        rate = self._conv.rate
        pad_amount_0 = int((kernel_shape[0] - 1) * rate[0])
        pad_amount_1 = int((kernel_shape[1] - 1) * rate[1])
        padded_inputs = tf.pad(inputs, paddings=[[0, 0], [pad_amount_0, 0], [pad_amount_1, 0], [0, 0]])
        return self._conv(padded_inputs)
