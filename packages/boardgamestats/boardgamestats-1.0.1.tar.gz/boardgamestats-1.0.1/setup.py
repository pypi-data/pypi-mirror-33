from setuptools import setup
setup(
  name = 'boardgamestats',
  packages = ['boardgamestats'], 
  version = '1.0.1',
  license='MIT',
  python_requires='>=3',
  description = 'Python wrapper to pull latest board game rankings from wwww.boardgamegeek.com',
  author = 'Aadhi Manivannan',
  author_email = 'dnrkaseff360@gmail.com',
  url = 'https://github.com/DnrkasEFF/BoardGameStats',
  download_url = 'https://github.com/DnrkasEFF/boardgamestats/archive/1.0.1.tar.gz',
  keywords = ['board games', 'boardgamegeek', 'python', 'wrapper', 'board game stats'],
  install_requires=['requests', 'lxml'],
  classifiers = [],
)