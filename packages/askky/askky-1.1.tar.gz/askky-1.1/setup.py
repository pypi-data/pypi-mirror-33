from setuptools import setup
setup(
    name="askky",
    version="1.1",
    description="Askky Python Client",
    url="https://github.com/Askky/python-askky-sdk.git",
    author="Team Askky",
    author_email="hello@razorpay.com",
    license="MIT",
    install_requires=["requests"],
    include_package_data=True,
    package_dir={'askky': 'askky'},
    packages=['askky'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",

        # List of supported Python versions
        "Programming Language :: Python",
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',

        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)