QFlashlight
===========

QFlashlight is a simple application that will fill the whole screen
with a solid color. The color can be selected via command line with
`--color` optional or interactively via the color picker (press 'C').
Fullscreen can be entered and left with a double click. The mouse
cursor can be hidden by pressing 'M'.

    usage: qflashlight [-h] [-c COLOR] [-w] [-m] [-b] [-g WxH+X+Y]
                       [FILE [FILE ...]]

    QFlashlight - Fill the screen with a solid color

    positional arguments:
      FILE

    optional arguments:
      -h, --help            show this help message and exit
      -c COLOR, --color COLOR
                            Color to use for the background (#FFF, #FFFFFF or
                            name)
      -w, --window          Start in window mode
      -m, --hide-cursor     Hide the mouse cursor
      -b, --borderless      Run the window without a border
      -g WxH+X+Y, --geometry WxH+X+Y
                            Set the size and position of the window
