This is a simple general purpose display server - it takes values from
mqtt and publishes the resulting image to mqtt.

Based on the received values a black/white image is generated. The image
can be generated from the following elements: \* ``Bar`` - subscribes to
a topic and draws a solid bar. \* ``SequentialChart`` - subscribes to a
topic, groups them by time window and draws a simple chart. \*
``DigitalClock`` - writes the current time. \* ``MQTTText`` - subscribes
to a topic and writes the value using the provided format string. \*
``StaticText`` - writes the provided text. Each element can be used
multiple times.

``Nikippe`` is part of the collection of mqtt based microservices
`pelops <https://gitlab.com/pelops>`__. An overview on the microservice
architecture and an example setup can be found at
(http://gitlab.com/pelops/pelops).

The name
`Nikippe <https://de.wikipedia.org/wiki/Nikippe_(Tochter_des_Pelops)>`__
(Νiκίππη) is taken from the children of Pelops.

For Users
=========

Installation
------------

Prerequisites for the core functionality are:

::

    sudo apt install python3 python3-pip python-pil
    sudo pip3 install pelops

Install via pip:

::

    sudo pip3 install nikippe

To update to the latest version add ``--upgrade`` as suffix to the
``pip3`` line above.

Install via gitlab (might need additional packages):

::

    git clone git@gitlab.com:pelops/nikippe.git
    cd nikippe
    sudo python3 setup.py install

This will install the following shell script: \* ``nikippe`` - the
display server as a registered shell script.

The script cli arguments are: \* '-c'/'--config' - config file
(mandatory) \* '-v' - verbose output (optional) \* '--version' - show
the version number and exit

YAML-Config Example
-------------------

A yaml file must contain two root blocks: \* mqtt - mqtt-address,
mqtt-port, and path to credentials file mqtt-credentials (a file
consisting of two entries: mqtt-user, mqtt-password) \* display-server -
topics that nikippe should publish the resulting image to and the update
behavior. \* renderer - configuration for the render engine and the
elements that should be displayed.

| Each element must have at least the following parameters: \*
  ``name: humidity-chart`` - free choose able name - not used internally
  \* ``type: chart`` - element type. must be [chart, bar, digitalclock,
  mqtttext, statictext] \* ``x: 30`` - position in rendered image
  (top/left) \* ``y: 5`` - position in rendered image (top/left) \*
  ``width: 256`` - size of the element \* ``height: 60`` - size of the
  element \* ``foreground-color: 0`` - either 0 (black) or 255 (white).
  \* ``background-color: 255`` - either 0 (black) or 255 (white).
| \* ``active: True`` - if set to false, this entry will be ignored.

config.yaml
~~~~~~~~~~~

The config file consists of three root nodes: mqtt, display-driver, and
renderer. #### mqtt

::

    mqtt:
        mqtt-address: localhost
        mqtt-port: 1883
        mqtt-credentials: ~/credentials.yaml

display-server
^^^^^^^^^^^^^^

::

    display-server:
        epaper_full_image: /test/full_image
        epaper_full_image_twice: /test/full_image_twice
        send-on-change: True  # send new image to epaper if any element reports that it received an update
        send-interval: 60  # seconds. if 0 interval is disabled.

The first two entries are the topics the epaper device driver (see
`copreus <https://gitlab.com/pelops/copreus>`__) listens to.
``send-on-change`` and ``send-interval`` define the update behavior.

Renderer
^^^^^^^^

::

    renderer:
        width: 296
        height: 128
        background: ../resources/gui_background.png  # optional
        background-color: 255  # either 0 (black) or 255 (white).
        elements:

SequentialChart
'''''''''''''''

::

          - name: humidity-chart  
            type: chart  
            x: 30  
            y: 5  
            width: 256 
            height: 60  
            foreground-color: 0 
            background-color: 255   
            active: True
            group-by: 300  # in seconds. 0==no grouping
            aggregator: avg  # aggregator for group-by. valid values: avg, min, max, median. can be omitted if group-by=0.
            connect-values: True  # if true - values are connected with lines, other wise they are independent dots
            pixel-per-value: 2  # a new value/dot is drawn every n-th pixel on the x-axis. must be > 0.       
            topic-sub: /test/humidity  # input value
            border-top: False  # if true, a single line in foreground-color will be drawn as border
            border-bottom: True  # if true, a single line in foreground-color will be drawn as border
            border-left: True  # if true, a single line in foreground-color will be drawn as border
            border-right: False  # if true, a single line in foreground-color will be drawn as border

The first six entries are the same for all elements. ##### Bar

::

          - name: current-humidity
            type: bar
            x: 5
            y: 5
            width: 20
            height: 60
            foreground-color: 0 
            background-color: 255 
            active: True
            border: True  # if true, the whole bar will be surrounded by a single line in foreground-color.
            orientation: up  # up, down, left, right
            topic-sub: /test/humidity  # input value
            min-value: 5  # displayed bar % = (max(max-value, input) - min-value) / (max-value - min-value)
            max-value: 23  #

DigitalClock
''''''''''''

::

          - name: digital-clock
            type: digitalclock
            x: 0  
            y: 10 
            width: 242
            height: 77
            foreground-color: 0 
            background-color: 255  
            active: False
            font: /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
            size: 20  # font-size

MQTTText
''''''''

::

          - name: humidity-value
            type: mqtttext
            x: 5  
            y: 70 
            width: 70
            height: 25
            foreground-color: 0 
            background-color: 255
            active: True
            font: /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
            size: 20  # font-size
            string: "{0:.1f}%"  # format string
            topic-sub: /test/humidity  # input value

StaticText
''''''''''

::

          - name: design
            type: statictext
            x: 124  
            y: 103  
            width: 76
            height: 10
            foreground-color: 0  
            background-color: 255
            active: True        
            font: /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
            size: 8  # font-size
            string: "design by tgd1975"  # text to be displayed     

credentials.yaml
~~~~~~~~~~~~~~~~

::

    mqtt:
        mqtt-user: user
        mqtt-password: password

run Nikippe
-----------

using ``screen``
~~~~~~~~~~~~~~~~

``screen -d -m -S nikippe bash -c 'nikippe -c config_nikippe.yaml'`` ###
using ``systemd`` - add systemd example.

For Developers
==============

Getting Started
---------------

Nikippe consists of three elements: ``DisplayServer``, ``Renderer`` and
the render elements. The ``DisplayServer`` instantiates the render
engine and sends the publishes the updated image. This is done either
with a time interval and/or upon reception of new values. The
``Renderer`` is controlling the render elements and integrates them into
a single image.

Render elements are either specialications of ``AElement`` or
``AElementMQTT``. If you write a new element you must also add it to the
``ElementFactory``.

Additional Dependencies
-----------------------

Next to the dependencies listed above, you need to install the
following:

::

    sudo apt install pandoc
    sudo pip3 install pypandoc

Todos
-----

-  Add StaticImage
-  Document code
-  Sanity check of yaml config
-  Automated unit tests (instead of manual testing)
-  "Real-world" examples
-  ...

Misc
----

The code is written for ``python3`` (and tested with python 3.5 on an
Raspberry Pi Zero with Raspbian Stretch).

`Merge requests <https://gitlab.com/pelops/nikippe/merge_requests>`__ /
`bug reports <https://gitlab.com/pelops/nikippe/issues>`__ are always
welcome.

