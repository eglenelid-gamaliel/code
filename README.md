# Code

A text editor built with GTK 4, LibAdwaita 1 and GtkSourceView 5, written in Python 3 thanks to the PyGObject bindings

Currently the project it's on early development stages

## Features

  **Files**
  - Open file (Choose a file and place it on a new tab)
  - New file (Create a new text editor on a new tab)
  - Save (Overwrite)
  - Save as... (Optional for existing files but mandatory for new files)

  **UI**
  - Tab navigation (to edit multiple files at the same time)
  - Toggleable sidebar to browse files on the workspace folder
  - Keyboard shortcuts (not configurable)

  **Source View**
  - Syntax highlighting (not configurable)
  - Line numbers (not configurable)
  - Style schemes

## Roadmap to v1.0

  **Application**
  - Make the features configurable through the preferences window
  - Save the app state (open files, current tab, etc)
  - Make the app themeable

  **UI**
  - Search file
  - Have a toggleable terminal targetting to the workspace folder
  - Be GNOME Human Interface Guidelines compliant (Icons, alerts, toasts, etc)
  - Make the file explorer detect changes in the current directory and update the sidebar accordingly

  **Source View**
  - Search
  - Go to line
  - Make the font famity and size configurable through the preferences window
  - Properly handle indentation (tabs and spaces)

### Future
  - Develop a Git panel to manage pulls, files to commit and change between branches
  - Develop an extension API to integrate development tools like pylint, black, jedi, etc...

## Development and building
  The app can be build with GNOME Builder, the goal is to distribute it through Flatpak
