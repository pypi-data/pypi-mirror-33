from setuptools import setup, find_packages

setup(  
    # Application name
    name='magicstr',

    # Version number
    version='3.62',

    # Author information
    author='wombatwen',
    author_email='wombatwen@gmail.com',

    # Description
    description='Do some magic on your strings files.',
 
    # Package
    # packages=['magicstr'],
    packages=find_packages(),
    package_data={
        'magicstr' : ['template_strings.xml']
    },

    # Include additional file into the package
    #include_package_data=True,

    # Url details
    url='',

    # Dependent packages
    install_requires=[
        'gspread', 
        'lxml',
        'oauth2client'    
    ],

    # scripts
    scripts = ['magicstr/magicstr']
)
