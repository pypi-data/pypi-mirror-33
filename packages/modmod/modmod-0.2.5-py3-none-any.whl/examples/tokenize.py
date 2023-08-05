from typing import List

import nltk

from modmod.model import Model


class SplitString(Model):
  def call(self, s: str) -> List[str]:
    return s.split(' ')


class Normalize(Model):
  def call(self, s: str) -> str:
    return s.lower()


class RemoveStopwords(Model):
  def __init__(self, pool, config, stopwords):
    super().__init__(pool, config)
    self.stopwords = stopwords

  @classmethod
  def create(cls, pool, config):
    nltk.download('stopwords')
    stopwords = nltk.corpus.stopwords.words('english')
    stopwords.append('')
    stopwords.remove('not')
    stopwords.remove('no')
    return RemoveStopwords(pool, config, stopwords)

  def call(self, words: List[str]) -> List[str]:
    return list(filter(lambda w: w not in self.stopwords, words))


class Tokenizer(Model):
  def __init__(self, pool, config):
    super().__init__(pool, config)
    self.split = pool.get(SplitString)
    self.normalize = pool.get(Normalize)
    self.remove_stopwords = pool.get(RemoveStopwords)

  def call(self, s: str) -> List[str]:
    tokens = self.split(s)
    tokens = [self.normalize(token) for token in tokens]
    tokens = self.remove_stopwords(tokens)
    return tokens


if __name__ == '__main__':
  tokenizer = Tokenizer.get()
  print(tokenizer("Hello, world"))

