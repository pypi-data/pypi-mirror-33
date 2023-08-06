#!/usr/bin/python

#
# Project Librarians: Shasvath J. Kapadia
#              Postdoctoral Researcher
#              UW-Milwaukee Department of Physics
#              Center for Gravitation & Cosmology
#              <shasvath.kapadia@ligo.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from setuptools import setup, find_packages

setup(
    name='p_astro',
    version='0.1',
    url='http://gracedb.ligo.org',
    author='Shasvath Kapadia',
    author_email='shasvath.kapadia@ligo.org',
    maintainer="Deep Chatterjee, Heather Fong, Surabhi Sachdev",
    maintainer_email="deep.chatterjee@ligo.org, heather.fong@ligo.org, surabhi.sachdev@ligo.org",
    description='Low-latency estimation of category-wise astrophysical probability of GW candidates',
    license='GNU General Public License Version 3',
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics"
    ),
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    namespace_packages=['ligo'],
    install_requires=[
        'numpy',
        'scipy',
    ],
    python_requires='>=3.0',
)
