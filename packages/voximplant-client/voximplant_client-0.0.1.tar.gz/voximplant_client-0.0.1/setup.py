from setuptools import find_packages, setup

setup(
    name='voximplant_client',
    version='0.0.1',
    description="Voximplant.com API client.",
    keywords=[],
    url="https://github.com/gdml/voximplant-client/",
    author="Fedor Borshev",
    author_email="f@f213.in",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        'Click',
        'requests',
    ],
    entry_points="""
        [console_scripts]
        voximplant = voximplant_client.cli:main
    """,
    include_package_data=True,
    zip_safe=False,
)
