from setuptools import setup, find_packages

LONG_DESCRIPTION = """
This Library provide several methods for the control of the flow of your program.
You can make Recursive a function , change the font color and the background color of your program,
improve yourself with the Simple MultiThreading that this library offer.
You can manage Server and Client in local, there is also a class for the
management of the SQL Database, based on sqlite3.
Server Hacking Tools are provided by this Library.
'Shell' class is a Class neededonly for me.
There are also an 'old_perks' library,
with the overload of some standard built-in types,
like Int, String, List and Float.
You can also send an e-mail in a very simple way during your program.
There are more and more method to learn so,
Good Luck!
"""

setup(name='perks',
      version='1.26.1',
      author='Marco Della Putta',
      author_email='marcodp183@gmail.com',
      url='https://github.com/Marco-Della-Putta/perks',
      maintainer='Marco Della Putta',
      maintainer_email='marcodp183@gmail.com',
      description='A powerful package that provide some interesting function',
      license='GNU License',
      packages=find_packages(),
      long_description=LONG_DESCRIPTION   
      )
