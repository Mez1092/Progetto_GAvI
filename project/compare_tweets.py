import pandas as pd
import argparse
import matplotlib
import numpy as np
matplotlib.use('qt5agg')
from matplotlib import pyplot as plt
plt.style.use('seaborn')
parser = argparse.ArgumentParser()
parser.add_argument('input_vader', type=argparse.FileType("r"))
parser.add_argument('input_sentiwn', type=argparse.FileType("r"))
args = parser.parse_args()

if __name__ == '__main__':
    scores_vader = pd.read_csv(args.input_vader.name)
    scores_sentiwn = pd.read_csv(args.input_sentiwn.name)

    total = scores_vader.shape[0]

    labels = ('Vader', 'SentiWordNet')
    ind = np.arange(len(labels))
    width = 0.2

    pos_vader = scores_vader[scores_vader.polarity == 'Positive'].shape[0]
    neg_vader = scores_vader[scores_vader.polarity == 'Negative'].shape[0]
    neu_vader = scores_vader[scores_vader.polarity == 'Neutral'].shape[0]

    pos_sentiwn = scores_sentiwn[scores_sentiwn.polarity == 'Positive'].shape[0]
    neg_sentiwn = scores_sentiwn[scores_sentiwn.polarity == 'Negative'].shape[0]
    neu_sentiwn = scores_sentiwn[scores_sentiwn.polarity == 'Neutral'].shape[0]

    bar_1 = plt.bar(ind, [pos_vader, pos_sentiwn], width, color='r')
    bar_2 = plt.bar(ind+width, [neg_vader, neg_sentiwn], width, color='g')
    bar_3 = plt.bar(ind+(width*2), [neu_vader, neu_sentiwn], width, color='y')

    ax = plt.gca()
    ax.set_ylabel("# of tweets")
    ax.set_xticks(ind + (width*2) / 2)
    ax.set_xticklabels(labels)

    for bars in [bar_1, bar_2, bar_3]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x()+ bar.get_width()/2., 0.99*height,
                    '%d' % int(height*100 / total) + "%", ha='center', va='bottom')

    plt.legend((bar_1[0], bar_2[0], bar_3[0]), ('Positive', 'Negative', 'Neutral'))
    plt.tight_layout()
    plt.show()

