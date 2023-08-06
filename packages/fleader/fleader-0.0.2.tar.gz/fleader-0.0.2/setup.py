from setuptools import setup, find_packages            #这个包没有的可以pip一下

setup(
    name = "fleader",      #这里是pip项目发布的名称
    version = "0.0.2",  #版本号，数值大的会优先被pip
    keywords = ("pip", "fleader"),
    description = "Pythonic request Library",
    long_description = "Pythonic request Library",
    license = "GNU Licence",

    url = "https://github.com/m1coco/Fleader",     #项目相关文件地址，一般是github
    author = "kele",
    author_email = "loser7758@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["requests","beautifulsoup4"]          #这个项目需要的第三方库
)