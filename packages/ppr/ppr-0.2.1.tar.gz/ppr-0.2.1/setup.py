from setuptools import setup, find_packages, Extension

graph_module = Extension('_graph',
    language="c++",
    extra_compile_args=['-std=c++11'],
    sources=['src/ppr/cpp/graph.i', 'src/ppr/cpp/src/graph.cpp'],
    include_dirs=['src/ppr/cpp/include'],
    swig_opts=['-c++', '-I ppr/cpp']
    )

geometry_module = Extension('_geometry',
    language="c++",
    extra_compile_args=['-std=c++11'],
    sources=['src/ppr/cpp/geometry.i', 'src/ppr/cpp/src/geometry.cpp'],
    include_dirs=['src/ppr/cpp/include', '/usr/include/eigen3'],
    swig_opts=['-c++', '-I ppr/cpp']
    )

setup(
    name = 'ppr',
    version = '0.2.1',
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'':'src'},
    description = 'Planar Python Robotics',
    long_description=('Software tool to experiment with 2D motion planning problems' +
    'for robot manipulators.'),
    author = 'Jeroen De Maeyer',
    author_email = 'jeroen.demaeyer@kuleuven.be',
    url = 'https://u0100037.pages.mech.kuleuven.be/planar_python_robotics/',
    download_url = 'https://gitlab.mech.kuleuven.be/u0100037/planar_python_robotics/raw/master/dist/ppr-0.2.0.tar.gz',
    keywords = ['robotics', 'motion planning'],
    classifiers = [],
    install_requires=['scipy', 'matplotlib'],
    python_requires='>=3',
    ext_package='ppr.cpp',
    ext_modules=[graph_module, geometry_module],
)
