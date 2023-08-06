from setuptools import setup, find_packages
setup(
        name = 'merlin_interface',
        packages = [
            'merlin_interface',
            ],
        version = '0.0.4',
        author = 'Magnus Nord',
        author_email = 'magnunor@gmail.com',
        license = 'GPL v3',
        url = 'https://fast_pixelated_detectors.gitlab.io/merlin_interface/',
        download_url = 'https://gitlab.com/fast_pixelated_detectors/merlin_interface/repository/master/archive.tar?ref=0.0.4',
        description = 'Library for interfacing with the Merlin Medipix3 readout software over the TCP/IP API',
        keywords = [
            'TPC/IP',
            'interface',
            'Merlin',
            'Medipix3',
            'microscopy',
            ],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python :: 3',
            ],
)
