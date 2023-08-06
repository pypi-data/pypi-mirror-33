from setuptools import setup

setup(name = "django-loggable",
      version = "0.3",
      description = "this library adds 'created_at', 'updated_at' and 'delete_at'  fields like a rail apps in django,"
                    " also added soft delete method",
      long_description=open('README.rst', 'r').read(),
      author = "Carlos Ganoza Plasencia",
      author_email = "cganozap@gmail.com",
      url = "https://github.com/drneox/django_loggable",
      license = "GPL",
      packages=["django_loggable"],
      keywords="django created_at updated_at deleted_at fields models django-admin",
)