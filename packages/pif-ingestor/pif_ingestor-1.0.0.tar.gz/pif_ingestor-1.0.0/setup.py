from setuptools import setup, find_packages

setup(name='pif_ingestor',
      version='1.0.0',
      url='http://github.com/CitrineInformatics/pif-ingestor',
      description='Script to ingest common data formats into Citrination',
      author='Max Hutchinson',
      author_email='maxhutch@citrine.io',
      packages=find_packages(),
      entry_points={
          'console_scripts': [
              'pif-ingestor = pif_ingestor:drive_cli'
          ]
      },
      install_requires=[
          "pypif>=2.0.0,<3",
          "pypif_sdk>=2.0.0,<3",
          "citrination_client>=2,<4",
          "stevedore"
      ],
      extra_require={
          "all" : ["dfttopif", "globus_sdk", "mdf_forge", "matmeta"],
          "mdf" : ["globus_sdk", "mdf_forge"],
          "dft" : ["dfttopif"],
          "matmeta": ["matmeta"],
      }
)
