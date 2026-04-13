"""
gui.py

Dear PyGui-based GUI for the Terrain Color Mapper application.
"""

import dearpygui.dearpygui as dpg
import sys
import io


class TerrainColorMapperGUI:
    def __init__(self, title="Terrain Color Mapper", width=1000, height=700):
        """Initialize the GUI."""
        self.title = title
        self.width = width
        self.height = height
        self.width_controlPanel = 300
        self.height_consolePanel = 500
        self.console_header_height = 35  # DPG default title-bar height
        self._console_collapsed = False
        self.proposed_color_image = None
        self.height_map_image = None

        # Redirect stdout to capture print statements
        self.console_output = io.StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.console_output

        # Create context
        dpg.create_context()

        # Create viewport
        dpg.create_viewport(title=self.title, width=self.width, height=self.height)

    # ------------------------------------------------------------------
    # Panel content builders
    # ------------------------------------------------------------------

    def _setup_image_panel(self):
        """Set up the image display panel (placeholder)."""
        dpg.add_text("Image Panel - Placeholder")
        dpg.add_text("Images will be displayed here with subtitles.")

    def _setup_console_panel(self):
        """Set up the console output panel.

        We use a collapsing_header rather than the window's own title-bar
        collapse because dpg.window does NOT support toggled_open_handler —
        it is simply not applicable to window items.  collapsing_header
        does support it and is the correct widget for this pattern.
        """
        with dpg.collapsing_header(
            label="Console Output",
            tag="console_header",
            default_open=True,
        ):
            self.console_text_tag = dpg.add_text("", tag="console_text")

    def _setup_control_panel(self):
        """Set up the control panel with image upload buttons."""
        dpg.add_text("Image Upload")
        dpg.add_separator()
        
        dpg.add_button(
            label="Upload Proposed Color Image",
            width=-1,
            callback=self._on_upload_proposed_color,
            tag="btn_proposed_color"
        )
        self.proposed_color_status = dpg.add_text("No file selected", color=(200, 200, 200))
        
        dpg.add_spacing(count=2)
        
        dpg.add_button(
            label="Upload Height Map Image",
            width=-1,
            callback=self._on_upload_height_map,
            tag="btn_height_map"
        )
        self.height_map_status = dpg.add_text("No file selected", color=(200, 200, 200))

    def _on_upload_proposed_color(self, sender, app_data, user_data):
        """Handle proposed color image upload."""
        with dpg.file_dialog(
            directory_selector=False,
            show=True,
            callback=self._file_dialog_proposed_callback,
            tag="file_dialog_proposed",
            width=700,
            height=400
        ):
            dpg.add_file_extension(".png", custom_text="PNG Images")
            dpg.add_file_extension(".*")

    def _file_dialog_proposed_callback(self, sender, app_data):
        """Callback for proposed color image file dialog."""
        selected_file = app_data["file_path_name"]
        if selected_file.lower().endswith('.png'):
            self.proposed_color_image = selected_file
            filename = selected_file.split("\\")[-1]
            dpg.set_value(self.proposed_color_status, f"✓ {filename}")
            dpg.configure_item(self.proposed_color_status, color=(100, 200, 100))
            print(f"Proposed color image loaded: {selected_file}")
        else:
            print(f"Error: Invalid file type. Only .png files are accepted.")

    def _on_upload_height_map(self, sender, app_data, user_data):
        """Handle height map image upload."""
        with dpg.file_dialog(
            directory_selector=False,
            show=True,
            callback=self._file_dialog_height_callback,
            tag="file_dialog_height",
            width=700,
            height=400
        ):
            dpg.add_file_extension(".png", custom_text="PNG Images")
            dpg.add_file_extension(".*")

    def _file_dialog_height_callback(self, sender, app_data):
        """Callback for height map image file dialog."""
        selected_file = app_data["file_path_name"]
        if selected_file.lower().endswith('.png'):
            self.height_map_image = selected_file
            filename = selected_file.split("\\")[-1]
            dpg.set_value(self.height_map_status, f"✓ {filename}")
            dpg.configure_item(self.height_map_status, color=(100, 200, 100))
            print(f"Height map image loaded: {selected_file}")
        else:
            print(f"Error: Invalid file type. Only .png files are accepted.")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _check_console_collapse(self):
        """Detect collapse state changes on the collapsing_header.

        toggled_open_handler only fires when closing, not opening (DPG bug
        #1280), so we cannot rely on it for both directions.  Instead we
        read dpg.get_value() on the collapsing_header each frame — it
        returns True when open, False when collapsed — and only trigger a
        layout update when the state actually changes.  This keeps the
        layout update event-driven in effect (one recalc per transition)
        while avoiding the broken handler.
        """
        open_now = dpg.get_value("console_header")  # True = expanded
        collapsed_now = not open_now
        if collapsed_now != self._console_collapsed:
            self._console_collapsed = collapsed_now
            self._update_layout()

    def _update_layout(self, *_args):
        """Recompute and apply window geometry.

        Accepts variadic *_args so it can be used directly as a DPG
        callback (which passes sender/app_data/user_data) as well as
        called with no arguments during initialisation.
        """
        width = dpg.get_viewport_client_width()
        height = dpg.get_viewport_client_height()
        left_width = width - self.width_controlPanel

        console_height = (
            self.console_header_height if self._console_collapsed else self.height_consolePanel
        )
        image_height = height - console_height

        dpg.configure_item(
            "image_window",
            width=left_width,
            height=image_height,
            pos=(0, 0),
        )
        dpg.configure_item(
            "console_window",
            width=left_width,
            height=console_height,
            pos=(0, image_height),
        )
        dpg.configure_item(
            "control_window",
            width=self.width_controlPanel,
            height=height,
            pos=(left_width, 0),
        )

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup(self):
        """Set up the main UI elements and event handlers."""
        left_width = self.width - self.width_controlPanel
        image_height = self.height - self.height_consolePanel

        with dpg.window(
            label="Image Panel",
            tag="image_window",
            pos=(0, 0),
            width=left_width,
            height=image_height,
            no_title_bar=True,
            no_close=True,
            no_collapse=True,
            no_move=True,
            no_resize=True,
        ):
            self._setup_image_panel()

        with dpg.window(
            label="Console Output",
            tag="console_window",
            pos=(0, image_height),
            width=left_width,
            height=self.height_consolePanel,
            no_title_bar=True,
            no_close=True,
            no_collapse=True,
            no_move=True,
            no_resize=True,
        ):
            self._setup_console_panel()

        with dpg.window(
            label="Control Panel",
            tag="control_window",
            pos=(left_width, 0),
            width=self.width_controlPanel,
            height=self.height,
            no_title_bar=True,
            no_close=True,
            no_collapse=True,
            no_move=True,
            no_resize=True,
        ):
            self._setup_control_panel()

        # No item handler registry needed — toggled_open_handler is broken
        # for collapsing_header (only fires in one direction, DPG bug #1280).
        # Collapse detection is handled via _check_console_collapse() in _run.

    # ------------------------------------------------------------------
    # Show / run / cleanup
    # ------------------------------------------------------------------

    def _show(self):
        """Display the GUI and register the resize callback."""
        dpg.setup_dearpygui()
        dpg.show_viewport()
        # Viewport resize fires _update_layout event-driven (not per-frame).
        dpg.set_viewport_resize_callback(self._update_layout)
        self._update_layout()

    def _run(self):
        """Run the main event loop.

        Layout updates are now purely event-driven (resize / collapse).
        The loop only renders frames and refreshes the console text.
        """
        while dpg.is_dearpygui_running():
            # Refresh console text from captured stdout
            console_content = self.console_output.getvalue()
            dpg.set_value("console_text", console_content)
            # Detect collapse/expand transitions (toggled_open_handler is
            # broken in DPG — fires in one direction only, bug #1280).
            self._check_console_collapse()
            dpg.render_dearpygui_frame()

    def _cleanup(self):
        """Clean up resources."""
        sys.stdout = self.original_stdout
        dpg.destroy_context()

    def start(self):
        """Start the GUI (setup, show, and run)."""
        self._setup()
        self._show()
        self._run()
        self._cleanup()
