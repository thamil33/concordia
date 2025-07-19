```bash
Error[vscode-pytest]: unable to read testIds from temp file

ERROR: pytest-cov is not installed, please install this before running pytest with coverage as pytest-cov is required.

Traceback (most recent call last):
  File "c:\Users\tyler\.vscode\extensions\ms-python.python-2025.10.0-win32-x64\python_files\vscode_pytest\run_pytest_script.py", line 64, in <module>
<<<PYTHON-EXEC-OUTPUT
    pytest.main(arg_array)
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\config\__init__.py", line 156, in main
    config = _prepareconfig(args, plugins)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\config\__init__.py", line 342, in _prepareconfig
    config = pluginmanager.hook.pytest_cmdline_parse(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_hooks.py", line 513, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
    raise exception.with_traceback(exception.__traceback__)
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_callers.py", line 122, in _multicall
    teardown.throw(exception)  # type: ignore[union-attr]
    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\helpconfig.py", line 112, in pytest_cmdline_parse
    config = yield
             ^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_callers.py", line 103, in _multicall
    res = hook_impl.function(*args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\config\__init__.py", line 1146, in pytest_cmdline_parse
    self.parse(args)
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\config\__init__.py", line 1527, in parse
    self._preparse(args, addopts=addopts)
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\config\__init__.py", line 1431, in _preparse
    self.hook.pytest_load_initial_conftests(
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_hooks.py", line 513, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
    raise exception.with_traceback(exception.__traceback__)
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_callers.py", line 122, in _multicall
    teardown.throw(exception)  # type: ignore[union-attr]
    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\warnings.py", line 129, in pytest_load_initial_conftests
    return (yield)
            ^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_callers.py", line 122, in _multicall
    teardown.throw(exception)  # type: ignore[union-attr]
    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\capture.py", line 173, in pytest_load_initial_conftests
    yield
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_callers.py", line 103, in _multicall
    res = hook_impl.function(*args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\Users\tyler\.vscode\extensions\ms-python.python-2025.10.0-win32-x64\python_files\vscode_pytest\__init__.py", line 71, in pytest_load_initial_conftests
    raise VSCodePytestError(
vscode_pytest.VSCodePytestError:

ERROR: pytest-cov is not installed, please install this before running pytest with coverage as pytest-cov is required.


During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "c:\Users\tyler\.vscode\extensions\ms-python.python-2025.10.0-win32-x64\python_files\get_output_via_markers.py", line 26, in <module>
    runpy.run_path(module, run_name="__main__")
  File "<frozen runpy>", line 287, in run_path
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
  File "c:\Users\tyler\.vscode\extensions\ms-python.python-2025.10.0-win32-x64\python_files\vscode_pytest\run_pytest_script.py", line 67, in <module>
    run_pytest(args)
  File "c:\Users\tyler\.vscode\extensions\ms-python.python-2025.10.0-win32-x64\python_files\vscode_pytest\run_pytest_script.py", line 23, in run_pytest
    pytest.main(arg_array)
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\config\__init__.py", line 156, in main
    config = _prepareconfig(args, plugins)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\config\__init__.py", line 342, in _prepareconfig
    config = pluginmanager.hook.pytest_cmdline_parse(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_hooks.py", line 513, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
    raise exception.with_traceback(exception.__traceback__)
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_callers.py", line 122, in _multicall
    teardown.throw(exception)  # type: ignore[union-attr]
    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\helpconfig.py", line 112, in pytest_cmdline_parse
    config = yield
             ^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_callers.py", line 103, in _multicall
    res = hook_impl.function(*args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\config\__init__.py", line 1146, in pytest_cmdline_parse
    self.parse(args)
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\config\__init__.py", line 1527, in parse
    self._preparse(args, addopts=addopts)
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\config\__init__.py", line 1431, in _preparse
    self.hook.pytest_load_initial_conftests(
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_hooks.py", line 513, in __call__
    return self._hookexec(self.name, self._hookimpls.copy(), kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_manager.py", line 120, in _hookexec
    return self._inner_hookexec(hook_name, methods, kwargs, firstresult)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_callers.py", line 139, in _multicall
    raise exception.with_traceback(exception.__traceback__)
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_callers.py", line 122, in _multicall
    teardown.throw(exception)  # type: ignore[union-attr]
    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\warnings.py", line 129, in pytest_load_initial_conftests
    return (yield)
            ^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_callers.py", line 122, in _multicall
    teardown.throw(exception)  # type: ignore[union-attr]
    ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\_pytest\capture.py", line 173, in pytest_load_initial_conftests
    yield
  File "C:\Users\tyler\miniconda3\envs\a0\Lib\site-packages\pluggy\_callers.py", line 103, in _multicall
    res = hook_impl.function(*args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "c:\Users\tyler\.vscode\extensions\ms-python.python-2025.10.0-win32-x64\python_files\vscode_pytest\__init__.py", line 71, in pytest_load_initial_conftests
    raise VSCodePytestError(
vscode_pytest.VSCodePytestError:

ERROR: pytest-cov is not installed, please install this before running pytest with coverage as pytest-cov is required.

ERROR conda.cli.main_run:execute(125): `conda run python c:\Users\tyler\.vscode\extensions\ms-python.python-2025.10.0-win32-x64\python_files\get_output_via_markers.py c:\Users\tyler\.vscode\extensions\ms-python.python-2025.10.0-win32-x64\python_files\vscode_pytest\run_pytest_script.py --rootdir=c:\Users\tyler\dev\concordia\concordia` failed. (See above for error)
Finished running tests!
