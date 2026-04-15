"""
gui.py

Dear PyGui-based GUI for the Terrain Color Mapper application.
"""

import dearpygui.dearpygui as dpg
import sys
import io
import numpy as np
from PIL import Image
from terrain_color_mapper import TerrainColorMapper, FILAMENTS, LOOKUP


class TerrainColorMapperGUI:
    # Image display configuration: defines which images to display
    IMAGE_DISPLAY_CONFIG = [
        {"attr_name": "proposed_color_image", "label": "Proposed Color"},
        {"attr_name": "height_map_image", "label": "Height Map"},
        {"attr_name": "used_color_image", "label": "Used Color"},
        {"attr_name": "top_layer_image", "label": "Top Layer"},
    ]

    def __init__(self, title="Terrain Color Mapper", width=1000, height=700):
        """Initialize the GUI."""
        self.title = title
        self.width = width
        self.height = height
        self.width_controlPanel = 300
        self.height_consolePanel = 500
        self.console_header_height = 35  # DPG default title-bar height
        self._console_collapsed = False

        # Store Image file path
        self.proposed_color_image = None
        self.height_map_image = None
        self.used_color_image = None
        self.top_layer_image = None
        # Store PIL Image object
        self.proposed_color_image_data = None
        self.height_map_image_data = None
        self.used_color_image_data = None  
        self.top_layer_image_data = None

        self.download_buttons = {}  # Store download button references
        self.texture_tags = {}  # Store texture tags for each image
        self.texture_registry_tag = "texture_registry"

        # Redirect stdout to capture print statements
        self.console_output = io.StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.console_output

        # Create context
        dpg.create_context()
        
        # Create texture registry once at startup
        with dpg.texture_registry(tag=self.texture_registry_tag, show=False):
            pass

    # ------------------------------------------------------------------
    # Panel content builders
    # ------------------------------------------------------------------

    def _create_image_grid(self, parent=None):
        """Create the image grid that holds all display slots."""
        with dpg.group(tag="image_grid", horizontal=False, parent=parent):
            for i in range(0, len(self.IMAGE_DISPLAY_CONFIG), 2):
                with dpg.group(horizontal=True):
                    for j in range(2):
                        if i + j < len(self.IMAGE_DISPLAY_CONFIG):
                            config = self.IMAGE_DISPLAY_CONFIG[i + j]
                            attr_name = config["attr_name"]
                            label = config["label"]
                            image_path = getattr(self, attr_name)
                            image_data = getattr(self, f"{attr_name}_data", None)
                            slot_tag = f"{attr_name}_slot"
                            with dpg.child_window(tag=slot_tag, border=True, autosize_x=False, autosize_y=False, width=300, height=300):
                                if image_path:
                                    texture_tag = f"{attr_name}_texture"
                                    if dpg.does_item_exist(texture_tag):
                                        dpg.delete_item(texture_tag)
                                    try:
                                        # Check if we have image data (PIL Image) or a file path
                                        if image_data is not None:
                                            # Convert PIL Image to numpy array for DearPyGUI
                                            import numpy as np
                                            img_array = np.array(image_data.convert("RGBA"), dtype=np.float32) / 255.0
                                            width, height = image_data.size
                                            buffer = img_array.tobytes()
                                        else:
                                            # Load from file path
                                            width, height, channels, buffer = dpg.load_image(image_path)
                                        dpg.add_raw_texture(
                                            width, height, buffer,
                                            tag=texture_tag,
                                            parent=self.texture_registry_tag,
                                            format=dpg.mvFormat_Float_rgba
                                        )
                                        dpg.add_image(texture_tag, tag=f"{attr_name}_display")
                                        dpg.configure_item(slot_tag, width=max(300, width + 18), height=max(300, height + 40))
                                    except Exception as e:
                                        dpg.add_text(f"Failed to load image: {e}", color=(255, 100, 100), tag=f"{attr_name}_display")
                                else:
                                    dpg.add_text("No image loaded", color=(150, 150, 150), tag=f"{attr_name}_display")
                                dpg.add_text(label, tag=f"{attr_name}_label")

    def _setup_image_panel(self):
        """Set up the image display panel with all configured images in a grid."""
        if dpg.does_item_exist("image_grid"):
            dpg.delete_item("image_grid")
        self._create_image_grid(parent="image_window")
    
    def _create_image_display_slot(self, attr_name, label):
        # Disabled while simplifying image display. The panel now shows a single preview image.
        pass

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
        """Set up the control panel with image upload and download buttons."""
        dpg.add_text("Image Upload")
        dpg.add_separator()
        
        self._create_upload_button(
            "Proposed Color",
            "proposed_color_image",
            "proposed_color_status"
        )
        
        dpg.add_spacing(count=2)
        
        self._create_upload_button(
            "Height Map",
            "height_map_image",
            "height_map_status"
        )
        
        dpg.add_spacing(count=3)
        dpg.add_text("Image Download")
        dpg.add_separator()
        
        self._create_download_button(
            "Used Color",
            "used_color_image"
        )
        
        dpg.add_spacing(count=2)
        
        self._create_download_button(
            "Top Layer",
            "top_layer_image"
        )
        
        # Initialize buttons as disabled
        self._update_download_buttons()
        
        dpg.add_spacing(count=3)
        dpg.add_text("Processing")
        dpg.add_separator()
        
        dpg.add_button(
            label="Process Images",
            width=-1,
            callback=self._on_process_images
        )

    def _create_upload_button(self, image_type, attr_name, status_attr_name):
        """Create an upload button for an image type.
        
        Args:
            image_type: Display name of the image (e.g., "Proposed Color")
            attr_name: Name of the instance attribute to store the file path
            status_attr_name: Name of the instance attribute to store the status widget
        """
        dpg.add_button(
            label=f"Upload {image_type} Image",
            width=-1,
            callback=self._on_upload_file,
            user_data={"attr_name": attr_name, "image_type": image_type}
        )
        status_widget = dpg.add_text("No file selected", color=(200, 200, 200))
        setattr(self, status_attr_name, status_widget)

    def _on_upload_file(self, sender, app_data, user_data):
        """Generic file upload handler."""
        image_type = user_data["image_type"]
        with dpg.file_dialog(
            directory_selector=False,
            show=True,
            callback=self._file_dialog_load_callback,
            user_data=user_data,
            width=700,
            height=400
        ):
            dpg.add_file_extension(".png", custom_text="PNG Images")
            dpg.add_file_extension(".*")

    def _file_dialog_load_callback(self, sender, app_data, user_data):
        """Generic file dialog callback."""
        selected_file = app_data["file_path_name"]
        attr_name = user_data["attr_name"]
        image_type = user_data["image_type"]
        
        if selected_file.lower().endswith('.png'):
            # Store file path in instance attribute
            setattr(self, attr_name, selected_file)

            # Load and store image data
            img  = Image.open(selected_file).convert("RGB")
            setattr(self, f"{attr_name}_data", img)
            
            # Update status widget
            filename = selected_file.split("\\")[-1]
            status_attr_name = f"{attr_name.replace('_image', '')}_status"
            status_widget = getattr(self, status_attr_name)
            dpg.set_value(status_widget, f"✓ {filename}")
            dpg.configure_item(status_widget, color=(100, 200, 100))
            
            print(f"{image_type} image loaded: {selected_file}")
            
            # Update download buttons state
            self._update_download_buttons()
            
            # Refresh image display if the uploaded image is one of the display images
            if attr_name in [config["attr_name"] for config in self.IMAGE_DISPLAY_CONFIG]:
                if dpg.does_item_exist("image_grid"):
                    dpg.delete_item("image_grid")
                self._create_image_grid(parent="image_window")
        else:
            print(f"Error: Invalid file type. Only .png files are accepted.")

    def _create_download_button(self, image_type, attr_name):
        """Create a download button for an image type.
        
        Args:
            image_type: Display name of the image (e.g., "Used Color")
            attr_name: Name of the instance attribute storing the file path
        """
        btn = dpg.add_button(
            label=f"Download {image_type} Image",
            width=-1,
            callback=self._on_download_file,
            user_data={"attr_name": attr_name, "image_type": image_type}
        )
        self.download_buttons[attr_name] = btn

    def _update_download_buttons(self):
        """Enable/disable download buttons based on image availability."""
        for attr_name, btn in self.download_buttons.items():
            # Check if the image data exists (PIL Image object in memory)
            image_data = getattr(self, f"{attr_name}_data", None)
            image_available = image_data is not None
            dpg.configure_item(btn, enabled=image_available)

    def _on_download_file(self, sender, app_data, user_data):
        """Generic file download handler - shows file dialog for saving."""
        attr_name = user_data["attr_name"]
        image_type = user_data["image_type"]
        image_data = getattr(self, f"{attr_name}_data", None)
        
        if image_data is not None:
            with dpg.file_dialog(
                directory_selector=False,
                show=True,
                callback=self._file_dialog_save_callback,
                user_data={"image_data": image_data, "image_type": image_type},
                width=700,
                height=400,
                default_filename=f"{attr_name.replace('_image', '')}.png"
            ):
                dpg.add_file_extension(".png", custom_text="PNG Images")
                dpg.add_file_extension(".*")
        else:
            print(f"Error: No {image_type} image available.")

    def _file_dialog_save_callback(self, sender, app_data, user_data):
        """Callback for file save dialog."""
        file_path = app_data["file_path_name"]
        image_data = user_data["image_data"]
        image_type = user_data["image_type"]
        
        try:
            image_data.save(file_path)
            print(f"Downloaded {image_type} image to: {file_path}")
        except Exception as e:
            print(f"Error saving {image_type} image: {e}")

    def _on_process_images(self, sender, app_data, user_data):
        """Process the proposed color image to generate used color and top layer images."""
        if self.proposed_color_image or self.proposed_color_image_data:
            try:
                mapper = TerrainColorMapper(FILAMENTS, LOOKUP)
                if self.proposed_color_image_data:
                    data = np.array(self.proposed_color_image_data, dtype=np.uint8)
                    mapper.process_image(data=data)
                else:
                    mapper.process_image(input_path=self.proposed_color_image)
                mapper.print_report()
                # Store image data (PIL Image objects) directly without saving
                self.used_color_image_data = mapper.get_used_color_image()
                self.top_layer_image_data = mapper.get_top_layer_image()
                # Mark these as available for download (use a sentinel value)
                self.used_color_image = "<generated>"
                self.top_layer_image = "<generated>"
                self._update_download_buttons()
                # Refresh image display
                if dpg.does_item_exist("image_grid"):
                    dpg.delete_item("image_grid")
                self._create_image_grid(parent="image_window")
                print("Image processing completed successfully.")
            except Exception as e:
                print(f"Error during image processing: {e}")
        else:
            print("Error: No proposed color image selected.")

    def _display_image(self, attr_name):
        # Disabled while simplifying image display. No dynamic per-slot rendering is used.
        return

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
        dpg.create_viewport(title=self.title, width=self.width, height=self.height)
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
