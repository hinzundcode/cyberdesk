## setup

1. make sure OpenGL and GLFW are installed on your system
2. install the python requirements with `pip install -r requirements.txt`
3. create a `_config.py` file specifying your setup, for example:

```python
camera_size = (1024, 576)
projection_size = (1280, 720)
monitor_name = b"NeoPix"
```

4. calibrate your camera/projector with `python calibrate.py`
5. generate and print some markers with (`python generate-markers.py`)
6. run an example program like `python detect-markers.py`
7. have fun!

## applications

| Application | Screenshot |
|-------------|------------|
| paint.py | <img alt="paint.py screenshot" src="https://raw.githubusercontent.com/hinzundcode/cyberdesk/master/screenshots/paint.png" width="300" /> |
| detect-markers.py | <img alt="detect-markers.py screenshot" src="https://raw.githubusercontent.com/hinzundcode/cyberdesk/master/screenshots/detect-markers.jpg" width="300" /> |
