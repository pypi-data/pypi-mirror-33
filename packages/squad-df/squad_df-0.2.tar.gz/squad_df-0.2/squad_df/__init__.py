import os
import json
import requests


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
            url = self.base_url + train_fn
            print(f'Downloading {url}')
            r = requests.get(url)
            with open(self.train_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        if not os.path.exists(self.dev_path):
            url = self.base_url + dev_fn
            print(f'Downloading {url}')
            r = requests.get(url)
            with open(self.dev_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

    def __iter__(self):
        self.__ensure_dataset__()
        for is_train, path in [[True, self.train_path],
                               [False, self.dev_path]]:
            with open(path, 'r') as fl:
                data = json.load(fl)
            for wiki_id, wiki in enumerate(data['data']):
                for para_id, para in enumerate(wiki['paragraphs']):
                    for qas in para['qas']:
                        data = {"wiki_id": wiki_id,
                                'para_id': para_id,
                                'question_id': qas['id'],
                                'question': qas['question'],
                                'context': para['context'],
                                'is_train': is_train,
                                'answers': qas.get('answers', []),
                                'plausible': qas.get('plausible_answers', []),
                                'possible': not qas.get('is_impossible', False)
                                }
                        yield data


v1 = SquadDataset('1.1')
v2 = SquadDataset('2.0')
if __name__ == '__main__':
    for _ in v1:
        pass
    for _ in v2:
        pass
