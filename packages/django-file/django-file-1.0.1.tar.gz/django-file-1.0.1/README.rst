===========
django-file
===========

Django File Relative

Installation
============

::

    pip install django-file


Usage
=====

::

    from django_file import calculate_md5

    def xxx(request):
        photo = request.FILES.get('photo', '')
        # if photo:
        #     md5 = calculate_md5(photo)
        md5 = calculate_md5(photo)

