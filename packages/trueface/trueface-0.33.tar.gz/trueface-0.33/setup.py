from setuptools import setup,find_packages

setup(name='trueface',
      version='0.33',
      description='Trueface.ai Face Recognition',
      url='https://github.com/getchui/truefacesdk',
      author='Nezare Chafni',
      author_email='nchafni@truface.ai',
      license='MIT',
      packages=['trueface'],
      package_data={'trueface': ['model/*json', 'model/*caffemodel', 'model/*prototxt','model/*params','logo.png']},
      install_requires=[
                'pubnub',
                'imutils',
                'opencv-python',
                'mxnet',
                'dlib',
                'requests',
                'requests_futures',
                'mss',
                'art',
                'numpy',
                'pandas',
                'termcolor',
                'docker'
            ],
      entry_points={
       'console_scripts': [
           'trueface = trueface.trueface:main',
           'enroll = trueface.enroll:main',
           'trueface-server = trueface.server:main',

       ],
      },
      zip_safe=False)