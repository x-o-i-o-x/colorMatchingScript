"""
gui.py

Dear PyGui-based GUI for the Terrain Color Mapper application.
"""

import dearpygui.dearpygui as dpg


class TerrainColorMapperGUI:
    def __init__(self, title="Terrain Color Mapper", width=1000, height=700):
        """Initialize the GUI."""
        self.title = title
        self.width = width
        self.height = height
        
        # Create context
        dpg.create_context()
        
        # Create viewport
        dpg.create_viewport(title=self.title, width=self.width, height=self.height)

    def _setup(self):
        """Set up the main UI elements."""
        with dpg.window(label="Main Window", pos=(0, 0), width=self.width, height=self.height, no_close=True):
            dpg.add_text("Hello World!")
            dpg.add_text("Terrain Color Mapper GUI", color=(100, 200, 255))

    def _show(self):
        """Display the GUI and start the main loop."""
        dpg.setup_dearpygui()
        dpg.show_viewport()

    def _run(self):
        """Run the main event loop."""
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()

    def _cleanup(self):
        """Clean up resources."""
        dpg.destroy_context()

    def start(self):
        """Start the GUI (setup, show, and run)."""
        self._setup()
        self._show()
        self._run()
        self._cleanup()
