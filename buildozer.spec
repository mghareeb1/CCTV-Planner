[app]
title = CCTV Planner
package.name = cctvplanner
package.domain = org.itlife
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ico,txt
version = 1.0
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True
android.accept_sdk_license = True
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1