# -*- coding: utf-8 -*-
"""
@Author         :  LEITENG
@Version        :  
------------------------------------
@File           :  p65_my_lstm.py
@Description    :  
@CreateTime     :  2020/7/25 13:35
------------------------------------
@ModifyTime     :  模仿 tf.nn.rnn_cell.LSTMCell()
"""
import tensorflow as tf

name_id = 1


class MyLSTMCell:
    def __init__(self, num_units, state_is_tuple=True, name=None):
        '''
        初始化
        :param num_units: 中间状态的维度会根据输入的第一个维度确定，保证每一维都进行存储
        :param state_is_tuple: 状态是否为元组
        :param name:
        '''
        self.num_units = num_units
        self.state_is_tuple = state_is_tuple
        if name is None:
            global name_id
            name = 'my_lstm_cell_%d' % name_id
            name_id += 1
        self.name = name

    def __call__(self, inputs, state):
        '''
        调用函数
        :param inputs: [-1, num_units]
        :param state: tuple of [-1, num_units]'s or [-1, 2*num_units]
        :return:
        '''
        with tf.variable_scope(self.name):
            units = self.num_units
            if self.state_is_tuple:
                c, h = state
            else:
                c = state[:, :units]
                h = state[:, units:]
            inputs = tf.concat((inputs, h), axis=1)  # [-1, 2*num_units]
            inputs = tf.layers.dense(inputs, 4 * units, name='dense1')  # [-1, 4*num_units]
            gates = tf.nn.sigmoid(inputs[:3 * units])
            # 遗忘门
            gate_input = gates[:, 2 * units:]
            # 输入门
            c2 = tf.nn.tanh(inputs[:, 3 * units:]) * gate_input
            # 输出门
            c = c * gates[:, :units] + c2
            h = tf.tanh(c) * gates[:, units: 2 * units]

        state = (c, h) if self.state_is_tuple else tf.concat((c, h), axis=1)
        return h, state

    def zero_state(self, batch_size, dtype):
        '''
        初始化：隐藏状态，上个神经元的输出，输入
        :param batch_size:
        :param dtype:
        :return:
        '''
        if self.state_is_tuple:
            zeros = tf.zeros([batch_size, self.num_units], dtype)
            return zeros, zeros
        else:
            return tf.zeros([batch_size, 2 * self.num_units], dtype)
