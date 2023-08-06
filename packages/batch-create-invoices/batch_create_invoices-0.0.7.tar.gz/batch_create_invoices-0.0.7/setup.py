import setuptools

setuptools.setup(
    name='batch_create_invoices',
    version='0.0.7',
    author='Lewis Zhang',
    author_email='244563813@qq.com',
    description='A util for batch create mock invoice for tradeshift.',
    long_description='A util for batch create mock invoice for tradeshift platform. This is used for test only!',
    long_description_content_type='text/raw',
    url='',
    packages=setuptools.find_packages(),
    install_requires=['requests'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    )
)