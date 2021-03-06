# -*- coding: utf-8 -*-
"""
@Author         :  LEITENG
@Version        :  
------------------------------------
@File           :  p64_stock.py
@Description    :  
@CreateTime     :  2020/7/16 11:09
------------------------------------
@ModifyTime     :  rnn 进行股票预测
"""
import p50_framework as myf
import tensorflow as tf
import numpy as np


class MyConfig(myf.Config):
    def __init__(self):
        super(MyConfig, self).__init__()
        self.num_steps = 10  # 参考前几天的股票
        self.stocks = 8
        self.batch_size = 1
        self.days = 300
        # 存储状态的维度
        self.state_size = 4

    def get_ds_test(self):
        return MyDS(self.stocks, self.days, self.num_steps)

    def get_ds_train(self):
        return MyDS(self.stocks, self.days, self.num_steps)

    def get_sub_tensors(self, gpu_index):
        return MySubTensors(self)

    def get_name(self):
        return 'p64'


class MySubTensors:
    def __init__(self, config: MyConfig):
        self.config = config
        x = tf.placeholder(tf.float32, [None, config.num_steps])  # [-1, 10]
        y = tf.placeholder(tf.float32, [None])  # [-1]
        self.inputs = [x, y]

        cell = Cell(config.state_size)
        # 将 cell 进行初始化
        state = cell.zero_state(tf.shape(x)[0], x.dtype)  # [-1, 4]
        with tf.variable_scope('my_cell') as scope:
            # 循环创建张量
            for i in range(config.num_steps):
                # state: [-1, state_size]
                _, state = cell(x[:, i], state)
                scope.reuse_variables()

        y_predict = tf.layers.dense(state, 1, name='dense1')  # [-1, 1]
        y_predict = tf.reshape(y_predict, [-1])
        loss = tf.reduce_mean(tf.square(y_predict - y))
        self.losses = [loss]


class Cell:
    def __init__(self, num_units):
        self.num_units = num_units

    def __call__(self, xi, statei):
        # xi: [-1]
        # statei: [-1, state_size]
        xi = tf.reshape(xi, [-1, 1])  # 输入
        # [-1, state_size + 1]
        x = tf.concat((xi, statei), axis=1)  # [-1, 5]
        x = tf.layers.dense(x, 400, name='dense', activation=tf.nn.relu)
        state = tf.layers.dense(x, statei.shape[-1].value, name='dense2')  # [-1, 4]
        return None, state

    def zero_state(self, batch_size, dtype):
        '''
        初始化状态
        :param batch_size: -1, 与x的第一个维度相同
        :param dtype:
        :return: [-1, 4]
        '''
        return tf.zeros([batch_size, self.num_units], dtype)


class MyDS:
    def __init__(self, stacks, days, steps):
        '''
        模拟数据
        :param stacks: 股票个数
        :param days: 天数
        :param steps: 循环次数，也就是参考天数
        '''
        # 伪随机数造成损失在下降
        self.data = np.random.normal(size=[stacks, days])
        # 每10天算一个样本，如果1-100天，则共有91个样本，由于使用前十个样本预测下一个，所以取90个样本
        self.num_examples = days - steps
        self.pos = np.random.randint(0, self.num_examples)
        self.steps = steps

    def next_batch(self, batch_size):
        next = self.pos + self.steps
        # [stocks, steps]
        x = self.data[:, self.pos: next]
        # [stocks]
        y = self.data[:, next]
        self.pos += 1
        if self.pos >= self.num_examples:
            self.pos = 0
        return x, y


def main():
    cfg = MyConfig()
    cfg.from_cmd()


if __name__ == '__main__':
    main()