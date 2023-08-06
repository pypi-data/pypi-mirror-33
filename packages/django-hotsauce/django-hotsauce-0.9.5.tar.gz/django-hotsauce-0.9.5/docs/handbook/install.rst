=======
Install
=======


:Author: Etienne Robillard <tkadm30@yandex.com>
:Version: 0.9.4

The django-hotsauce library can be installed normally using the ``pip``
extension. ::

    % pip install Django-hotsauce

To develop locally, you can use the "develop" command provided by
setuptools to install a symlink to the source directory: ::

    % sudo make develop

Note: This is the recommended method to install django-hotsauce.

To build the documentation, Sphinx and Doxygen are needed. Sphinx
is used to build the standard documentation and Doxygen for the API
documentation: ::

    % sudo make doxygen          # generate the API docs
    % make -f docs/Makefile html # generate the HTML docs (work-in-progress)

