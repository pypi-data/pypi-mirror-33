from distutils.core import setup

setup(name="py-app",
      description="Simple helpers for python apps",
      version="0.7.0",
      author="Eric Faurot",
      author_email="eric@faurot.net",
      url="https://github.com/ericfaurot/py-app",
      classifiers = [
          "Programming Language :: Python",
          "Programming Language :: Python :: 3",
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: ISC License (ISCL)",
          "Operating System :: OS Independent",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      packages=[ "app", "app.tests" ])
