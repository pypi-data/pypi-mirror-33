from setuptools import setup, find_packages

def get_long_description():
    with open('README.md') as f:
        return f.read()

setup(
    name='mara-config',
    version='0.1.4',

    description="Mara app composing and configuration infrastructure.",
    long_description=get_long_description(),
    long_description_content_type='text/markdown',



    extras_require={
        'test': ['pytest',
                 'flask>=0.12', 'mara_page' # config views
        ],
    },

    dependency_links=[
        'git+https://github.com/mara/mara-page.git@1.2.3#egg=mara-page-1.2.3',
    ],

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

)
