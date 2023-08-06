from distutils.core import setup

setup(
	name='phenoai',
	version='0.1.1',
	description='Machine Learning interface for High Energy Physics Phenomenology',
	long_description=open('README.md').read(),
	keywords='high energy physics machine learning phenomenology limits exclusion likleihood likelihoods',
	url='http://hef.ru.nl/~bstienen/phenoai',
	author='Bob Stienen',
	author_email='b.stienen@science.ru.nl',
	license='MIT',
	data_files = [("", ["LICENSE.txt"])],
	packages=['phenoai'],
	classifiers=[
		'Development Status :: 4 - Beta',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6',
		'Intended Audience :: Science/Research',
		'License :: OSI Approved :: MIT License',
		'Natural Language :: English',
		'Topic :: Scientific/Engineering :: Physics',
		'Topic :: Scientific/Engineering :: Artificial Intelligence'],
	install_requires=['pyslha','requests','h5py','numpy','matplotlib','scipy']
)

