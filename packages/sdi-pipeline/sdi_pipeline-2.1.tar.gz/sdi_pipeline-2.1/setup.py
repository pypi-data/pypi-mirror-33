from distutils.core import setup

with open("README", "r") as fh:
    long_description = fh.read()

setup(name='sdi_pipeline',
      version='2.1',
      description='Optical SETI Image Subtraction Pipeline',
      long_description=long_description,
      author='Andrew Stewart',
      url='https://github.com/andrewhstewart/SDI.git',
      author_email='andrew.henry.stewart@emory.edu',
      packages=['sdi_pipeline'],
#      py_modules=['sdi_pipeline.align_astroalign',
#                  'sdi_pipeline.align_iraf',
#                  'sdi_pipeline.align_template',
#                  'sdi_pipeline.align',
#                  'sdi_pipeline.combine_iraf',
#                  'sdi_pipeline.combine_numpy'
#                  'sdi_pipeline.combine_swarp',
#                  'sdi_pipeline.combine',
#                  'sdi_pipeline.get',
#                  'sdi_pipeline.initialize',
#                  'sdi_pipeline.obtain',
#                  'sdi_pipeline.ref_image',
#                  'sdi_pipeline.simulation',
#                  'sdi_pipeline.stats',
#                  'sdi_pipeline.subtract_hotpants',
#                  'sdi_pipeline.subtract_ibi',
#                  'sdi_pipeline.subtract_iraf',
#                  'sdi_pipeline.subtract_numpy',
#                  'sdi_pipeline.subtract',
#                  'sdi_pipeline.pipeline'
#                  'sdi_pipeline.sex',
#                  'sdi_pipeline.sextractor',
#                  'sdi_pipeline.check_saturation'],
      )