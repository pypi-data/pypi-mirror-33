from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='aio-msgpack-rpc',
    author='Robert Mcgregor',
    url="https://gitlab.com/rmcgregor/aio-msgpack-rpc",
    author_email='rmcgregor1990@gmail.com',
    description="asyncio MsgPack RPC",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['msgpack'],
    packages=['aio_msgpack_rpc'],
    use_scm_version=True,
    python_requires=">=3.6",
    setup_requires=['setuptools_scm'],
    extras_require={"test": ["pytest", "pytest-asyncio", "asyncio_extras"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: AsyncIO",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ]
)