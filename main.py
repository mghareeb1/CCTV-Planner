from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.relativelayout import MDRelativeLayout
from kivymd.uix.slider import MDSlider
from kivymd.uix.selectioncontrol import MDSwitch
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import ScreenManager, SlideTransition
import webbrowser
import os
import sys

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# استيراد ملفات الحسابات (Logic)
try:
    from calculations.calc_bandwidth import calculate_bandwidth_storage
    from calculations.calc_power import calculate_power_ups
    from calculations.calc_cabling import calculate_voltage_drop
    from calculations.calc_optics import calculate_lens_dori
    from calculations.calc_network import calculate_network_details # الملف الأخير
except ImportError as e:
    print(f"Error importing logic: {e}")
    # دوال وهمية
    def calculate_bandwidth_storage(*args): return 0, 0
    def calculate_power_ups(*args): return 0, "N/A", 0, 0
    def calculate_voltage_drop(*args): return 0, 0, "N/A", "Error", "gray"
    def calculate_lens_dori(*args): return 2.8, "N/A", "N/A", 0, "gray"
    def calculate_network_details(*args): return "-", "-", "-", 0, "-", "Error"
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

Window.size = (360, 640)

# --- Base Screen ---
class BaseScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._update_bg, pos=self._update_bg)
        with self.canvas.before:
            bg_path = resource_path(os.path.join("assets", "bg.png"))
            source_img = bg_path if os.path.exists(bg_path) else None 
            Color(1, 1, 1, 1) 
            self.bg_rect = Rectangle(source=source_img, pos=self.pos, size=self.size)
            Color(0, 0, 0, 0.7) 
            self.overlay_rect = Rectangle(pos=self.pos, size=self.size)

    def _update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size
        self.overlay_rect.pos = instance.pos
        self.overlay_rect.size = instance.size

# --- 1. Storage Screen ---
class StorageScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(do_scroll_x=False)
        layout = MDBoxLayout(orientation='vertical', spacing="15dp", padding="20dp", size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        toolbar = MDBoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
        back_btn = MDIconButton(icon="arrow-left", theme_text_color="Custom", text_color="#ffffff", on_release=self.go_back)
        title = MDLabel(text="Storage Calculator", font_style="H6", theme_text_color="Custom", text_color="#ffffff", bold=True, valign="center")
        toolbar.add_widget(back_btn)
        toolbar.add_widget(title)
        
        self.input_cameras = MDTextField(hint_text="Number of Cameras", input_filter="int", mode="rectangle", text_color_normal="#E0E0E0", text_color_focus="#00A8E8", hint_text_color_normal="#AAAAAA")
        self.input_days = MDTextField(hint_text="Recording Days", input_filter="int", mode="rectangle", text_color_normal="#E0E0E0", text_color_focus="#00A8E8", hint_text_color_normal="#AAAAAA")

        res_container = MDRelativeLayout(size_hint_y=None, height="60dp")
        self.field_res = MDTextField(text="2MP (1080p)", hint_text="Resolution", mode="rectangle", readonly=True, text_color_normal="#E0E0E0", text_color_focus="#00A8E8", hint_text_color_normal="#AAAAAA", pos_hint={"center_y": .5})
        btn_overlay_res = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='', pos_hint={"center_x": .5, "center_y": .5})
        btn_overlay_res.bind(on_release=self.open_res_menu)
        res_container.add_widget(self.field_res)
        res_container.add_widget(btn_overlay_res)

        comp_container = MDRelativeLayout(size_hint_y=None, height="60dp")
        self.field_comp = MDTextField(text="H.265", hint_text="Compression", mode="rectangle", readonly=True, text_color_normal="#E0E0E0", text_color_focus="#00A8E8", hint_text_color_normal="#AAAAAA", pos_hint={"center_y": .5})
        btn_overlay_comp = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='', pos_hint={"center_x": .5, "center_y": .5})
        btn_overlay_comp.bind(on_release=self.open_comp_menu)
        comp_container.add_widget(self.field_comp)
        comp_container.add_widget(btn_overlay_comp)

        fps_layout = MDBoxLayout(orientation='vertical', spacing="5dp", size_hint_y=None, height="60dp")
        self.lbl_fps = MDLabel(text="Frame Rate (FPS): 15", theme_text_color="Custom", text_color="#AAAAAA", font_style="Caption")
        self.slider_fps = MDSlider(min=1, max=30, value=15, color="#00A8E8")
        self.slider_fps.bind(value=self.update_fps_label)
        fps_layout.add_widget(self.lbl_fps)
        fps_layout.add_widget(self.slider_fps)

        self.res_items = ["2MP (1080p)", "4MP (2K)", "5MP", "8MP (4K)", "12MP"]
        self.comp_items = ["H.264", "H.265", "H.265+ (Smart)"]
        self.menu_res = MDDropdownMenu(caller=self.field_res, items=[{"text": i, "viewclass": "OneLineListItem", "on_release": lambda x=i: self.set_res(x)} for i in self.res_items], width_mult=4)
        self.menu_comp = MDDropdownMenu(caller=self.field_comp, items=[{"text": i, "viewclass": "OneLineListItem", "on_release": lambda x=i: self.set_comp(x)} for i in self.comp_items], width_mult=4)

        calc_btn = MDRaisedButton(text="CALCULATE STORAGE", md_bg_color="#00A8E8", text_color="#ffffff", size_hint_x=1, elevation=2, padding="15dp", on_release=self.calculate)

        self.result_card = MDCard(orientation='vertical', size_hint_y=None, height="120dp", padding="15dp", radius=[15], md_bg_color=[0.1, 0.1, 0.1, 0.6], elevation=0)
        self.result_storage = MDLabel(text="Storage: 0.00 TB", halign="center", font_style="H5", theme_text_color="Custom", text_color="#4CAF50", bold=True, adaptive_height=True)
        self.result_bandwidth = MDLabel(text="Bandwidth: 0.0 Mbps", halign="center", font_style="Subtitle1", theme_text_color="Custom", text_color="#E0E0E0", adaptive_height=True)
        self.result_card.add_widget(MDLabel(size_hint_y=1))
        self.result_card.add_widget(self.result_storage)
        self.result_card.add_widget(MDLabel(size_hint_y=None, height="10dp"))
        self.result_card.add_widget(self.result_bandwidth)
        self.result_card.add_widget(MDLabel(size_hint_y=1))

        layout.add_widget(toolbar)
        layout.add_widget(self.input_cameras)
        layout.add_widget(self.input_days)
        layout.add_widget(res_container)
        layout.add_widget(comp_container)
        layout.add_widget(fps_layout)
        layout.add_widget(MDLabel(text="", size_hint_y=None, height="10dp"))
        layout.add_widget(calc_btn)
        layout.add_widget(MDLabel(text="", size_hint_y=None, height="20dp"))
        layout.add_widget(self.result_card)
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def update_fps_label(self, instance, value): self.lbl_fps.text = f"Frame Rate (FPS): {int(value)}"
    def open_res_menu(self, instance): self.menu_res.open()
    def open_comp_menu(self, instance): self.menu_comp.open()
    def set_res(self, text): self.field_res.text = text; self.menu_res.dismiss()
    def set_comp(self, text): self.field_comp.text = text; self.menu_comp.dismiss()
    def go_back(self, instance): self.manager.transition = SlideTransition(direction="right"); self.manager.current = "home"
    def calculate(self, instance):
        try:
            cams = int(self.input_cameras.text) if self.input_cameras.text else 0
            days = int(self.input_days.text) if self.input_days.text else 0
            fps = int(self.slider_fps.value)
            res = self.field_res.text
            comp = self.field_comp.text
            bw_mbps, storage_tb = calculate_bandwidth_storage(cams, days, fps, res, comp)
            self.result_storage.text = f"Storage: {storage_tb:.2f} TB"
            self.result_bandwidth.text = f"Bandwidth: {bw_mbps:.1f} Mbps"
            if storage_tb > 20: self.result_storage.text_color = "#FCA311"
            else: self.result_storage.text_color = "#4CAF50"
        except ValueError: self.result_storage.text = "Error"; self.result_storage.text_color = "#FF5252"

# --- 2. Power Screen ---
class PowerScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(do_scroll_x=False)
        layout = MDBoxLayout(orientation='vertical', spacing="15dp", padding="20dp", size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        toolbar = MDBoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
        back_btn = MDIconButton(icon="arrow-left", theme_text_color="Custom", text_color="#ffffff", on_release=self.go_back)
        title = MDLabel(text="Power Center", font_style="H6", theme_text_color="Custom", text_color="#ffffff", bold=True, valign="center")
        toolbar.add_widget(back_btn)
        toolbar.add_widget(title)
        
        self.input_cameras = MDTextField(hint_text="Number of Cameras", input_filter="int", mode="rectangle", text_color_normal="#E0E0E0", text_color_focus="#FFC107", hint_text_color_normal="#AAAAAA")
        
        type_container = MDRelativeLayout(size_hint_y=None, height="60dp")
        self.field_type = MDTextField(text="Fixed Bullet/Dome", hint_text="Camera Type", mode="rectangle", readonly=True, text_color_normal="#E0E0E0", text_color_focus="#FFC107", hint_text_color_normal="#AAAAAA", pos_hint={"center_y": .5})
        btn_overlay_type = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='', pos_hint={"center_x": .5, "center_y": .5})
        btn_overlay_type.bind(on_release=self.open_type_menu)
        type_container.add_widget(self.field_type)
        type_container.add_widget(btn_overlay_type)

        backup_container = MDRelativeLayout(size_hint_y=None, height="60dp")
        self.field_backup = MDTextField(text="15 Minutes", hint_text="Desired Backup Time", mode="rectangle", readonly=True, text_color_normal="#E0E0E0", text_color_focus="#FFC107", hint_text_color_normal="#AAAAAA", pos_hint={"center_y": .5})
        btn_overlay_backup = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='', pos_hint={"center_x": .5, "center_y": .5})
        btn_overlay_backup.bind(on_release=self.open_backup_menu)
        backup_container.add_widget(self.field_backup)
        backup_container.add_widget(btn_overlay_backup)

        switch_layout = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="50dp", spacing="10dp", padding=[5,0])
        lbl_switch = MDLabel(text="Warm Light Mode (+3W)", theme_text_color="Custom", text_color="#E0E0E0", font_style="Subtitle1")
        self.switch_night = MDSwitch(active=False, widget_style="ios", thumb_color_active="#FFC107", track_color_active="#5D4037")
        switch_layout.add_widget(lbl_switch)
        switch_layout.add_widget(self.switch_night)

        self.type_items = ["Fixed Bullet/Dome (Standard)", "Motorized Varifocal", "PTZ (High PoE)"]
        self.backup_items = ["15 Minutes", "30 Minutes", "1 Hour", "2 Hours", "4 Hours"]
        self.menu_type = MDDropdownMenu(caller=self.field_type, items=[{"text": i, "viewclass": "OneLineListItem", "on_release": lambda x=i: self.set_type(x)} for i in self.type_items], width_mult=5)
        self.menu_backup = MDDropdownMenu(caller=self.field_backup, items=[{"text": i, "viewclass": "OneLineListItem", "on_release": lambda x=i: self.set_backup(x)} for i in self.backup_items], width_mult=4)

        calc_btn = MDRaisedButton(text="CALCULATE POWER", md_bg_color="#FFC107", text_color="#000000", size_hint_x=1, elevation=2, padding="15dp", on_release=self.calculate)

        self.result_card = MDCard(orientation='vertical', size_hint_y=None, height="180dp", padding="15dp", radius=[15], md_bg_color=[0.1, 0.1, 0.1, 0.6], elevation=0)
        self.res_watts = MDLabel(text="PoE Load: 0 W", halign="center", font_style="H5", theme_text_color="Custom", text_color="#FFC107", bold=True, adaptive_height=True)
        self.res_switch = MDLabel(text="Switch: N/A", halign="center", font_style="Caption", theme_text_color="Custom", text_color="#E0E0E0", adaptive_height=True)
        self.res_ups = MDLabel(text="UPS: 0 VA", halign="center", font_style="Subtitle1", theme_text_color="Custom", text_color="#E0E0E0", adaptive_height=True)
        self.res_battery = MDLabel(text="Battery: 0 Ah (12V)", halign="center", font_style="Subtitle1", theme_text_color="Custom", text_color="#E0E0E0", adaptive_height=True)
        self.result_card.add_widget(MDLabel(size_hint_y=1))
        self.result_card.add_widget(self.res_watts)
        self.result_card.add_widget(self.res_switch)
        self.result_card.add_widget(MDLabel(size_hint_y=None, height="15dp"))
        self.result_card.add_widget(self.res_ups)
        self.result_card.add_widget(MDLabel(size_hint_y=None, height="5dp"))
        self.result_card.add_widget(self.res_battery)
        self.result_card.add_widget(MDLabel(size_hint_y=1))

        layout.add_widget(toolbar)
        layout.add_widget(self.input_cameras)
        layout.add_widget(type_container)
        layout.add_widget(switch_layout)
        layout.add_widget(backup_container)
        layout.add_widget(MDLabel(text="", size_hint_y=None, height="10dp"))
        layout.add_widget(calc_btn)
        layout.add_widget(MDLabel(text="", size_hint_y=None, height="20dp"))
        layout.add_widget(self.result_card)
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def open_type_menu(self, instance): self.menu_type.open()
    def open_backup_menu(self, instance): self.menu_backup.open()
    def set_type(self, text): self.field_type.text = text; self.menu_type.dismiss()
    def set_backup(self, text): self.field_backup.text = text; self.menu_backup.dismiss()
    def go_back(self, instance): self.manager.transition = SlideTransition(direction="right"); self.manager.current = "home"
    def calculate(self, instance):
        try:
            cams = int(self.input_cameras.text) if self.input_cameras.text else 0
            cam_type = self.field_type.text
            backup_time = self.field_backup.text
            night_mode = self.switch_night.active
            watts, switch_sugg, ups, battery = calculate_power_ups(cams, cam_type, night_mode, backup_time)
            self.res_watts.text = f"PoE Load: {int(watts)} Watts"
            self.res_switch.text = f"Suggested: {switch_sugg}"
            self.res_ups.text = f"Req. UPS: {int(ups)} VA"
            self.res_battery.text = f"Battery: {int(battery)} Ah (12V)"
        except ValueError: self.res_watts.text = "Error"

# --- 3. Cabling Screen ---
class CablingScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(do_scroll_x=False)
        layout = MDBoxLayout(orientation='vertical', spacing="15dp", padding="20dp", size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        toolbar = MDBoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
        back_btn = MDIconButton(icon="arrow-left", theme_text_color="Custom", text_color="#ffffff", on_release=self.go_back)
        title = MDLabel(text="Cable Check", font_style="H6", theme_text_color="Custom", text_color="#ffffff", bold=True, valign="center")
        toolbar.add_widget(back_btn)
        toolbar.add_widget(title)
        
        # 1. Cable Cat Dropdown
        cat_container = MDRelativeLayout(size_hint_y=None, height="60dp")
        self.field_cat = MDTextField(text="Cat6 (23 AWG)", hint_text="Cable Category", mode="rectangle", readonly=True, text_color_normal="#E0E0E0", text_color_focus="#4CAF50", hint_text_color_normal="#AAAAAA", pos_hint={"center_y": .5})
        btn_overlay_cat = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='', pos_hint={"center_x": .5, "center_y": .5})
        btn_overlay_cat.bind(on_release=self.open_cat_menu)
        cat_container.add_widget(self.field_cat)
        cat_container.add_widget(btn_overlay_cat)

        # 2. Material Dropdown
        mat_container = MDRelativeLayout(size_hint_y=None, height="60dp")
        self.field_mat = MDTextField(text="Pure Copper", hint_text="Conductor Material", mode="rectangle", readonly=True, text_color_normal="#E0E0E0", text_color_focus="#4CAF50", hint_text_color_normal="#AAAAAA", pos_hint={"center_y": .5})
        btn_overlay_mat = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='', pos_hint={"center_x": .5, "center_y": .5})
        btn_overlay_mat.bind(on_release=self.open_mat_menu)
        mat_container.add_widget(self.field_mat)
        mat_container.add_widget(btn_overlay_mat)

        # 3. Length Input
        self.input_len = MDTextField(hint_text="Cable Length (Meters)", input_filter="int", mode="rectangle", text_color_normal="#E0E0E0", text_color_focus="#4CAF50", hint_text_color_normal="#AAAAAA")

        # 4. Load Dropdown
        load_container = MDRelativeLayout(size_hint_y=None, height="60dp")
        self.field_load = MDTextField(text="7W (Fixed Camera)", hint_text="Camera Power", mode="rectangle", readonly=True, text_color_normal="#E0E0E0", text_color_focus="#4CAF50", hint_text_color_normal="#AAAAAA", pos_hint={"center_y": .5})
        btn_overlay_load = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='', pos_hint={"center_x": .5, "center_y": .5})
        btn_overlay_load.bind(on_release=self.open_load_menu)
        load_container.add_widget(self.field_load)
        load_container.add_widget(btn_overlay_load)

        self.cat_items = ["Cat5e (24 AWG)", "Cat6 (23 AWG)"]
        self.mat_items = ["Pure Copper (Standard)", "CCA (Copper Clad Aluminum)"]
        self.load_items = ["7W (Fixed Camera)", "12W (Motorized)", "25W (PTZ)", "4W (Eco)"]

        self.menu_cat = MDDropdownMenu(caller=self.field_cat, items=[{"text": i, "viewclass": "OneLineListItem", "on_release": lambda x=i: self.set_cat(x)} for i in self.cat_items], width_mult=4)
        self.menu_mat = MDDropdownMenu(caller=self.field_mat, items=[{"text": i, "viewclass": "OneLineListItem", "on_release": lambda x=i: self.set_mat(x)} for i in self.mat_items], width_mult=4)
        self.menu_load = MDDropdownMenu(caller=self.field_load, items=[{"text": i, "viewclass": "OneLineListItem", "on_release": lambda x=i: self.set_load(x)} for i in self.load_items], width_mult=4)

        calc_btn = MDRaisedButton(text="CHECK VOLTAGE", md_bg_color="#4CAF50", text_color="#ffffff", size_hint_x=1, elevation=2, padding="15dp", on_release=self.calculate)

        self.result_card = MDCard(orientation='vertical', size_hint_y=None, height="160dp", padding="15dp", radius=[15], md_bg_color=[0.1, 0.1, 0.1, 0.6], elevation=0)
        self.res_voltage = MDLabel(text="Voltage: 0.0 V", halign="center", font_style="H5", theme_text_color="Custom", text_color="#4CAF50", bold=True, adaptive_height=True)
        self.res_status = MDLabel(text="Status: UNKNOWN", halign="center", font_style="H6", theme_text_color="Custom", text_color="#9E9E9E", adaptive_height=True)
        self.res_msg = MDLabel(text="Ready to calculate", halign="center", font_style="Caption", theme_text_color="Custom", text_color="#E0E0E0", adaptive_height=True)
        
        self.result_card.add_widget(MDLabel(size_hint_y=1))
        self.result_card.add_widget(self.res_voltage)
        self.result_card.add_widget(MDLabel(size_hint_y=None, height="10dp"))
        self.result_card.add_widget(self.res_status)
        self.result_card.add_widget(self.res_msg)
        self.result_card.add_widget(MDLabel(size_hint_y=1))

        layout.add_widget(toolbar)
        layout.add_widget(cat_container)
        layout.add_widget(mat_container)
        layout.add_widget(self.input_len)
        layout.add_widget(load_container)
        layout.add_widget(MDLabel(text="", size_hint_y=None, height="20dp"))
        layout.add_widget(calc_btn)
        layout.add_widget(MDLabel(text="", size_hint_y=None, height="20dp"))
        layout.add_widget(self.result_card)
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def open_cat_menu(self, instance): self.menu_cat.open()
    def open_mat_menu(self, instance): self.menu_mat.open()
    def open_load_menu(self, instance): self.menu_load.open()
    def set_cat(self, text): self.field_cat.text = text; self.menu_cat.dismiss()
    def set_mat(self, text): self.field_mat.text = text; self.menu_mat.dismiss()
    def set_load(self, text): self.field_load.text = text; self.menu_load.dismiss()
    def go_back(self, instance): self.manager.transition = SlideTransition(direction="right"); self.manager.current = "home"

    def calculate(self, instance):
        try:
            length = float(self.input_len.text) if self.input_len.text else 0
            cat = self.field_cat.text
            mat = self.field_mat.text
            load = self.field_load.text
            final_v, drop_v, status, msg, color = calculate_voltage_drop(length, cat, mat, load)
            self.res_voltage.text = f"Voltage: {final_v:.1f} V"
            self.res_status.text = f"Status: {status}"
            self.res_msg.text = msg
            self.res_voltage.text_color = color
            self.res_status.text_color = color
        except ValueError: self.res_status.text = "Error"

# --- 4. Lens Screen ---
class LensScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(do_scroll_x=False)
        layout = MDBoxLayout(orientation='vertical', spacing="15dp", padding="20dp", size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        toolbar = MDBoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
        back_btn = MDIconButton(icon="arrow-left", theme_text_color="Custom", text_color="#ffffff", on_release=self.go_back)
        title = MDLabel(text="Lens Select", font_style="H6", theme_text_color="Custom", text_color="#ffffff", bold=True, valign="center")
        toolbar.add_widget(back_btn)
        toolbar.add_widget(title)
        
        scene_container = MDRelativeLayout(size_hint_y=None, height="60dp")
        self.field_scene = MDTextField(text="Indoor Room", hint_text="Scene Type", mode="rectangle", readonly=True, text_color_normal="#E0E0E0", text_color_focus="#00BCD4", hint_text_color_normal="#AAAAAA", pos_hint={"center_y": .5})
        btn_overlay_scene = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='', pos_hint={"center_x": .5, "center_y": .5})
        btn_overlay_scene.bind(on_release=self.open_scene_menu)
        scene_container.add_widget(self.field_scene)
        scene_container.add_widget(btn_overlay_scene)

        self.input_dist = MDTextField(hint_text="Target Distance (Meters)", input_filter="float", mode="rectangle", text_color_normal="#E0E0E0", text_color_focus="#00BCD4", hint_text_color_normal="#AAAAAA")
        self.input_width = MDTextField(hint_text="Target Width (Meters)", input_filter="float", mode="rectangle", text_color_normal="#E0E0E0", text_color_focus="#00BCD4", hint_text_color_normal="#AAAAAA")

        res_container = MDRelativeLayout(size_hint_y=None, height="60dp")
        self.field_res = MDTextField(text="2MP (1080p)", hint_text="Camera Resolution", mode="rectangle", readonly=True, text_color_normal="#E0E0E0", text_color_focus="#00BCD4", hint_text_color_normal="#AAAAAA", pos_hint={"center_y": .5})
        btn_overlay_res = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='', pos_hint={"center_x": .5, "center_y": .5})
        btn_overlay_res.bind(on_release=self.open_res_menu)
        res_container.add_widget(self.field_res)
        res_container.add_widget(btn_overlay_res)

        self.scene_items = ["Indoor Room", "Outdoor Parking", "Perimeter Fence"]
        self.res_items = ["2MP (1080p)", "4MP (2K)", "5MP", "8MP (4K)", "12MP"]

        self.menu_scene = MDDropdownMenu(caller=self.field_scene, items=[{"text": i, "viewclass": "OneLineListItem", "on_release": lambda x=i: self.set_scene(x)} for i in self.scene_items], width_mult=4)
        self.menu_res = MDDropdownMenu(caller=self.field_res, items=[{"text": i, "viewclass": "OneLineListItem", "on_release": lambda x=i: self.set_res(x)} for i in self.res_items], width_mult=4)

        calc_btn = MDRaisedButton(text="SUGGEST LENS", md_bg_color="#00BCD4", text_color="#ffffff", size_hint_x=1, elevation=2, padding="15dp", on_release=self.calculate)

        self.result_card = MDCard(orientation='vertical', size_hint_y=None, height="160dp", padding="15dp", radius=[15], md_bg_color=[0.1, 0.1, 0.1, 0.6], elevation=0)
        self.res_lens = MDLabel(text="Lens: ---", halign="center", font_style="H5", theme_text_color="Custom", text_color="#00BCD4", bold=True, adaptive_height=True)
        self.res_reason = MDLabel(text="Select Scene", halign="center", font_style="Caption", theme_text_color="Custom", text_color="#E0E0E0", adaptive_height=True)
        self.res_quality = MDLabel(text="Quality: ---", halign="center", font_style="H6", theme_text_color="Custom", text_color="#9E9E9E", adaptive_height=True)
        self.res_ppm = MDLabel(text="PPM: 0", halign="center", font_style="Caption", theme_text_color="Custom", text_color="#E0E0E0", adaptive_height=True)
        self.result_card.add_widget(MDLabel(size_hint_y=1))
        self.result_card.add_widget(self.res_lens)
        self.result_card.add_widget(self.res_reason)
        self.result_card.add_widget(MDLabel(size_hint_y=None, height="15dp"))
        self.result_card.add_widget(self.res_quality)
        self.result_card.add_widget(self.res_ppm)
        self.result_card.add_widget(MDLabel(size_hint_y=1))

        layout.add_widget(toolbar)
        layout.add_widget(scene_container)
        layout.add_widget(self.input_dist)
        layout.add_widget(self.input_width)
        layout.add_widget(res_container)
        layout.add_widget(MDLabel(text="", size_hint_y=None, height="10dp"))
        layout.add_widget(calc_btn)
        layout.add_widget(MDLabel(text="", size_hint_y=None, height="20dp"))
        layout.add_widget(self.result_card)
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def open_scene_menu(self, instance): self.menu_scene.open()
    def open_res_menu(self, instance): self.menu_res.open()
    def set_scene(self, text): self.field_scene.text = text; self.menu_scene.dismiss()
    def set_res(self, text): self.field_res.text = text; self.menu_res.dismiss()
    def go_back(self, instance): self.manager.transition = SlideTransition(direction="right"); self.manager.current = "home"
    def calculate(self, instance):
        try:
            dist = float(self.input_dist.text) if self.input_dist.text else 0
            width = float(self.input_width.text) if self.input_width.text else 0
            scene = self.field_scene.text
            res = self.field_res.text
            lens, reason, quality, ppm, color = calculate_lens_dori(dist, width, scene, res)
            self.res_lens.text = f"Lens: {lens} mm"
            self.res_reason.text = reason
            self.res_quality.text = quality
            self.res_ppm.text = f"{int(ppm)} PPM"
            self.res_quality.text_color = color
        except ValueError: self.res_lens.text = "Error"

# --- 5. IP Calculator Screen (الجديدة) ---
class IPScreen(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(do_scroll_x=False)
        layout = MDBoxLayout(orientation='vertical', spacing="15dp", padding="20dp", size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        
        toolbar = MDBoxLayout(size_hint_y=None, height="50dp", spacing="10dp")
        back_btn = MDIconButton(icon="arrow-left", theme_text_color="Custom", text_color="#ffffff", on_release=self.go_back)
        title = MDLabel(text="IP Calculator", font_style="H6", theme_text_color="Custom", text_color="#ffffff", bold=True, valign="center")
        toolbar.add_widget(back_btn)
        toolbar.add_widget(title)
        
        # 1. IP Input
        self.input_ip = MDTextField(text="192.168.1.1", hint_text="IP Address", mode="rectangle", text_color_normal="#E0E0E0", text_color_focus="#9C27B0", hint_text_color_normal="#AAAAAA")
        
        # 2. CIDR Select
        cidr_container = MDRelativeLayout(size_hint_y=None, height="60dp")
        self.field_cidr = MDTextField(text="/24 (254 Hosts)", hint_text="Subnet Mask", mode="rectangle", readonly=True, text_color_normal="#E0E0E0", text_color_focus="#9C27B0", hint_text_color_normal="#AAAAAA", pos_hint={"center_y": .5})
        btn_overlay_cidr = Button(size_hint=(1, 1), background_color=(0, 0, 0, 0), background_normal='', pos_hint={"center_x": .5, "center_y": .5})
        btn_overlay_cidr.bind(on_release=self.open_cidr_menu)
        cidr_container.add_widget(self.field_cidr)
        cidr_container.add_widget(btn_overlay_cidr)

        self.cidr_items = ["/24 (254 Hosts) - Standard", "/23 (510 Hosts) - Medium", "/22 (1022 Hosts) - Large", "/21 (2046 Hosts)", "/16 (65k Hosts) - Huge", "/30 (2 Hosts) - P2P Link"]
        self.menu_cidr = MDDropdownMenu(caller=self.field_cidr, items=[{"text": i, "viewclass": "OneLineListItem", "on_release": lambda x=i: self.set_cidr(x)} for i in self.cidr_items], width_mult=5)

        calc_btn = MDRaisedButton(text="CALCULATE NETWORK", md_bg_color="#9C27B0", text_color="#ffffff", size_hint_x=1, elevation=2, padding="15dp", on_release=self.calculate)

        # Result Card (Big one for details)
        self.result_card = MDCard(orientation='vertical', size_hint_y=None, height="240dp", padding="15dp", radius=[15], md_bg_color=[0.1, 0.1, 0.1, 0.6], elevation=0)
        
        self.res_netid = MDLabel(text="Network ID: ---", halign="center", font_style="Subtitle1", theme_text_color="Custom", text_color="#E0E0E0", adaptive_height=True)
        self.res_mask = MDLabel(text="Netmask: ---", halign="center", font_style="Subtitle2", theme_text_color="Custom", text_color="#AAAAAA", adaptive_height=True)
        self.res_bcast = MDLabel(text="Broadcast: ---", halign="center", font_style="Subtitle2", theme_text_color="Custom", text_color="#AAAAAA", adaptive_height=True)
        
        # Divider
        self.result_card.add_widget(MDLabel(size_hint_y=1))
        self.result_card.add_widget(self.res_netid)
        self.result_card.add_widget(MDLabel(size_hint_y=None, height="5dp"))
        self.result_card.add_widget(self.res_mask)
        self.result_card.add_widget(MDLabel(size_hint_y=None, height="5dp"))
        self.result_card.add_widget(self.res_bcast)
        self.result_card.add_widget(MDLabel(size_hint_y=1))
        
        # Usable Hosts Section
        self.res_hosts = MDLabel(text="Usable Hosts: 0", halign="center", font_style="H5", theme_text_color="Custom", text_color="#2EC4B6", bold=True, adaptive_height=True)
        self.res_range = MDLabel(text="Range: ---", halign="center", font_style="Caption", theme_text_color="Custom", text_color="#E0E0E0", adaptive_height=True)
        
        self.result_card.add_widget(MDLabel(size_hint_y=None, height="10dp")) # Space
        self.result_card.add_widget(self.res_hosts)
        self.result_card.add_widget(MDLabel(size_hint_y=None, height="5dp"))
        self.result_card.add_widget(self.res_range)
        self.result_card.add_widget(MDLabel(size_hint_y=1))

        layout.add_widget(toolbar)
        layout.add_widget(self.input_ip)
        layout.add_widget(cidr_container)
        layout.add_widget(MDLabel(text="", size_hint_y=None, height="10dp"))
        layout.add_widget(calc_btn)
        layout.add_widget(MDLabel(text="", size_hint_y=None, height="20dp"))
        layout.add_widget(self.result_card)
        scroll.add_widget(layout)
        self.add_widget(scroll)

    def open_cidr_menu(self, instance): self.menu_cidr.open()
    def set_cidr(self, text): self.field_cidr.text = text; self.menu_cidr.dismiss()
    def go_back(self, instance): self.manager.transition = SlideTransition(direction="right"); self.manager.current = "home"

    def calculate(self, instance):
        ip = self.input_ip.text
        cidr = self.field_cidr.text
        
        net_id, mask, bcast, hosts, ip_range, status = calculate_network_details(ip, cidr)
        
        if status == "Success":
            self.res_netid.text = f"Network ID: {net_id}"
            self.res_mask.text = f"Mask: {mask}"
            self.res_bcast.text = f"Broadcast: {bcast}"
            self.res_hosts.text = f"Usable Hosts: {hosts}"
            self.res_range.text = f"Range: {ip_range}"
            self.res_hosts.text_color = "#2EC4B6"
        else:
            self.res_hosts.text = status # Error msg
            self.res_hosts.text_color = "#FF5252"

# --- Dashboard Card ---
class DashboardCard(MDCard):
    def __init__(self, title, icon, color_hex, screen_name, **kwargs):
        super().__init__(**kwargs)
        self.screen_name = screen_name
        self.padding = "15dp"
        self.size_hint = (None, None)
        self.size = ("155dp", "130dp")
        self.radius = [20]
        self.ripple_behavior = True
        self.md_bg_color = [0.15, 0.15, 0.15, 0.8] 
        self.elevation = 4
        self.on_release = self.open_screen
        
        layout = MDBoxLayout(orientation='vertical', spacing="10dp", pos_hint={"center_y": .5})
        icon_btn = MDIconButton(icon=icon, icon_size="50sp", theme_text_color="Custom", text_color=color_hex, pos_hint={"center_x": .5})
        lbl_title = MDLabel(text=title, halign="center", theme_text_color="Custom", text_color="#E0E0E0", font_style="Subtitle2", bold=True)
        layout.add_widget(icon_btn)
        layout.add_widget(lbl_title)
        self.add_widget(layout)

    def open_screen(self):
        app = MDApp.get_running_app()
        if self.screen_name:
            app.root.transition = SlideTransition(direction="left")
            app.root.current = self.screen_name

# --- Home Screen ---
class HomeScreen(BaseScreen):
    def open_linkedin(self, instance): webbrowser.open("https://www.linkedin.com/in/mohammed-ghareeb")
    def open_facebook(self, instance): webbrowser.open("https://www.facebook.com")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        scroll = ScrollView(do_scroll_x=False)
        main_layout = MDBoxLayout(orientation='vertical', spacing="25dp", padding="20dp", size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))

        header = MDBoxLayout(orientation='vertical', size_hint_y=None, height="160dp", spacing="10dp", padding="10dp")
        logo_source = resource_path(os.path.join("assets", "logo.png"))
        if not os.path.exists(logo_source): logo_source = resource_path(os.path.join("assets", "app_icon.ico"))
        logo = Image(source=logo_source, size_hint=(None, None), size=("90dp", "90dp"), pos_hint={"center_x": .5})
        app_name = MDLabel(text="CCTV PLANNER", halign="center", font_style="H5", bold=True, theme_text_color="Custom", text_color="#00A8E8")
        header.add_widget(logo)
        header.add_widget(app_name)

        grid = MDGridLayout(cols=2, spacing="15dp", size_hint_y=None, adaptive_height=True, padding=[5, 0, 5, 0])
        grid.add_widget(DashboardCard("Storage Calc", "harddisk", "#03A9F4", screen_name="storage"))
        grid.add_widget(DashboardCard("Power Center", "flash", "#FFC107", screen_name="power"))
        grid.add_widget(DashboardCard("Lens Select", "camera-iris", "#00BCD4", screen_name="lens"))
        grid.add_widget(DashboardCard("Cable Check", "cable-data", "#4CAF50", screen_name="cabling"))
        grid.add_widget(DashboardCard("IP Calculator", "calculator", "#9C27B0", screen_name="ip")) # Linked!
        
        footer_layout = MDBoxLayout(orientation='vertical', size_hint_y=None, height="100dp", spacing="15dp")
        dev_label = MDLabel(text="Developed by\nMohammed Ghareeb", halign="center", font_style="Caption", theme_text_color="Hint")
        icons_box = MDBoxLayout(orientation='horizontal', spacing="30dp", adaptive_width=True, pos_hint={"center_x": .5})
        btn_li = MDIconButton(icon="linkedin", icon_size="35sp", theme_text_color="Custom", text_color="#0077B5", on_release=self.open_linkedin)
        btn_fb = MDIconButton(icon="facebook", icon_size="35sp", theme_text_color="Custom", text_color="#1877F2", on_release=self.open_facebook)
        icons_box.add_widget(btn_li)
        icons_box.add_widget(btn_fb)
        footer_layout.add_widget(dev_label)
        footer_layout.add_widget(icons_box)

        main_layout.add_widget(header)
        main_layout.add_widget(grid)
        main_layout.add_widget(footer_layout)
        scroll.add_widget(main_layout)
        self.add_widget(scroll)

# --- App Class ---
class CCTVPlannerApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "LightBlue"
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(StorageScreen(name="storage"))
        sm.add_widget(PowerScreen(name="power"))
        sm.add_widget(CablingScreen(name="cabling"))
        sm.add_widget(LensScreen(name="lens"))
        sm.add_widget(IPScreen(name="ip")) # Final Screen
        return sm

if __name__ == "__main__":
    CCTVPlannerApp().run()