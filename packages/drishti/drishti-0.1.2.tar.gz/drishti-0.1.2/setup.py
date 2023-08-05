from setuptools import setup, find_packages


setup(name='drishti',
      version='0.1.2',
      url='https://gitlab.com/abhishek.ambastha/computer-vision/tree/master/drishti',
      license='MIT',
      author='Abhishek Ambastha',
      author_email='ambastha.abhishek@gmail.com',
      description='module to simplify computer vision tasks',
      packages= ['drishti', 'drishti/datasets', 'drishti/datasets/pascal'],
      install_requires=['numpy', 'matplotlib', 'untangle', 'tqdm', 'opencv-python'],
      zip_safe=False)
