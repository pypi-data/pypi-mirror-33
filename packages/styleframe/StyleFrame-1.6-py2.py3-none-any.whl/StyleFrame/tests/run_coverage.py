import coverage
import webbrowser
from StyleFrame import tests

cov = coverage.Coverage(omit=[r'C:\Users\Adi\Documents\Python\StyleFrame\StyleFrame\warnings_conf.py',
                              r'C:\Users\Adi\Documents\Python\StyleFrame\StyleFrame\utils.py',
                              r'C:\Users\Adi\Documents\Python\StyleFrame\StyleFrame\command_line\tests\*',
                              r'C:\Users\Adi\Documents\Python\StyleFrame\StyleFrame\tests\*'],
                        branch=True)
cov.exclude(r'(raise)|(import)|(if PY2)')
cov.exclude(r'(def)|(class)', which='partial')
cov.start()
tests.run()
cov.stop()
cov.save()
cov.html_report()
webbrowser.open_new(r'C:\Users\Adi\Documents\Python\StyleFrame\StyleFrame\tests\htmlcov\index.html')
