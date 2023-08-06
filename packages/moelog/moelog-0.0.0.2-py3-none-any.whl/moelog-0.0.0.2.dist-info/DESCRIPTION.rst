A easy to use Logger
====================

--------------

I hate to always write code like
``logging.basicConfig(level = logging.INFO,format = '%(asctim ...`` So
..

--------------

::

   import moelog

   l = moelog.get_logger(both_to_file_path=r'.\t.log')

   l.info('moelog main')
   l.i('moelog main')

   l.e('nooooooo!')
   '''
   2018-06-27 05:21:52,632 [INFO]  :moelog main
   2018-06-27 05:21:52,632 [INFO]  :moelog main
   2018-06-27 05:21:52,632 [ERROR] :nooooooo!
   '''


