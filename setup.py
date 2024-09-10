from setuptools import find_packages, setup

setup(
    name="enhanced_selenium",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["selenium", "keyboard", "pyparsing"],
    description="A custom Selenium driver package",
    author="Sunwoo Kim",
    author_email="sunshower1127@gmail.com",
    url="https://github.com/sunshower1127/Enhanced-Selenium",  # 프로젝트 URL
)
