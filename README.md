## setup

1. make sure OpenGL and GLFW are installed on your system
2. install the python requirements with `pip install -r requirements.txt`
3. create a `_config.py` file specifying your setup, for example:

```python
camera_size = (1024, 576)
projection_size = (1280, 720)
monitor_name = b"NeoPix"
camera_id = 0
```

4. calibrate your camera/projector with `python calibrate.py`
5. generate and print some markers with (`python generate-markers.py`)
6. run an example program like `python detect-markers.py`
7. have fun!

## standalone applications

| Application | Screenshot |
|-------------|------------|
| paint.py | <img alt="paint.py screenshot" src="https://raw.githubusercontent.com/hinzundcode/cyberdesk/master/screenshots/paint.png" width="300" /> |
| laser-game.py | <img alt="laser-game.py screenshot" src="https://raw.githubusercontent.com/hinzundcode/cyberdesk/master/screenshots/laser-game.jpg" width="300" /> |
| detect-markers.py | <img alt="detect-markers.py screenshot" src="https://raw.githubusercontent.com/hinzundcode/cyberdesk/master/screenshots/detect-markers.jpg" width="300" /> |

## paperspace

<img alt="paperspace screenshot" src="https://raw.githubusercontent.com/hinzundcode/cyberdesk/master/screenshots/paperspace.jpg" width="300" />

The standalone demos like `pain.py` or `laser-game.py` run in fullscreen and take the whole desk. Paperspace takes a different approach. It's an application that can run many different little programs at once.

Each program is represented by a piece of paper that you place on the table. Paperspace starts to execute that program as soon as it is visible and stops it when you take the paper away.

Create and print some papers with `python create-paper.py`, then run the application with `python paperspace.py`. Note that you have to restart the paperspace application if you create new papers while it is running.

### video paper

<img alt="video paper screenshot" src="https://raw.githubusercontent.com/hinzundcode/cyberdesk/master/screenshots/video-paper.jpg" width="300" />

Papers of type video play videos.

Create them with:

```
$ python create-paper.py video --file <videofile>
```

### portals

<img alt="portal papers screenshot" src="https://raw.githubusercontent.com/hinzundcode/cyberdesk/master/screenshots/portal-papers.jpg" width="300" />

Portals take a snapshot of the desk and project them back on the desk. You have to print two papers, one that captures a region of the desk (PortalIn) and one that projects it (PortalOut).

Create them with:

```
$ python create-paper.py portal-in
$ python create-paper.py portal-out --portal-in <portal-in-id>
```
