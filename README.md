ZKB
===

ZKB is a static blog generator written in Python.

Usage
-----

`init [CONFIG]`

This command will try to create the config file in current directory to initialize basic blog information.
Note this command does not initialize git repository for current directory because remote is unknown.
Please modify the config file and run `init-git` to initialize git repository.

* `CONFIG`: name of the config file; if not provided, `config.yml` will be used.

`init-git [CONFIG]`

This command will create a git repository in current folder to store source files, and a git repository in `_site`
directory to store generated pages.
After creating, `_site` will be added into `.gitignore` of repository in current directory.
Default branch of repository of current directory will be renamed to `source`.
Remote configuration in config file will be added for both repositories, so please configure remote correctly in
config file before running this command.

`build [CONFIG]`

This command will build the blog, and generate pages into `_site` directory.
Note that no prompt will show when files got overwritten.

`deploy [CONFIG] [-f|--force]`

This command will push blog source and files inside `_site` to remote git repository.
Currently, only git deploy is support.

* `-f` `--force`: if provided, the `git push` operation will include `--force` parameter.

Roadmap
-------

Future development of ZKB includes:

* Allows user to generate blog in their own languages.
* Add support of deploying with `rsync`.
* Support of other article formats, like ReST, etc.

License
-------

ZKB is licenced under BSD. See [LICENSE](LICENSE) file for details.

Acknowledgement
---------------

Portions of ZKB utilize other copyrighted materials, see [ACKNOWLEDGEMENTS](ACKNOWLEDGEMENTS) file for details.

Contribution
------------

Please report bugs you found and send pull requests for bug fixes and new features.

Bug fixes should also include corresponding test cases.
