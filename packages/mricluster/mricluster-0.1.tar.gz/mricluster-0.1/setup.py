from setuptools import setup

setup(name='mricluster',
      version='0.1',
      description='MRI image set clustering module based on Convolutional Neural Network model',
      long_description='',
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
      ],
      url='https://github.com/terrenceliu/MRI_Clustering',
      author='Terrence Liu',
      author_email='terrenceliu@rice.edu',
      license='MIT',
      packages=['mricluster'],
      install_requires= [
            'numpy',
            'pandas',
            'matplotlib',
            'tensorflow-gpu',
            'keras'
      ],
      zip_safe=False)