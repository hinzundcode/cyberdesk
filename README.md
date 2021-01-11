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
5. run an example program, for example `python mirror.py`
6. have fun!
