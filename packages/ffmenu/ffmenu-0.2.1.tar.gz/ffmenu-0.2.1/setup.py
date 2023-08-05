from setuptools import setup

setup(
    name='ffmenu',
    version='0.2.1',
    author=u'Mārtiņš Šulcs',
    author_email='shulcsm@gmail.com',
    packages=['ffmenu', 'ffmenu.templatetags'],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'Django>=1.7'
    ]
)
