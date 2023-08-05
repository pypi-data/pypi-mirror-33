"""setup.py file."""

from setuptools import setup, find_packages

__author__ = 'Alcatel Lucent Enterprise <ebg_global_supportcenter@al-enterprise.com>'


with open("requirements.txt", "r") as fs:
    reqs = [r for r in fs.read().splitlines() if (len(r) > 0 and not r.startswith("#"))]

setup(
    description="Network Automation and Programmability Abstraction Layer with Multivendor support",
    long_description="This driver from Alcatel Lucent Enterprise will support the OmniSwitch Series of Switches namely OS6465, OS6560, OS6860(E), OS6865, OS6900 and OS9900. The driver has been tested with 8.5.R1 Release.",
    name="napalm-aos",
    version="0.1.1",
    packages=find_packages(),
    author="Alcatel Lucent Enterprise",
    author_email="ebg_global_supportcenter@al-enterprise.com",
    zip_safe=False,
    classifiers=[
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    url="https://github.com/napalm-automation/napalm-aos",
    include_package_data=True,
    install_requires=reqs,
)
