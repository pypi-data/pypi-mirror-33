[![Documentation Status](https://readthedocs.org/projects/galaxie-curses/badge/?version=latest)](http://galaxie-curses.readthedocs.io/?badge=latest)
[![pipeline status](https://gitlab.com/Tuuux/galaxie-curses/badges/master/pipeline.svg)](https://gitlab.com/Tuuux/galaxie-curses/commits/master)
[![codecov](https://codecov.io/gl/Tuuux/galaxie-curses/branch/master/graph/badge.svg)](https://codecov.io/gl/Tuuux/galaxie-curses)

Galaxie Curses, The ToolKit
===========================
<div style="text-align:center"><img src ="https://gitlab.com/Tuuux/galaxie-curses/raw/master/docs/source/images/logo_galaxie.png" /></div>

Once upon a time, this project was hosted on a ancient platform called GitHub. Then came the Buyer.
The Buyer bought GitHub, willing to rule over its community.

I was not to sell, so here is the new home of "https://github.com/Tuuux/galaxie-curses".

The Project
-----------
**Galaxie Curses** is a free software ToolKit for the NCurses API.
It can be consider as a text based implementation of the famous GTK+ Library.

Originally the project have start in 2016 when the author Jérôme.O have start to learn Python at home.

The Mission
-----------
Provide a Text Based ToolKit with powerfull high level Widget (Select Color, Printer Dialog, FileSelector).

During lot of years the main stream was to provide big computer with big GUI Toolkit,
unfortunately almost nobody have care about ultra low profile computer and we are now in a situation where no mature
ToolKit is ready to use on **pen computer**. Time's change then it's time to change the world ...

The goal of the version 1.0 will be to create a application like Midnight-Commander with **GLXCurses**.

Midnight-Commander: https://midnight-commander.org

Screenshots
-----------
v0.2
<p align="center">
<img src="https://gitlab.com/Tuuux/galaxie-curses/raw/master/docs/source/images/screen_01.png">
</p>

Example
-------

```python
    #!/usr/bin/env python
    # -*- coding: utf-8 -*-
    import GLXCurses

    # Create the main Application
    app = GLXCurses.Application()
    app.set_name('Galaxie-Curse Container Demo')

    # Create a Window
    win_main = GLXCurses.Window()

    # Create a Frame
    frame1 = GLXCurses.Frame()
    frame1.set_label('A Container Frame')

    # Add the frame to the main window
    win_main.add(frame1)

    # Add the main window inside the application
    app.add_window(win_main)

    # The super function call when press keys
    def handle_keys(self, event_signal, *event_args):
        if event_args[0] == ord('q'):
            # Key "q" was pressed
            GLXCurses.mainloop.quit()

    # Signal
    app.connect('CURSES', handle_keys)

    # Main loop start
    GLXCurses.mainloop.run()
```
More examples can be found here: https://gitlab.com/Tuuux/galaxie-curses/tree/master/examples

Features
--------
* MainLoop
* Signal
* Application Class
* Component like Button, Container, ProgressBar
* Have GTK+ design as roadmap
* Auto Rezize
* Minimize NCurses crash
* Common thing for a text based graphic interface tool kit :)

Roadmap
-------
**Galaxie-Curses** is a Text Based **GTK+** like, then the GTK+ Doc is the **roadmap**.

Yes NCurses haven't icons or pixel management :)

Contribute
----------
The GTK+ v3 documentation is our model: https://developer.gnome.org/gtk3/stable/

- Issue Tracker: https://gitlab.com/Tuuux/galaxie-curses/issues
- Source Code: https://gitlab.com/Tuuux/galaxie-curses

Documentations
--------------
Readthedocs link: http://galaxie-curses.readthedocs.io

Note for GTK+ Project Developer's
---------------------------------
I'm really confuse about the big copy/past i making from the GTK+ documentation during the creation of
the Galaxie-Curses documentation, that because english is not my primary language and i'm a bit limited for make a
ToolKit documentation without that ...
Consider that actual documentation of Galaxie-Curse as the better i can do and it
include to copy/past large parts of the GTK+ documentation. (sorry about that)

As you probably see **Galaxie-Curses** is a Text Based **GTK+** like, then the GTK+ Doc is the **roadmap**.

Thanks
------
All **Galaxie** API is develop with **pycharm** as IDE from **JetBrains** 
link: https://www.jetbrains.com

JetBrains graciously provide to us licenses for **pycharm profesional**

License
-------
GNU GENERAL PUBLIC LICENSE Version 3
https://gitlab.com/Tuuux/galaxie-curses/blob/master/LICENSE