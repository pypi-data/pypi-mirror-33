from setuptools import setup, find_packages


pkj_name = 'postie'


with open('README.rst') as f:
    readme = f.read()

setup(
    name='django-postie',
    version='0.5.3',
    install_requires=[
        'django>=2',
        'django-ckeditor',
        'django-codemirror2',
        'django-model-utils',
        'django-parler'
    ],
    packages=[pkj_name] + [pkj_name + '.' + x for x in find_packages(pkj_name)],
    url='https://gitlab.com/cyberbudy/django-postie',
    license='MIT',
    author='cyberbudy',
    author_email='cyberbudy@gmail.com',
    description='Django mailing through admin',
    long_description=readme,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3'
    ]

)
