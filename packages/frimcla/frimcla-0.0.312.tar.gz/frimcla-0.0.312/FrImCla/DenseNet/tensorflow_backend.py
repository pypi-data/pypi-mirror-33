import tensorflow as tf

from keras.backend.common import image_data_format
from keras.backend.tensorflow_backend import _has_nchw_support

from keras.backend.common import floatx

py_all = all

def _postprocess_conv2d_output(x, data_format):
    """Transpose and cast the output from conv2d if needed.
    # Arguments
        x: A tensor.
        data_format: string, `"channels_last"` or `"channels_first"`.
    # Returns
        A tensor.
    """

    if data_format == 'channels_first':
        x = tf.transpose(x, (0, 3, 1, 2))

    if floatx() == 'float64':
        x = tf.cast(x, 'float64')
    return x

def _preprocess_conv2d_input(x, data_format):
    """Transpose and cast the input before the conv2d.

    # Arguments
        x: input tensor.
        data_format: string, `"channels_last"` or `"channels_first"`.

    # Returns
        A tensor.
    """
    if x.dtype.base_dtype.name == 'float64':
        x = tf.cast(x, 'float32')
    tf_data_format = 'NHWC'
    if data_format == 'channels_first':
        if not _has_nchw_support():
            x = tf.transpose(x, (0, 2, 3, 1))  # NCHW -> NHWC
        else:
            tf_data_format = 'NCHW'
    return x, tf_data_format


def depth_to_space(input, scale, data_format=None):
    ''' Uses phase shift algorithm to convert channels/depth for spatial resolution '''
    if data_format is None:
        data_format = image_data_format()
    data_format = data_format.lower()
    input = _preprocess_conv2d_input(input, data_format)
    out = tf.depth_to_space(input, scale)
    out = _postprocess_conv2d_output(out, data_format)
    return out