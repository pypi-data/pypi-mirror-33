import setuptools

setuptools.setup(
        name="holmos_camera_server",
        version="0.0.1",
        author="Christoph Stelz",
        author_email="mail@ch-st.de",
        description="Serves raw bayer frames over HTTP",
        url="https://github.com/holmos-frs/camera-server",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "Topic :: Education",
        ],
)
