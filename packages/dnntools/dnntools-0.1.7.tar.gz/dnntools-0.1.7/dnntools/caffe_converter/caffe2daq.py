#!/usr/bin/env python3

import argparse
from google.protobuf import text_format
from caffe.proto import caffe_pb2
import caffe
import numpy as np
from dnntools import model_writer as mw
from dnntools.model_writer import ModelWriter
import typing


CAFFE_POOL_MAX = 0
CAFFE_POOL_AVE = 1
CAFFE_POOL_STOCHASTIC = 2

CAFFE_ELTWISE_PROD = 0
CAFFE_ELTWISE_SUM = 1
CAFFE_ELTWISE_MAX = 2

ACTIVATION_NONE = 0
ACTIVATION_RELU = 1

SUPPORTED_LAYERS = ['Convolution', 'InnerProduct', 'Pooling', 'Input', 'ReLU', 'Softmax', 'Dropout', 'Eltwise',
                    'BatchNorm', 'Scale', 'Concat', 'Power', 'LRN']
SUPPORTED_ACTIVATIONS = ['ReLU']


def find_inplace_activation(params: caffe_pb2.NetParameter, layer_name: str, skipped_layers: typing.List[str]) -> int:
    for i, layer in enumerate(params.layer):
        if layer.name != layer_name:
            continue
        top_blob_name = layer.top[0]
        for j in range(i + 1, len(params.layer)):
            layerJ = params.layer[j]
            if layerJ.top[0] == top_blob_name:
                if layerJ.type == 'ReLU':
                    skipped_layers.append(layerJ.name)
                    return ACTIVATION_RELU
                break
    return ACTIVATION_NONE


def convert(prototxt: str, caffemodel: str, dest: str = 'nnmodel.daq') -> None:
    assert isinstance(prototxt, str) and isinstance(caffemodel, str), 'prototxt and caffemodel shoule be filename'

    skipped_layers = []

    params = caffe_pb2.NetParameter()

    with open(prototxt) as f:
        text_format.Merge(f.read(), params)

    net = caffe.Net(prototxt, caffemodel, caffe.TEST)

    out_filename = dest
    with open(out_filename, 'wb') as f:
        model_writer = ModelWriter(f)

        for i, layer in enumerate(params.layer):
            if layer.type not in SUPPORTED_LAYERS:
                raise ValueError("Not supported layer " + layer.type)

            if layer.name in skipped_layers:
                continue

            top_name = layer.top[0]

            if i == 0:
                if layer.type != "Input":
                    raise ValueError("First layer should be input")

                param = layer.input_param
                model_writer.add_input(top_name, param.shape[0].dim)

            elif layer.type == 'Convolution':
                bottom_name = layer.bottom[0]
                param = layer.convolution_param
                pad = param.pad[0] if param.pad != [] else 0
                pad_left = pad_right = pad_top = pad_bottom = pad
                if param.pad_h != 0:
                    pad_top = pad_bottom = param.pad_h
                if param.pad_w != 0:
                    pad_left = pad_right = param.pad_w
                stride = param.stride[0] if param.stride != [] else 1
                stride_x = stride_y = stride
                if param.stride_h != 0:
                    stride_y = param.stride_h
                if param.stride_w != 0:
                    stride_x = param.stride_w
                kernel_size = param.kernel_size[0]
                filter_height = filter_width = kernel_size
                if param.kernel_h != 0:
                    filter_height = param.kernel_h
                if param.kernel_w != 0:
                    filter_width = param.kernel_w
                axis = param.axis
                if axis != 1:
                    raise ValueError("Only axis == 1 is supported.")
                num_output = param.num_output

                weights = net.params[layer.name][0].data
                swapped_weights = np.moveaxis(weights, 1, 3)

                bias = net.params[layer.name][1].data if param.bias_term else None  # np.zeros(swapped_weights.shape[0])
                activation = find_inplace_activation(params, top_name, skipped_layers)

                input_dim = list(net.blobs[bottom_name].data.shape)
                input_channel = input_dim[1]
                group = param.group
                if group == input_channel:
                    model_writer.add_dep_conv(bottom_name, top_name, pad_left, pad_right, pad_top, pad_bottom, stride_x,
                                 stride_y, filter_height, filter_width, num_output, activation, swapped_weights, group, bias)
                elif group == 1:
                    model_writer.add_conv(bottom_name, top_name, pad_left, pad_right, pad_top, pad_bottom,
                                          stride_x, stride_y, filter_height, filter_width,
                                          num_output, activation, swapped_weights, bias)
                else:
                    num_output //= group
                    input_channel //= group
                    for g in range(group):
                        bottom_group_name = "{}_{}".format(bottom_name, g)
                        top_group_name = "{}_{}".format(top_name, g)
                        model_writer.add_strided_slice(bottom_name, bottom_group_name,
                                                       [None, None, None, (input_channel*g, input_channel*(g+1), 1)],
                                                       [True, True, True, False],
                                                       [True, True, True, False]
                                                       )
                        group_weight = swapped_weights[num_output*g:num_output*(g+1)]
                        group_bias = bias[num_output*g:num_output*(g+1)] if bias is not None else None
                        model_writer.add_conv(bottom_group_name, top_group_name,
                                              pad_left, pad_right, pad_top, pad_bottom,
                                              stride_x, stride_y, filter_height, filter_width,
                                              num_output, activation, group_weight, group_bias)
                    model_writer.add_concat(["{}_{}".format(top_name, g) for g in range(group)], top_name)

            elif layer.type == 'Pooling':
                param = layer.pooling_param
                bottom_name = layer.bottom[0]

                pad = param.pad
                pad_left = pad_right = pad_top = pad_bottom = pad
                if param.pad_h != 0:
                    pad_top = pad_bottom = param.pad_h
                if param.pad_w != 0:
                    pad_left = pad_right = param.pad_w
                stride = param.stride
                stride_x = stride_y = stride
                if param.stride_h != 0:
                    stride_y = param.stride_h
                if param.stride_w != 0:
                    stride_x = param.stride_w
                kernel_size = param.kernel_size
                filter_height = filter_width = kernel_size
                if param.kernel_h != 0:
                    filter_height = param.kernel_h
                if param.kernel_w != 0:
                    filter_width = param.kernel_w
                if param.global_pooling:
                    filter_height, filter_width = -1, -1
                activation = find_inplace_activation(params, top_name, skipped_layers)

                if param.pool == CAFFE_POOL_MAX:
                    model_writer.add_max_pool(bottom_name, top_name, pad_left, pad_right, pad_top, pad_bottom,
                                              stride_x, stride_y, filter_height, filter_width, activation)
                elif param.pool == CAFFE_POOL_AVE:
                    model_writer.add_ave_pool(bottom_name, top_name, pad_left, pad_right, pad_top, pad_bottom,
                                              stride_x, stride_y, filter_height, filter_width, activation)
                else:
                    raise ValueError("Not supported pool type")

            elif layer.type == 'InnerProduct':
                bottom_name = layer.bottom[0]
                param = layer.inner_product_param
                input_dim = list(net.blobs[bottom_name].data.shape)
                weights = net.params[layer.name][0].data
                num_output = param.num_output
                if param.axis != 1:
                    raise ValueError("Only inner_product.axis == 1 is supported.")
                if param.transpose:
                    raise ValueError("Only inner_product.transpose == True is supported")
                if len(input_dim) == 4:
                    input_dim[0] = param.num_output
                    weights = weights.reshape(input_dim)
                    weights = np.moveaxis(weights, 1, 3)
                bias = net.params[layer.name][1].data if param.bias_term else None  # np.zeros(num_output)
                activation = find_inplace_activation(params, top_name, skipped_layers)

                model_writer.add_FC(bottom_name, top_name, num_output, activation, weights, bias)

            elif layer.type == 'ReLU':
                bottom_name = layer.bottom[0]
                param = layer.relu_param
                model_writer.add_ReLU(bottom_name, top_name, param.negative_slope)

            elif layer.type == 'Softmax':
                bottom_name = layer.bottom[0]
                param = layer.softmax_param
                if param.axis != 1:
                    raise ValueError("Only softmax.axis == 1 is supported.")
                model_writer.add_softmax(bottom_name, top_name, 1.)

            elif layer.type == 'Dropout':
                pass

            elif layer.type == 'LRN':
                bottom_name = layer.bottom[0]
                param = layer.lrn_param
                local_size = param.local_size
                alpha = param.alpha
                beta = param.beta
                model_writer.add_LRN(bottom_name, top_name, local_size, alpha, beta)

            elif layer.type == 'Eltwise':
                bottom0 = layer.bottom[0]
                bottom1 = layer.bottom[1]
                param = layer.eltwise_param
                if param.operation == CAFFE_ELTWISE_SUM:
                    if np.count_nonzero(np.array(param.coeff) != 1) > 0:
                        raise ValueError("Only all coefficients in sum == 1 is supported.")
                    model_writer.add_add(bottom0, mw.TENSOR_OP, bottom1, top_name)
                elif param.operation == CAFFE_ELTWISE_PROD:
                    model_writer.add_mul(bottom0, mw.TENSOR_OP, bottom1, top_name)
                else:
                    raise ValueError("Unsupported EltwiseOp " + str(param.operation))

            elif layer.type == 'BatchNorm':
                bottom_name = layer.bottom[0]
                param = layer.batch_norm_param
                if not param.use_global_stat:
                    raise ValueError("Only batch_norm.use_global_stat is true is supported. "
                                     "(Did you load model in train phase?)")
                scale_factor = net.params[layer.name][2].data[0]
                mean = net.params[layer.name][0].data / scale_factor
                var = net.params[layer.name][1].data / scale_factor + param.eps

                model_writer.add_add(bottom_name, mw.ARRAY_OP, -mean, top_name)
                # Append top into blobs so that the mul will use a new index as input
                # It will be the index of output blob of add
                model_writer.add_mul(top_name, mw.ARRAY_OP, 1 / np.sqrt(var), top_name)

            elif layer.type == 'Scale':
                if len(layer.bottom) != 1:
                    raise ValueError("Only a learnable Scale layer is supported.")
                bottom_name = layer.bottom[0]
                param = layer.scale_param
                if param.num_axes != 1:
                    raise ValueError("Only scale.num_axes == 2 is supported.")
                multiplier = net.params[layer.name][0].data
                model_writer.add_mul(bottom_name, mw.ARRAY_OP, multiplier, top_name)
                if param.bias_term:
                    bias = net.params[layer.name][1].data
                    model_writer.add_add(top_name, mw.ARRAY_OP, bias, top_name)

            elif layer.type == 'Concat':
                param = layer.concat_param
                model_writer.add_concat(layer.bottom, top_name, param.axis)

            elif layer.type == 'Power':
                bottom_name = layer.bottom[0]
                param = layer.power_param
                power, scale, shift = param.power, param.scale, param.shift

                internal_bottom_name = bottom_name
                if scale != 1:
                    model_writer.add_mul(internal_bottom_name, mw.SCALAR_OP, scale, top_name)
                    internal_bottom_name = top_name
                if shift != 0:
                    model_writer.add_add(internal_bottom_name, mw.SCALAR_OP, shift, top_name)
                    internal_bottom_name = top_name
                if power != 1:
                    raise ValueError('Only power == 1 is supported')

        model_writer.save()


def main():
    parser = argparse.ArgumentParser(description='Convert caffemodel to daq model')
    parser.add_argument('prototxt', type=str, help='prototxt file of source caffe model')
    parser.add_argument('caffemodel', type=str, help='caffemodel file of source caffe model')
    parser.add_argument('dest', type=str, nargs='?', default='nnmodel.daq',
                        help='filename of daq model (default "nnmodel.daq")')

    args = parser.parse_args()
    convert(args.prototxt, args.caffemodel, args.dest)


if __name__ == '__main__':
    main()
