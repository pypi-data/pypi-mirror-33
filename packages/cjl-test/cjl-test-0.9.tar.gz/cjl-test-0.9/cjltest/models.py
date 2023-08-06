# -*- coding: utf-8 -*-

import torch.nn as nn
import torch.nn.functional as f


class MnistCNN(nn.Module):
    """ CNN Network architecture. """

    def __init__(self):
        super(MnistCNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 10, kernel_size=5)
        self.conv2 = nn.Conv2d(10, 20, kernel_size=5)
        self.conv2_drop = nn.Dropout2d()
        self.fc1 = nn.Linear(320, 50)
        self.fc2 = nn.Linear(50, 10)

    def forward(self, x):
        x = f.relu(f.max_pool2d(self.conv1(x), 2))
        x = f.relu(f.max_pool2d(self.conv2_drop(self.conv2(x)), 2))
        x = x.view(-1, 320)
        x = f.relu(self.fc1(x))
        x = f.dropout(x, training=self.training)
        x = self.fc2(x)
        return f.log_softmax(x, dim=1)


# Linear Regression Model
class LinearRegression(nn.Module):
    def __init__(self):
        super(LinearRegression, self).__init__()
        self.linear = nn.Linear(1, 1)  # input and output is 1 dimension

    def forward(self, x):
        return self.linear(x)


class LeNetForMNIST(nn.Module):

    def __init__(self):
        super(LeNetForMNIST, self).__init__()
        self.conv1 = nn.Conv2d(1, 6, 5)
        self.conv2 = nn.Conv2d(6, 16, 5)
        self.fc1 = nn.Linear(16 * 4 * 4, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 10)

    def forward(self, x):
        x = f.max_pool2d(f.relu(self.conv1(x)), (2, 2))
        x = f.max_pool2d(f.relu(self.conv2(x)), 2)
        x = x.view(x.size()[0], -1)
        x = f.relu(self.fc1(x))
        x = f.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class AlexNetForCIFAR(nn.Module):

    def __init__(self, num_classes=10):
        super(AlexNetForCIFAR, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=11, stride=4, padding=5),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(64, 192, kernel_size=5, padding=2),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(192, 384, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(384, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(256, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        self.classifier = nn.Linear(256, num_classes)

    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return f.log_softmax(x, dim=1)


class RNNModel(nn.Module):
    """Container module with an encoder, a recurrent module, and a decoder."""

    def __init__(self, rnn_type, ntoken, ninp, nhid, nlayers, dropout=0.5, tie_weights=False):
        super(RNNModel, self).__init__()
        self.drop = nn.Dropout(dropout)
        self.encoder = nn.Embedding(ntoken, ninp)
        if rnn_type in ['LSTM', 'GRU']:
            self.rnn = getattr(nn, rnn_type)(ninp, nhid, nlayers, dropout=dropout)
        else:
            try:
                nonlinearity = {'RNN_TANH': 'tanh', 'RNN_RELU': 'relu'}[rnn_type]
            except KeyError:
                raise ValueError("""An invalid option for `--model` was supplied,
                                 options are ['LSTM', 'GRU', 'RNN_TANH' or 'RNN_RELU']""")
            self.rnn = nn.RNN(ninp, nhid, nlayers, nonlinearity=nonlinearity, dropout=dropout)
        self.decoder = nn.Linear(nhid, ntoken)

        # Optionally tie weights as in:
        # "Using the Output Embedding to Improve Language Models" (Press & Wolf 2016)
        # https://arxiv.org/abs/1608.05859
        # and
        # "Tying Word Vectors and Word Classifiers: A Loss Framework for Language Modeling" (Inan et al. 2016)
        # https://arxiv.org/abs/1611.01462
        if tie_weights:
            if nhid != ninp:
                raise ValueError('When using the tied flag, nhid must be equal to emsize')
            self.decoder.weight = self.encoder.weight

        self.init_weights()

        self.rnn_type = rnn_type
        self.nhid = nhid
        self.nlayers = nlayers

    def init_weights(self):
        initrange = 0.1
        self.encoder.weight.data.uniform_(-initrange, initrange)
        self.decoder.bias.data.zero_()
        self.decoder.weight.data.uniform_(-initrange, initrange)

    # noinspection PyShadowingBuiltins
    def forward(self, input, hidden):
        emb = self.drop(self.encoder(input))
        output, hidden = self.rnn(emb, hidden)
        output = self.drop(output)
        decoded = self.decoder(output.view(output.size(0) * output.size(1), output.size(2)))
        return decoded.view(output.size(0), output.size(1), decoded.size(1)), hidden

    def init_hidden(self, bsz):
        weight = next(self.parameters())
        if self.rnn_type == 'LSTM':
            return (weight.new_zeros(self.nlayers, bsz, self.nhid),
                    weight.new_zeros(self.nlayers, bsz, self.nhid))
        else:
            return weight.new_zeros(self.nlayers, bsz, self.nhid)


class CIFAR10Model(nn.Module):
    def __init__(self, num_classes):
        super(CIFAR10Model, self).__init__()
        self.conv1 = nn.Conv2d(3, 64, kernel_size=5, stride=1)
        nn.init.normal_(self.conv1.weight, 0, 5e-2)
        nn.init.constant_(self.conv1.bias, 0.0)

        self.pool1 = nn.MaxPool2d(kernel_size=3, stride=2)
        self.norm1 = nn.LocalResponseNorm(4, alpha=0.001 / 9.0, beta=0.75, k=1.0)

        self.conv2 = nn.Conv2d(64, 64, kernel_size=5, stride=1)
        nn.init.normal_(self.conv2.weight, 0, 5e-2)
        nn.init.constant_(self.conv2.bias, 0.1)

        self.norm2 = nn.LocalResponseNorm(4, alpha=0.001 / 9.0, beta=0.75, k=1.0)
        self.pool2 = nn.MaxPool2d(kernel_size=3, stride=2)

        self.local3 = nn.Linear(1024, 384)
        nn.init.normal_(self.local3.weight, 0, 0.04)
        nn.init.constant_(self.local3.bias, 0.1)

        self.local4 = nn.Linear(384, 192)
        nn.init.normal_(self.local4.weight, 0, 0.04)
        nn.init.constant_(self.local4.bias, 0.1)

        self.softmax_linear = nn.Linear(192, num_classes)
        nn.init.normal_(self.softmax_linear.weight, 0, 1 / 192.0)
        nn.init.constant_(self.softmax_linear.bias, 0.0)

    # noinspection PyUnresolvedReferences
    def forward(self, x):
        x = f.relu(self.conv1(x), inplace=True)
        x = self.norm1(self.pool1(x))
        x = f.relu(self.conv2(x), inplace=True)
        x = self.pool2(self.norm2(x))

        x = x.reshape(x.size(0), -1)
        # dim = x.size(1)
        # print(dim)
        # weight_local3 = torch.empty(dim, 384)
        # nn.init.normal_(weight_local3, 0, 0.04)
        # bias_local3 = torch.empty(384)
        # nn.init.constant_(bias_local3, 0.1)
        # x = f.relu(torch.matmul(x, weight_local3) + bias_local3, inplace=True)
        x = f.relu(self.local3(x), inplace=True)

        # weight_local4 = torch.empty(384, 192)
        # nn.init.normal_(weight_local4, 0, 0.04)
        # bias_local4 = torch.empty(192)
        # nn.init.constant_(bias_local4, 0.1)
        # x = f.relu(torch.matmul(x, weight_local4) + bias_local4, inplace=True)
        x = f.relu(self.local4(x), inplace=True)

        # weight_linear = torch.empty(192, self.num_classes)
        # nn.init.normal_(weight_linear, 0, 1 / 192.0)
        # bias_linear = torch.empty(self.num_classes)
        # nn.init.constant_(bias_linear, 0.0)
        # x = torch.add(torch.matmul(x, weight_linear), bias_linear)
        x = self.softmax_linear(x)

        return f.log_softmax(x, dim=1)
