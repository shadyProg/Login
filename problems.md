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
    

---

دلوقتي ازاي احط api key في خاجة معينة في settings مثلا زي هتا مفروض احطة بطريقة محترفة ANYMAIL = {
    "MAILTRAP_API_TOKEN": "YOUR_MAILTRAP_API_TOKEN",
}
EMAIL_BACKEND = "anymail.backends.mailtrap.EmailBackend"
DEFAULT_FROM_EMAIL = "hello@demomailtrap.co"


بص يا شادي، لو عايز تحط **API Key في Django Settings بطريقة Professional وآمنة**، أهم قاعدة هي:

> متحطش الـ API Key مباشرة في `settings.py`، ولا ترفعه على GitHub حتى لو الـ repository private.

الطريقة الاحترافية هي إنك تخزن الـ API Key في **Environment Variables**، وDjango يقرأه وقت تشغيل التطبيق.

كده تقدر تستخدم نفس الكود في:

- Local Development.
- GitHub بدون تسريب الـ API Key.
- Production Deployment زي PythonAnywhere أو Docker.

خلينا نطبق ده على إعدادات Mailtrap بتاعتك.

## **1. اعمل ملف&#x20;**`.env`

في نفس مستوى `manage.py`، اعمل ملف اسمه `.env`:

```

MAILTRAP_API_TOKEN=your_actual_mailtrap_token

```

حط الـ API Key الحقيقي هنا، مش في `settings.py`.

شكل المشروع هيكون مثلًا:

```
myproject/
├── manage.py
├── .env
├── .gitignore
├── myproject/
│   ├── settings.py
│   └── urls.py
└── accounts/
```

## **2. اقرأ الـ API Key من&#x20;**`settings.py`

أولًا ثبت مكتبة `django-environ`:

```
pip install django-environ
```

بعد كده في `settings.py`:

```
import environenv = environ.Env()# Load environment variables from .envenv.read_env(BASE_DIR / ".env")
```

تأكد إن `BASE_DIR` متعرف عندك باستخدام `pathlib`، مثلًا:

```
from pathlib import PathBASE_DIR = Path(__file__).resolve().parent.parent
```

ثم إعدادات Mailtrap:

```
ANYMAIL = {    "MAILTRAP_API_TOKEN": env("MAILTRAP_API_TOKEN"),}EMAIL_BACKEND = "anymail.backends.mailtrap.EmailBackend"DEFAULT_FROM_EMAIL = "hello@demomailtrap.co"
```

كده Django هيقرأ الـ token من ملف `.env`، ويضعه في إعدادات Anymail وقت تشغيل التطبيق.

استخدام `django-environ` لقراءة إعدادات البيئة من ملف `.env` موثق في دليل المكتبة.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://django-environ.readthedocs.io\&sz=32)

django-environ+1



## **3. أهم خطوة: امنع رفع&#x20;**`.env`**&#x20;على GitHub**

افتح ملف `.gitignore` وأضف:

```
# Environment variables and secrets
.env
.env.*
!.env.example
```

ولو عايز تعمل ملف يوضح لزملائك المتغيرات المطلوبة، اعمل `.env.example`:

```
MAILTRAP_API_TOKEN=
```

ارفع `.env.example` عادي، لكن لا ترفع `.env`.

لو الملف اتضاف بالفعل إلى Git قبل ما تحطه في `.gitignore`، نفّذ:

```
git rm --cached .env
git commit -m "Remove environment secrets"
```

ده بيشيله من النسخة الحالية في Git، لكن لو الـ API Key اتنشر قبل كده، لازم تعمل له **Revoke أو Rotate** من Mailtrap؛ لأن الـ key ممكن يفضل موجودًا في Git history.

Django نفسه ينصح باستخدام Environment Variables بدل تخزين الأسرار مباشرة في ملفات الإعدادات.&#x20;

[image](https://www.google.com/s2/favicons?domain=https://docs.djangoproject.com\&sz=32)

Django+1



## **4. طريقة أبسط بدون مكتبة**

لو مش عايز تثبت `django-environ`، تقدر تستخدم Python مباشرة:

```
import osANYMAIL = {    "MAILTRAP_API_TOKEN": os.environ["MAILTRAP_API_TOKEN"],}
```

لكن في الحالة دي لازم تكون الـ Environment Variable متعرفة في نظام التشغيل أو في منصة الـ Deployment، لأن Python مش هيقرأ ملف `.env` تلقائيًا.

## **5. لما تعمل Deployment**

في Production، الأفضل إنك تضيف:

```
MAILTRAP_API_TOKEN
```

في Environment Variables الخاصة بمنصة الاستضافة، وتخلي `settings.py` يقرأها بنفس الطريقة.

لو بتستخدم Docker، تقدر تمرر المتغير من ملف `.env` باستخدام `docker compose`، مع التأكد من عدم تضمين الملف في الـ image أو رفعه إلى GitHub.

**الخلاصة:** خلي `settings.py` يحتوي على أسماء الإعدادات وطريقة قراءتها، وخلي الـ API Keys في Environment Variables أو Secret Manager. دي طريقة منظمة وآمنة وقابلة للتوسع لما يكون عندك أكتر من API Key، زي Mailtrap وJWT وDatabase credentials.
---
### in model 
we add this 
```python 
#NOTE: علشان لما تعمل register لل user جديد يعمل profile جديد ليه اوتوماتيك
@receiver(post_save, sender=User)
def save_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

```