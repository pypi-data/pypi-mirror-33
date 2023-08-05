from setuptools import setup


version = {}
with open("datasmash/_version.py") as fp:
    exec(fp.read(), version)


setup(name='datasmash',
      version=version['__version__'],
      packages=['datasmash.bin', 'datasmash'],
      keywords='d3m_primitive',
      install_requires=['pandas', 'numpy', 'scikit-learn', 'imageio', 'd3m'],
      include_package_data=True,
      package_data={
          'bin':
              ['bin/smash',
               'bin/embed',
               'bin/smashmatch',
               'bin/Quantizer',
               'bin/serializer',
               'bin/genESeSS',
               'bin/genESeSS_feature',
               'bin/XgenESeSS'
              ]
      },

      # metadata for PyPI upload
      url='https://gitlab.datadrivendiscovery.org/uchicago/datasmash',
      download_url=('https://gitlab.datadrivendiscovery.org/uchicago/datasmash/archive/'
                    + version['__version__'] + '.tar.gz'),

      maintainer_email='wmowkm@gmail.com',
      maintainer='Warren Mo',

      description=('Quantifier of universal similarity amongst arbitrary data'
                   + ' streams without a priori knowledge, features, or'
                   + ' training.'),

      classifiers=[
          "Programming Language :: Python :: 3"
      ],
      entry_points={
          'd3m.primitives': [
              'datasmash.SmashClassification= datasmash.classification:SmashClassification',
              'datasmash.CSmashClassification= datasmash.cclassification:CSmashClassification',
              'datasmash.GSmashClassification= datasmash.gclassification:GSmashClassification',
              'datasmash.CGSmashClassification= datasmash.cgclassification:CGSmashClassification',
              'datasmash.SmashClustering= datasmash.clustering:SmashClustering',
              'datasmash.SmashDistanceMetricLearning= datasmash.distance_metric_learning:SmashDistanceMetricLearning',
              'datasmash.SmashEmbedding= datasmash.embedding:SmashEmbedding',
              'datasmash.SmashFeaturization= datasmash.featurization:SmashFeaturization',
              'datasmash.XG1= datasmash.xgenesess:XG1',
              'datasmash.XG2= datasmash.genesess:XG2',
          ],
      },
     )
