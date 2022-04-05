# Code

A text editor built with GTK 4, LibAdwaita 1 and GtkSourceView 5, written in Python 3 thanks to the PyGObject bindings

Currently the project it's on early development stages

## Features

  - Open file (Choose a file and place it on a new tab)
  - Create file (Create a new text editor on a new tab)
  - Save (Overwrite) 
  - Save as... (Optional for existing files but mandatory for new files)
  - Tab navigation (to edit multiple files at the same time)
  - Keyboard shortcuts

## Roadmap
  - Be GNOME Human Interface Guidelines compliant (Icons, alerts, toasts, etc)
  - Have an adaptive sidebar to browse files on the workspace folder
  - Have a functional theming API
  - Expose the editor settings through a preferences dialog

## Development and building
  The app can be build through GNOME Builder, the goal is to distribute it through Flatpak
