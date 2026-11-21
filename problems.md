(.env) D:\special for shady\ComputerScience\SelfStudy\2026\Back-end\Django REST FRAMEWORK\login\Jwttutorial>python manage.py runserver 
Watching for file changes with StatReloader
Performing system checks...

Exception in thread django-main-thread:
Traceback (most recent call last):
  File "C:\Users\ECC.DESKTOP-BOGB7O8\AppData\Local\Python\pythoncore-3.14-64\Lib\threading.py", line 1082, in _bootstrap_inner
    self._context.run(self.run)
    ~~~~~~~~~~~~~~~~~^^^^^^^^^^
  File "C:\Users\ECC.DESKTOP-BOGB7O8\AppData\Local\Python\pythoncore-3.14-64\Lib\threading.py", line 1024, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\special for shady\ComputerScience\SelfStudy\2026\Back-end\Django REST FRAMEWORK\login\.env\Lib\site-packages\django\utils\autoreload.py", line 83, in wrapper
    raise e
  File "D:\special for shady\ComputerScience\SelfStudy\2026\Back-end\Django REST FRAMEWORK\login\.env\Lib\site-packages\django\utils\autoreload.py", line 66, in wrapper
    fn(*args, **kwargs)
    ~~^^^^^^^^^^^^^^^^^
  File "D:\special for shady\ComputerScience\SelfStudy\2026\Back-end\Django REST FRAMEWORK\login\.env\Lib\site-packages\django\core\management\commands\runserver.py", line 134, in inner_run
    self.check(**check_kwargs)
    ~~~~~~~~~~^^^^^^^^^^^^^^^^
  File "D:\special for shady\ComputerScience\SelfStudy\2026\Back-end\Django REST FRAMEWORK\login\.env\Lib\site-packages\django\core\management\base.py", line 575, in check
    raise SystemCheckError(msg)
django.core.management.base.SystemCheckError: SystemCheckError: System check identified some issues:

ERRORS:
auth.User.groups: (fields.E304) Reverse accessor 'Group.user_set' for 'auth.User.groups' clashes with reverse accessor for 'users.User.groups'.
        HINT: Add or change a related_name argument to the definition for 'auth.User.groups' or 'users.User.groups'.
auth.User.user_permissions: (fields.E304) Reverse accessor 'Permission.user_set' for 'auth.User.user_permissions' clashes with reverse accessor for 'users.User.user_permissions'.
        HINT: Add or change a related_name argument to the definition for 'auth.User.user_permissions' or 'users.User.user_permissions'.
users.User.groups: (fields.E304) Reverse accessor 'Group.user_set' for 'users.User.groups' clashes with reverse accessor for 'auth.User.groups'.
        HINT: Add or change a related_name argument to the definition for 'users.User.groups' or 'auth.User.groups'.
users.User.user_permissions: (fields.E304) Reverse accessor 'Permission.user_set' for 'users.User.user_permissions' clashes with reverse accessor for 'auth.User.user_permissions'.
        HINT: Add or change a related_name argument to the definition for 'users.User.user_permissions' or 'auth.User.user_permissions'. 

    مشكلة ديه ظهرت بسبب انا كنت عامل كاستم يوزر ومش حاطه  في apps 
    عامل configre غلط يعني
    