# yatrash
Safely move files into a trash can.

Train yourself to use `trash` instead of `rm`.

Now living on [Github][5]

## Detailed usage

```
$ trash --help
usage: __main__.py [-h] [--trash-dir TRASH_DIR]
                   [trash_files [trash_files ...]]

...
see the real --help for more
```

## Why do we need another trash utility?

This is mostly for self-educational purposes.

If you actually want a trash utility, see [trash-cli][1] which
implements the [xdg trash specification][2], so it will play nicely
with your Desktop's trash and other tools. It also features more
utilities, such as recover.

## Origin

- [CodeReview][3]
- [Github Gist][4]
- [Github Repository][4] (current home)

[1]: https://pypi.org/project/trash-cli/
[2]: http://www.ramendik.ru/docs/trashspec.html
[3]: https://gist.github.com/charmoniumQ/0c5fe34dbb5b3905440a3b06c4f60634
[4]: https://codereview.stackexchange.com/questions/188842/safely-trash-instead-of-rm
[5]: https://github.com/charmoniumQ/yatrash/
