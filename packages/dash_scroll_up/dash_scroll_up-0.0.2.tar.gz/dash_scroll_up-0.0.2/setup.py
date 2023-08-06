from setuptools import setup

exec (open('dash_scroll_up/version.py').read())

setup(
    name='dash_scroll_up',
    version=__version__,
    author='martinbaste',
    packages=['dash_scroll_up'],
    include_package_data=True,
    license='MIT',
    description='Dash component to add custom button to scroll to the top of the page.',
    install_requires=[]
)
