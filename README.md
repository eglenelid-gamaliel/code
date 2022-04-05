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

## Roadmap to v1.0
  - Have an adaptive and toggleable sidebar to browse files on the workspace folder
  - Save the app state and auto save files
  - Have a toggleable terminal targetting to the workspace folder
  - Expose the editor settings through a preferences dialog
  - Be GNOME Human Interface Guidelines compliant (Icons, alerts, toasts, etc)
  - Have a functional theming API

### Future
  - Develop a Git panel to manage pulls, files to commit and change between branches
  - Develop an extension API to integrate development tools like pylint, black, jedi, etc...

## Development and building
  The app can be build with GNOME Builder, the goal is to distribute it through Flatpak
