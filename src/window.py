# window.py
#
# Copyright 2022 Eglenelid Gamaliel Gutierrez Hernandez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time
from pathlib import Path

from gi.repository import Adw, Gio, GLib, Gtk, GtkSource

from .widgets import Codeview, FileExplorerView


# Main window class
@Gtk.Template(resource_path="/dev/eglenelidgamaliel/code/window.ui")
class CodeWindow(Adw.ApplicationWindow):
    __gtype_name__ = "CodeWindow"

    # Map widgets from the template
    # Window
    window_title = Gtk.Template.Child()
    # Flap
    flap = Gtk.Template.Child()
    # Sidebar
    open_folder_button = Gtk.Template.Child()
    sidebar_box = Gtk.Template.Child()
    tree_view = None
    # Greeter
    code_greeter = Gtk.Template.Child()
    # Tabs
    toast_overlay = Gtk.Template.Child()
    tab_bar = Gtk.Template.Child()
    tab_view = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Create the 'toggle_sidebar' action referenced in window.ui
        toggle_sidebar_action = Gio.SimpleAction(name="toggle_sidebar")
        toggle_sidebar_action.connect("activate", self.on_toggle_sidebar)
        self.add_action(toggle_sidebar_action)

        # Create the 'new_file' action referenced in window.ui
        new_file_action = Gio.SimpleAction(name="new_file")
        new_file_action.connect("activate", self.on_new_file)
        self.add_action(new_file_action)

        # Create the 'open_file' action referenced in window.ui
        open_file_action = Gio.SimpleAction(name="open_file")
        open_file_action.connect("activate", self.open_file_dialog)
        self.add_action(open_file_action)

        # Create the 'open_folder' action referenced in window.ui
        open_folder_action = Gio.SimpleAction(name="open_folder")
        open_folder_action.connect("activate", self.open_folder_dialog)
        self.add_action(open_folder_action)

        # Create the 'save' action referenced in window.ui
        save_action = Gio.SimpleAction(name="save")
        save_action.connect("activate", self.on_save)
        self.add_action(save_action)

        # Create the 'save_as' action referenced in window.ui
        save_as_action = Gio.SimpleAction(name="save_as")
        save_as_action.connect("activate", self.save_file_dialog)
        self.add_action(save_as_action)

        # Connect the tab bar close-page signal
        self.tab_view.connect("close-page", self.on_tab_close)

        # Get the GSettings instance for the app schema id
        self.settings = Gio.Settings(schema_id="dev.eglenelidgamaliel.code")

        # Remember the window size
        self.settings.bind("window-width", self, "default-width", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-height", self, "default-height", Gio.SettingsBindFlags.DEFAULT)
        self.settings.bind("window-maximized", self, "maximized", Gio.SettingsBindFlags.DEFAULT)

    # Callback for the sidebar toggle action
    def on_toggle_sidebar(self, action, _):
        self.flap.set_reveal_flap(not self.flap.get_reveal_flap())

    # Get current code view
    def get_current_code_view(self):
        return self.tab_view.get_selected_page().get_child().get_child()

    # New file action callback
    def on_new_file(self, action, parameter):
        # Hide the greeter
        self.code_greeter.set_visible(False)
        self.tab_bar.set_visible(True)

        # Create a new editor widget
        new_gtksource_view = Codeview()

        # Create a new scrolled window to hold the editor
        new_scrolleable_window = Gtk.ScrolledWindow()
        new_scrolleable_window.set_child(new_gtksource_view)
        new_scrolleable_window.set_vexpand(True)

        # Create a new tab and add it to the tabview
        newly_created_page = self.tab_view.append(new_scrolleable_window)
        newly_created_page.set_title("Untitled")
        newly_created_page.set_tooltip("Untitled")

        new_gtksource_view.grab_focus()

    # Save (step 1) write or overwrite the file
    def on_save(self, action, _):
        current_code_view = self.get_current_code_view()
        # If the code view has no file, call the save as dialog
        if current_code_view.file:
            self.save_file(current_code_view.file)
        else:
            self.save_file_dialog()

    # Save (step 2) open the file chooser dialog
    def save_file_dialog(self, action=None, _=None):
        self._native = Gtk.FileChooserNative(
            title="Save File As",
            transient_for=self,
            action=Gtk.FileChooserAction.SAVE,
            accept_label="_Save",
            cancel_label="_Cancel",
        )
        self._native.connect("response", self.on_save_response)
        self._native.show()

    # Save (step 3) called when the file chooser dialog is closed
    def on_save_response(self, native, response):
        if response == Gtk.ResponseType.ACCEPT:
            self.save_file(native.get_file())
        self._native = None

    # Save (step 4) called when the file contents are saved
    def save_file(self, file):
        # Get the current code view
        buffer = self.get_current_code_view().get_buffer()
        # Retrieve the iterator at the start of the buffer
        start = buffer.get_start_iter()
        # Retrieve the iterator at the end of the buffer
        end = buffer.get_end_iter()
        # Retrieve all the visible text between the two bounds
        text = buffer.get_text(start, end, False)

        # If there is nothing to save, return early
        if not text:
            return

        bytes = GLib.Bytes.new(text.encode("utf-8"))

        # Start the asynchronous operation to save the data into the file
        file.replace_contents_bytes_async(bytes, None, False, Gio.FileCreateFlags.NONE, None, self.save_file_complete)

    # Save (step 5) called when the file contents finish saving
    def save_file_complete(self, file: Gio.File, result):
        # Keep a reference to the file so we can use it later
        code_view = self.get_current_code_view()
        code_view.file = file

        # Update the code view language
        code_buffer = code_view.get_buffer()
        code_buffer.set_language(GtkSource.LanguageManager.get_default().guess_language(file.get_path()))

        # Update the title of the code view tab
        current_page = self.tab_view.get_selected_page()
        current_page.set_title(file.get_basename())
        current_page.set_tooltip(file.get_path())

        # Show a toast for the successful save
        self.toast_overlay.add_toast(Adw.Toast(title="File saved successfully", timeout=1))

    # Open (step 1) file action callback
    def open_file_dialog(self, action, parameter):
        # Create a new file selection dialog, using the "open" mode
        # and keep a reference to it
        self._native = Gtk.FileChooserNative(
            title="Open file",
            transient_for=self,
            action=Gtk.FileChooserAction.OPEN,
            accept_label="_Open",
            cancel_label="_Cancel",
        )
        # Connect the "response" signal of the file selection dialog;
        # this signal is emitted when the user selects a file, or when
        # they cancel the operation
        self._native.connect("response", self.on_open_response)
        # Present the dialog to the user
        self._native.show()

    # Open (step 2) called when the file chooser dialog is closed
    def on_open_response(self, dialog, response):
        # If the user selected a file...
        if response == Gtk.ResponseType.ACCEPT:
            # ... retrieve the location from the dialog and open it
            self.open_file(dialog.get_file())
        # Release the reference on the file selection dialog now that we
        # do not need it any more
        self._native = None

    # Open (step 3) function to open a file asynchronously
    def open_file(self, file):
        file_path = Path(file.get_path())
        if file_path.is_dir():
            start = time.perf_counter()
            self.open_folder(file_path)
            print(f"Completed Execution in {time.perf_counter() - start} seconds")
        else:
            # Load the file contents asynchronously
            file.load_contents_async(None, self.open_file_complete)

    # Open (step 4) called when the file contents finish loading
    def open_file_complete(self, file, result):
        contents = file.load_contents_finish(result)

        # Try to open the file
        if not contents[0]:
            path = file.peek_path()

        # Check if the file is a text file and UTF-8 encoding
        try:
            text = contents[1].decode("utf-8")
        except UnicodeError as err:
            path = file.peek_path()
            return

        # Hide the greeter
        self.code_greeter.set_visible(False)
        self.tab_bar.set_visible(True)

        # Create a new editor widget
        new_gtksource_view = Codeview()
        new_gtksource_view.file = file
        new_gtksource_view.grab_focus()

        # Load the file contents into the editor instance
        buffer = new_gtksource_view.get_buffer()
        buffer.set_text(text)
        buffer.set_language(GtkSource.LanguageManager.get_default().guess_language(file.get_path()))

        # Place the cursor at the beginning of the file
        start = buffer.get_start_iter()
        buffer.place_cursor(start)

        # Create a new scrolled window to hold the editor
        new_scrolleable_window = Gtk.ScrolledWindow()
        new_scrolleable_window.set_child(new_gtksource_view)
        new_scrolleable_window.set_vexpand(True)

        # Create a new tab and add it to the tabview
        newly_created_page = self.tab_view.append(new_scrolleable_window)
        newly_created_page.set_title(file.get_basename())
        newly_created_page.set_tooltip(file.get_path())

        new_gtksource_view.grab_focus()

    # Open folder (step 1) action callback
    def open_folder_dialog(self, action, parameter):
        self._native = Gtk.FileChooserNative(
            title="Open folder",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER,
            accept_label="_Open",
            cancel_label="_Cancel",
        )
        self._native.connect("response", self.on_open_folder_response)
        self._native.show()

    # Open folder (step 2) called when the folder chooser dialog is closed
    def on_open_folder_response(self, dialog, response):
        # If the user selected a file...
        if response == Gtk.ResponseType.ACCEPT:
            # Hide the folder chooser button
            self.open_folder_button.set_visible(False)

            # Set the window title to the folder name
            self.window_title.set_title(dialog.get_file().get_basename())

            # If there is already a folder open, remove it
            if self.tree_view:
                self.sidebar_box.remove(self.tree_view)

            # Create the file explorer view
            self.tree_view = FileExplorerView(dialog.get_file())

            # Connect the selection "changed" signal of the file explorer view
            select = self.tree_view.get_selection()
            select.connect("changed", self.on_tree_selection_changed)

            # Add the file explorer view to the sidebar
            self.sidebar_box.append(self.tree_view)

            # Reveal the sidebar
            self.flap.set_reveal_flap(True)

        # Release the reference on the file selection dialog now that we
        # do not need it any more
        self._native = None

    # Called when the user selects a file in the file explorer view
    def on_tree_selection_changed(self, selection):
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            path = Path(model[treeiter][1])
            if not path.is_dir():
                gfile = Gio.File.new_for_path(model[treeiter][1])
                self.open_file(gfile)

    # Called when the user closes a tab
    def on_tab_close(self, tab_view, tab_page):
        if self.tab_view.get_n_pages() == 1:
            self.code_greeter.set_visible(True)
            self.tab_bar.set_visible(False)


# About dialog
class AboutDialog(Gtk.AboutDialog):
    def __init__(self, parent):
        Gtk.AboutDialog.__init__(self)
        self.props.program_name = "Code"
        self.props.version = "0.0.1"
        self.props.authors = ["Eglenelid Gamaliel Gutierrez Hernandez"]
        self.props.copyright = "2022 Eglenelid Gamaliel Gutierrez Hernandez"
        self.props.logo_icon_name = "dev.eglenelidgamaliel.code"
        self.props.modal = True
        self.set_transient_for(parent)


# Preferences dialog
@Gtk.Template(resource_path="/dev/eglenelidgamaliel/code/gtk/preferences_window.ui")
class PreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = "PreferencesWindow"

    preferences_style_group = Gtk.Template.Child()

    def __init__(self, window):
        Adw.PreferencesWindow.__init__(self)

        self.props.modal = True
        self.set_transient_for(window)

        self.settings = Gio.Settings(schema_id="dev.eglenelidgamaliel.code")

        style_chooser = GtkSource.StyleSchemeChooserWidget()
        style_chooser.connect("notify::style-scheme", self.on_scheme_changed)

        self.preferences_style_group.add(style_chooser)

    def on_scheme_changed(self, widget, param):
        self.settings.set_string("code-view-style-scheme", widget.get_style_scheme().get_id())
