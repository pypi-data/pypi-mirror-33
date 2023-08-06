#coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/11/29.
# ---------------------------------
from setuptools import  setup,find_packages
setup(
    name="threadspider",
    packages=["threadspider","threadspider.utils","threadspider.utils.tests"],
    version='0.3.2',
    install_requires=["setuptools","psutil","selenium","pybloom","pyquery"],
)