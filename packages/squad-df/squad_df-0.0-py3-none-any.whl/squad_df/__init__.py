import os
import json
from urllib.request import urlretrieve


def reporter(done, size, total, width=50):
    fraction = done * size / total
    done = int(width * fraction)
    string = '=' * done
    string += '-' * (width - done)
    print(round(fraction, 2), f'[{string}]', end='\r')


class SquadDataset:
    def __init__(self, version, data_folder='.data'):
        self.version = version
        home = os.path.expanduser("~")
        self.data_folder = os.path.join(home, data_folder)
        self.base_url = 'https://rajpurkar.github.io/SQuAD-explorer/dataset/'

    def __ensure_dataset__(self):
        if not os.path.exists(self.data_folder):
            os.mkdir(self.data_folder)
        train_fn = f'train-v{self.version}.json'
        dev_fn = f'dev-v{self.version}.json'
        self.train_path = os.path.join(self.data_folder, train_fn)
        self.dev_path = os.path.join(self.data_folder, dev_fn)
        if not os.path.exists(self.train_path):
            print('Downloading training dataset')
            url = self.base_url + train_fn
            print(url)
            urlretrieve(url, self.train_path, reporter)
        if not os.path.exists(self.dev_path):
            print('Downloading development dataset')
            url = self.base_url + dev_fn
            print(url)
            urlretrieve(url, self.dev_path, reporter)

    def __iter__(self):
        self.__ensure_dataset__()
        for is_train, path in [[True, self.train_path],
                               [False, self.dev_path]]:
            with open(path, 'r') as fl:
                data = json.load(fl)
            for wiki_id, wiki in enumerate(data['data']):
                for para_id, para in enumerate(wiki['paragraphs']):
                    for qas in para['qas']:
                        if qas.get('is_impossible', False):
                            yield {"wiki_id": wiki_id,
                                   'para_id': para_id,
                                   'question': qas['question'],
                                   'context': para['context'],
                                   'answers': [],
                                   'plausible': qas['plausible_answers'],
                                   'possible': False,
                                   'is_train': is_train
                                   }
                        else:  # possible
                            yield {"wiki_id": wiki_id,
                                   'para_id': para_id,
                                   'question': qas['question'],
                                   'context': para['context'],
                                   'answers': qas['answers'],
                                   'plausible': [],
                                   'possible': True,
                                   'is_train': is_train
                                   }


if __name__ == '__main__':
    v2 = SquadDataset('2.0')
    for _ in v2:
        pass
