import io
from setuptools import find_packages, setup


with io.open('README.rst') as readme:
    setup(
        name='pyramid_flamegraph',
        version='0.1.1',
        description="Pyramid tween to generate a flamegraph log for every request",
        long_description=readme.read(),
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
        ],
        author='Hideo Hattori',
        author_email='hhatto.jp@gmail.com',
        url='https://gitlab.com/hhatto/pyramid_flamegraph',
        license='MIT',
        keywords='pyramid, flamegraph, profile',
        packages=find_packages(),
        zip_safe=False,
        include_package_data=True,
        entry_points={},
    )
