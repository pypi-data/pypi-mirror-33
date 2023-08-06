.. _voicechat:

``voicechat``
=============

.. note::

   Extra-highly experimental. Don't use for real things yet!

This needs a **few weird dependencies** including the Python GStreamer
bindings which unfortunately can't be installed via PyPI. On Debian,
you need::

    apt-get install python-gst0.10
    apt-get install gstreamer0.10-tools gstreamer0.10-plugins-base gstreamer0.10-plugins-good gstreamer0.10-plugins-bad gstreamer0.10-plugins-ugly gstreamer0.10-alsa gstreamer0.10-pulseaudio
    # one of alsa or pulseaudio can go away from above if you like

And you need to create your ``virtualenv`` with
``--system-site-packages`` to get the above bindings. I'm hoping there
is an easier/better solution. One might be to simply use
``gst-launcher0.10`` instead of the Python bindings. Still a Debian
package to install, but that would get rid of the
``--system-site-packages`` at least if you're working in a venv.

You also need to install ``txtorsocksx
<https://github.com/david415/txtorsocksx>_`` in your venv, like so::

    pip install git+https://github.com/david415/txtorsocksx.git

This gives you the client-side endpoint-over-Tor functionality that
the example below uses.

For ALSA, an example for an explicit source for, say, a USB-attached
microphone might be: ``alsasrc device="plughw:CARD=A10,DEV=0"`` You
may figure out the ``CARD`` and ``DEV`` IDs with ``arecord``.

..sourcecode:: console-session

    user@machine:~$ arecord -l
    card 1: A10 [A Device 1.0], device 0: USB Audio [USB Audio]
      Subdevices: 1/1
      Subdevice #0: subdevice #0
    # test that it works:
    user@machine:~$ gst-launch-0.10 alsasrc device="plughw:CARD=A10,DEV=0" ! audioconvert ! autoaudiosink


**REMINDER** that this is in no way audited. I'd like some feedback,
ideally in the form of pull-requests or issues filed on GitHub. I also
have little concrete notion of the privacy implications of a voice
codec over Tor. Feedback via IRC suggested a fixed-bit-rate codec at
minimum. I've tried Vorbis, Opus and SPEEX (the latter deprecated in
favour of Opus) and changing this is fairly easy by playing with the
GStreamer pipelines.


Examples
--------

The initiator of the phone call simply runs ``carml
voicechat``. Eventually, a Tor launches and publishes a hidden-service
on port 5050 -- the ``.onion`` URI will be printed on the
command-line. Once this happens, securely communicate the URI to your
callee, who then runs::

    carml voicechat --client tor:blargfoobar.onion:5050

Eventually, this should connect and you can theoretically both hear
each other. If you get a "connection refused" from the client side,
simply try again.

I'm simply using ``autoaudiosink`` and ``autoaudiosrc`` in the
gstreamer pipelines, which I *believe* means that whatever you set up
using ``gstreamer-properties`` will get used. Otherwise, figure out
what gstreamer source you need and edit the code.

As a fallback for testing, you can use ``audiotestsrc`` which emits a
really annoying continuous tone. You can also easily change the source
code so that your server listens on a public non-Tor port for testing;
then the client-side command-line would look like ``carml
voicechat --client tcp:1.2.3.4:5050`` if your server is on 1.2.3.4
