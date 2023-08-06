from setuptools import setup


setup(name='microsoftbotframework',
      version='0.3.3',
      description='A wrapper for the microsoft bot framework API',
      classifiers=[
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.6',
            'Topic :: Communications :: Chat',
      ],
      keywords='microsoft bot framework flask celery',
      url='https://github.com/Grungnie/microsoftbotframework',
      author='Matthew Brown',
      author_email='mbrown1508@outlook.com',
      license='MIT',
      packages=['microsoftbotframework'],
      install_requires=[
            "Flask",
            "celery",
            "requests",
            "pyyaml",
      ],
      extras_require={'test': ['nose', 'redis',  'pymongo']},
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose', 'redis', 'pymongo'],
      )
