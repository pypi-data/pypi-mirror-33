# -*- coding: utf-8 -*-
"""
train_models 主要完成了：
1.SVM支持向量机原始语料的转化和分类器的训练和保存
2.W2V词嵌入原始语料的转化和词向量的训练和保存
3.RNN语言模型原始语料的转化和RNNLM和词典的训练和保存
"""
__title__ = 'QGDT'
__author__ = 'Ex_treme'
__license__ = 'MIT'
__copyright__ = 'Copyright 2018, Ex_treme'

import codecs
import pickle
import re

import numpy as np
import pandas as pd
from TEDT.segmentation import WordSegmentation
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
from jieba import cut
from sklearn import svm
from sklearn.externals import joblib
from sklearn.model_selection import train_test_split
from torch.nn.utils import clip_grad_norm

from QGDT.tools import *


class TrainModel(object):
    """训练模型"""

    def __init__(self, origin_path, train_path, model_path, config=None, *args, **kwargs):
        self._config = config or Configuration()
        self._config = extend_config(self._config, kwargs)
        if self._config.LOG_ENABLE:
            logging.basicConfig(format='%(levelname)s:%(message)s', level=self._config.LOG_LEVEL)
        self.origin_path = origin_path
        self.train_path = train_path
        self.model_path = model_path

    # 分词处理
    def cut(self, line):
        w = WordSegmentation()
        line = w.segment(line)
        return " ".join(line) + '\n'

    def origin_to_train(self):
        # 读取源数据
        f = codecs.open(self.origin_path, 'r', encoding='utf-8')
        # 目标训练集
        target = codecs.open(self.train_path, 'w', encoding='utf-8')
        # 逐行读取，逐行切分
        line_num = 1
        line = f.readline()
        while line:
            log('info', '--------processing {} line---------------'.format(line_num))
            line_seg = self.cut(line)
            target.write(line_seg)
            line = f.readline()
            line_num += 1
        # 扫尾处理
        f.close()
        target.close()
        log('info', '源数据转换训练集成功！')


class TrainSVM(TrainModel):
    def __init__(self, origin_path=get_current_path('data/svm.csv'), train_path=get_current_path('data/svm_train.csv'),
                 model_path=get_current_path('models/svm')):
        super(TrainSVM, self).__init__(origin_path, train_path, model_path)

    def jaccard(self, x1, x2):
        intersection = [i for i in x1 if i in x2]
        union = [i for i in x1 if i not in x2]
        union[0:0] = x2
        return float(len(intersection)) / len(union)

    def jac_list(self, ser1, ser2):
        if ser1.__len__() == ser2.__len__():
            jac_list = []
            length = ser1.__len__()
            for x in range(length):
                x1 = [i for i in cut(str(ser1[x]))]
                x2 = [i for i in cut(str(ser2[x]))]
                jac_list.append(self.jaccard(x1, x2))
            return jac_list
        else:
            return log('info', '数据集长度不一致，请调整后再转换！')

    def origin_to_train(self):
        # 读取数据源
        origin = pd.read_csv(self.origin_path, encoding='utf-8')
        # 数据预处理(删除任何包含空值的行)
        origin = origin.dropna()
        # 生成新的索引号
        origin.index = range(len(origin))
        # 生成特征字段
        origin['x1_len'] = pd.Series([str(i).__len__() for i in origin.x1])
        origin['x2_len'] = pd.Series([str(i).__len__() for i in origin.x2])
        origin['jac'] = pd.Series(self.jac_list(origin.x1, origin.x2))
        # 生成训练数据集
        origin.to_csv(self.train_path, columns=['x1_len', 'x2_len', 'jac', 'label'], encoding='utf-8',
                      date_format=float)
        return log('info', '源数据转换成训练集成功！')

    def train(self):
        # 读入训练集
        train_data = np.loadtxt(self.train_path, dtype=float, delimiter=',', skiprows=1)
        # 按照label，划分训练集和标签
        x, y = np.split(train_data, (4,), axis=1)
        # 选取训练特征
        x = x[:, 1:]
        # 自动划分训练集和测试集
        x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=1, train_size=0.6)
        # 为分类器设定训练参数(线性划分核函数：linear，高斯核函数：rbf)
        clf = svm.SVC(C=1, kernel='linear', gamma='auto', decision_function_shape='ovr')
        # 开始训练
        clf.fit(x_train, y_train.ravel())
        # 保存训练好的模型
        joblib.dump(clf, self.model_path)

        return log('info', '训练SVM分类器成功！准确率为：{}%'.format(round(clf.score(x_test, y_test) * 100, 2)))


class TrainW2V(TrainModel):
    def __init__(self, origin_path=get_current_path('data/w2v.csv'), train_path=get_current_path('data/w2v_train.csv'),
                 model_path=get_current_path('models/w2v')):
        super(TrainW2V, self).__init__(origin_path, train_path, model_path)

    def question_like(self, line):
        if re.findall(r'[0-9a-zA-Z，。/；‘·「、《》：“{}|！@#￥%…&×（）—+,.;]', line):
            return False
        elif re.search(r'[？].+', line):
            return False
        elif re.match(r'如何.+?？', line):
            return True
        elif re.match(r'.+?是什么？', line):
            return True
        elif re.match(r'.+?有哪些？', line):
            return True
        elif re.match(r'.+?如何.+?？', line):
            return True
        else:
            return False

    def origin(self):
        with open('question.txt', encoding='utf-8', mode='r') as f:
            f.seek(0)
            line = f.readline()
            count = 0
            with open('question2.txt', encoding='utf-8', mode='a') as f2:
                while line:
                    if self.question_like(line):
                        f2.write(line)
                        log('info', '第{}行写入：{}'.format(count, line))
                    else:
                        log('info', '第{}行舍弃：{}'.format(count, line))
                    line = f.readline()
                    count += 1
                f2.close()
            f.close()

    def train(self):
        model = Word2Vec(LineSentence(self.train_path), size=12, window=2, min_count=0, workers=4)
        model.save(self.model_path)


class TrainRNN(TrainModel):
    def __init__(self, origin_path=get_current_path('data/rnn.csv'), train_path=get_current_path('data/rnn_train.csv'),
                 model_path=get_current_path('models/rnn')):
        super(TrainRNN, self).__init__(origin_path, train_path, model_path)
        # Load "Penn Treebank" dataset
        self.corpus = Corpus()
        self.ids = self.corpus.get_data(self.origin_path, batch_size)
        self.vocab_size = len(self.corpus.dictionary)
        self.num_batches = self.ids.size(1) // seq_length
        self.dict_path = get_current_path('models/rnn_dict')

    def cut(self, line):
        line = [i.lower() for i in cut(line)]
        return " ".join(line)

        # Truncated backpropagation

    def detach(self, states):
        return [state.detach() for state in states]

    def train(self):
        model = RNNLM(self.vocab_size, embed_size, hidden_size, num_layers).to(device)

        # Loss and optimizer
        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

        # Train the model
        for epoch in range(num_epochs):
            # Set initial hidden and cell states
            states = (torch.zeros(num_layers, batch_size, hidden_size).to(device),
                      torch.zeros(num_layers, batch_size, hidden_size).to(device))

            for i in range(0, self.ids.size(1) - seq_length, seq_length):
                # Get mini-batch inputs and targets
                inputs = self.ids[:, i:i + seq_length].to(device)
                targets = self.ids[:, (i + 1):(i + 1) + seq_length].to(device)

                # Forward pass
                states = self.detach(states)
                outputs, states = model(inputs, states)
                loss = criterion(outputs, targets.reshape(-1))

                # Backward and optimize
                model.zero_grad()
                loss.backward()
                clip_grad_norm(model.parameters(), 0.5)
                optimizer.step()

                step = (i + 1) // seq_length
                if step % 100 == 0:
                    log('info', 'Epoch [{}/{}], Step[{}/{}], Loss: {:.4f}, Perplexity: {:5.2f}'
                        .format(epoch + 1, num_epochs, step, self.num_batches, loss.item(), np.exp(loss.item())))

        # Save the model checkpoints
        torch.save(model, self.model_path)
        rnn_dict = dict(zip(self.corpus.dictionary.idx2word.values(), self.corpus.dictionary.idx2word.keys()))
        with open(self.dict_path, mode='wb') as f:
            pickle.dump(rnn_dict, f)


if __name__ == "__main__":
    # t = TrainSVM()
    t = TrainW2V()
    # t = TrainRNN()
    # t.origin_to_train()
    t.train()
