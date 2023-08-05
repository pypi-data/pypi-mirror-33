from setuptools import setup

setup(
    name='Flask-HSExcel',
    version='0.1.1',
    license='MIT',
    author='Alan Zhang',
    author_email='1095087479@qq.com',
    description=u'环思的flask导入excel的插件',
    long_description=__doc__,
    packages=['flask_hsexcel'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'SQLAlchemy',
        'celery',
        'flask-DouWa'
        'Flask-SQLAlchemy',
        'marshmallow',
        'xlrd',
        'xlutils',
        'xlwt',
        'openpxxl'
    ],
    classifiers=[
        'Framework :: Flask',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
