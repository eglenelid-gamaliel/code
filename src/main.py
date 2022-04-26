# main.py
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

import sys

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
gi.require_version("GtkSource", "5")

from gi.repository import Adw, Gdk, Gio, GObject, Gtk, GtkSource

from .window import AboutDialog, CodeWindow, PreferencesWindow

GObject.type_register(GtkSource.View)


class CodeApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id="dev.eglenelidgamaliel.code", flags=Gio.ApplicationFlags.FLAGS_NONE)

        # Add application actions
        self.create_action("about", self.on_about_action)
        self.create_action("preferences", self.on_preferences_action)
        self.create_action("quit", self.on_quit)

        # Map the keyboard shortcuts
        self.set_accels_for_action("win.toggle_sidebar", ["<Ctrl>b"])
        # File actions
        self.set_accels_for_action("win.new_file", ["<Ctrl>n"])
        self.set_accels_for_action("win.open_file", ["<Ctrl>o"])
        self.set_accels_for_action("win.open_folder", ["<Ctrl><Shift>o"])
        # Edit actions
        self.set_accels_for_action("win.save", ["<Ctrl>s"])
        self.set_accels_for_action("win.save_as", ["<Ctrl><Shift>s"])
        # Application actions
        self.set_accels_for_action("app.preferences", ["<Ctrl>comma"])
        self.set_accels_for_action("app.quit", ["<Ctrl>q"])

        # Set the application custom css
        css = b"""
            treeview.navigation-sidebar {border-radius: 5px; padding: 2px 2px 2px 2px;}
            
            treeview.navigation-sidebar > *:hover {background-color: @headerbar_bg_color;}
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = CodeWindow(application=self)
        win.present()

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = AboutDialog(self.props.active_window)
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        about = PreferencesWindow(self.props.active_window)
        about.present()

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def on_quit(self, _, _2):
        """Callback for the app.quit action."""
        self.quit()


def main(version):
    """The application's entry point."""
    app = CodeApplication()
    return app.run(sys.argv)
