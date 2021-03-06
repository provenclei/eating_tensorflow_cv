# -*- coding: utf-8 -*-
"""
@Author         :  LEITENG
@Version        :  
------------------------------------
@File           :  p51_face_recog.py
@Description    :  
@CreateTime     :  2020/7/3 09:04
------------------------------------
@ModifyTime     :  
"""
import tensorflow as tf
import numpy as np

from p45_celeba import CelebA
from p48_BufferDS import BufferDS
import p50_framework as myf

# img_size: 218, 178


class MyConfig(myf.Config):
    def __init__(self, persons):
        super(MyConfig, self).__init__()
        self.lr = 0.001
        self.epoches = 2000
        self.buffer_size = 10
        self.batch_size = 50

        self.img_size = 32 * 4  # target size of images
        self.convs = 5
        self.base_filters = 32
        self.persons = persons
        self.ds = None

    def get_name(self):
        return 'p51'

    def get_sub_tensors(self, gpu_idx):
        return MySubTensors(self)

    def get_app(self):
        return MyApp(self)

    def get_ds_train(self):
        return self.ds

    def get_ds_test(self):
        return self.ds


class MySubTensors:
    def __init__(self, config: MyConfig):
        self.config = config
        x = tf.placeholder(tf.float32, [None, None, None, 3], name='x')
        y = tf.placeholder(tf.int32, [None], name='y')
        self.inputs = [x, y]
        with tf.variable_scope('encode'):
            self.vector = self.encode(x)  # [-1, persons]

        logits = self.get_logits(self.vector)
        y2 = tf.one_hot(y, config.persons)
        loss = tf.nn.softmax_cross_entropy_with_logits_v2(labels=y2, logits=logits)
        loss = tf.reduce_mean(loss)
        self.losses = [loss]

        y_predict = tf.argmax(logits, axis=1, output_type=tf.int32)
        precise = tf.cast(tf.equal(y, y_predict), tf.float32)
        self.precise = tf.reduce_mean(precise)

    def get_logits(self, vector):
        logits = tf.layers.dense(vector, cfg.persons)
        return logits

    def encode(self, x):
        cfg = self.config
        x = tf.image.resize_images(x, (cfg.img_size, cfg.img_size))
        #  x: [-1, img_size, img_size, 3]
        x = tf.layers.conv2d(x, cfg.base_filters, 3, 1, 'same', activation=tf.nn.relu, name='conv1')
        filters = cfg.base_filters
        size = cfg.img_size
        for i in range(cfg.convs):
            filters *= 2
            size //= 2
            x = tf.layers.conv2d(x, filters, 3, 2, 'same', activation=tf.nn.relu, name='conv2_%d'%i)
        return tf.layers.flatten(x)


def predict(app):
    pass


class MyApp(myf.App):

    def train(self, ds_train, ds_validation):
        self.ds_valid = ds_validation
        super(MyApp, self).train(ds_train, ds_validation)

    def after_epoch(self, epoch):
        '''
        每轮之后求一次精度
        :param epoch:
        :return:
        '''
        super(MyApp, self).after_epoch()
        feed_dict = self.get_feed_dict(self.ds_valid)
        # 每个 gpu 上的精度
        precise = [ts.precise for ts in self.ts.sub_ts]
        ps = self.session.run(precise, feed_dict)
        print('precise:', np.mean(ps))

    def test(self, ds_test):
        print('in MyApp.test()', flush=True)


def main():
    pass


if __name__ == '__main__':
    main()