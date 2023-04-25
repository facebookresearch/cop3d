# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.


import setuptools

setuptools.setup(
    name="cop3d",
    version="1.0.0",
    author="Meta AI",
    author_email="romansh@meta.com",
    packages=setuptools.find_packages(),
    license="LICENSE",
    description="Common Pets in 3D tools",
    long_description=open("README.md").read(),
    install_requires=[
        "co3d @ git+ssh://git@github.com/facebookresearch/co3d.git#egg=co3d-2.1.0"
    ],
)
