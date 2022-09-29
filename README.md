Introduction
------------

Rally 7 is a car racing game from Infukor inspired by an arcade classic with a
similar name. Written in Python and using Pygame and Numeric, it should be
playable on a number of different platforms given a fast enough computer.

The aim of the game is to navigate your car around the rally course - a maze
surrounded by scenery - collecting flags and avoiding rocks and the red cars,
making sure that the flags are cleared before your fuel runs out. If the red
cars get too close, a smoke screen can be created to make them crash, but
since this uses fuel, it may be best not to do so too often.

Quick Start
-----------

To run the game, just run the rally7.py program:

  python rally7.py

If you have installed Rally 7 as a package, run the game like this:

  rally7

The game may also have been installed in your games menu:

  "Games" -> "Arcade" -> "Arcade Game (Rally 7)"

Some options can be given to change the game settings:

  --fullscreen  Try and run the game in fullscreen mode.
  --halfsize    Use a game window or display which is half the usual width and
                height.
  --small       A synonym for --halfsize.
  --medium      Use a game window or display which is four fifths (4/5) of the
                usual width and height.
  --no-sound    Mute the sound output from the game.
  --no-intros   Skip game introduction and interlude sequences.
  --no-audio    Prevent the game from even trying to use audio/sound.

For example:

  python rally7.py --fullscreen
  rally7 --fullscreen

On some systems, sound output may be managed by some kind of mixing system;
for example, KDE uses a system called aRts for this purpose. To work in such
environments, you will need to specify a special command before "python".

For example:

  artsdsp python rally7.py --fullscreen
  artsdsp rally7 --fullscreen

Alternatively, you can try and switch off the mixing system.

Game Controls
-------------

Use the following keys to play the game:

  C             Insert coin!
  1             Player 1 (1UP) start
  Z             Turn left
  X             Turn right
  K             Turn upwards
  M             Turn downwards
  L or SPACE    Create smoke screen
  ESCAPE        Quit current game, quit game
  S             Take a snapshot of the screen (as snapshot-*.png in the
                current directory)

Cabinet Controls
----------------

The following keys can be used to set up the game cabinet:

  H             Show the controls
  F1            Small display
  F2            Medium display
  F3            Large display
  F4            Fullscreen mode
  F5            Window mode

Note that in fullscreen mode, the large display may not actually scale to a
larger size on screen than the small or medium size displays; this is due to
the way particular monitors or screens perform scaling of graphical output.
(On the 1280x1024 LCD monitor used for testing, the medium display scaled
better than the large display, for example.)

Requirements
------------

Rally 7 has been tested with the following software:

  Python        2.4.1
  Pygame        1.7.1 (although it should now work with 1.6)
  Numeric       23.7 (using the 23.7-2ubuntu1 package)

The game may work with previous releases of the above software, but this is
not guaranteed.

URLs
----

The required software can be obtained at the following locations:

  Python        http://www.python.org/
  Pygame        http://www.pygame.org/
  Numeric       http://sourceforge.net/projects/numpy/
                http://sourceforge.net/project/showfiles.php?group_id=1369&package_id=1351

Contact, Copyright and Licence Information
------------------------------------------

The current Web page for Rally 7 at the time of release is:

http://www.infukor.com/rally7.html

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt and docs/gpl-3.0.txt for more information.

New in Rally 7 1.0.9 (Changes since Rally 7 1.0.8)
--------------------------------------------------

  * Fixed various packaging issues.

New in Rally 7 1.0.8 (Changes since Rally 7 1.0.7)
--------------------------------------------------

  * Relicensed under the LGPL version 3 or later.
  * Added Ubuntu Feisty (7.04) package support.

New in Rally 7 1.0.7 (Changes since Rally 7 1.0.6)
--------------------------------------------------

  * Added a freeze script for the preparation of stand-alone editions of the
    game using cx_Freeze. Self-extracting executables are also supported using
    makeself.

New in Rally 7 1.0.6 (Changes since Rally 7 1.0.5)
--------------------------------------------------

  * Added --no-audio and some audio device error handling.

New in Rally 7 1.0.5 (Changes since Rally 7 1.0.4)
--------------------------------------------------

  * Added runtime display switching.
  * Added an initialising message and help screen.
  * Fixed number of red cars on challenging stage intro.

New in Rally 7 1.0.4 (Changes since Rally 7 1.0.3)
--------------------------------------------------

  * Fixed fuel draining and improved fuel bar plotting.
  * Fixed non-integer medium screen size dimensions.

New in Rally 7 1.0.3 (Changes since Rally 7 1.0.2)
--------------------------------------------------

  * Added a demo mode.
  * Added a medium screen size.
  * Made fixes to the tools.

New in Rally 7 1.0.2 (Changes since Rally 7 1.0.1)
--------------------------------------------------

  * Added a desktop entry and icon for the game.
  * Added tests to signal when the game resources are not available.
  * Improved the packaging to make smaller source packages.

New in Rally 7 1.0.1 (Changes since Rally 7 1.0)
------------------------------------------------

  * Added support for Pygame 1.6 (when copying loaded images).

Preparing the Graphics
----------------------

A tool is provided to convert the graphics templates into bitmaps for use in
the game:

  python tools/convert.py

This uses the ksvgtopng utility to convert SVG files to PNG images, storing
them in the data directory and under various subdirectories. This utility is
found in the KDE distribution, possibly in a GNU/Linux distribution package
such as kdelibs-bin - it was found in the 3.4.0-0ubuntu3.5 version of that
package in the Kubuntu 5.04 distribution, for example.

Composing the Music
-------------------

The NoteEdit application was used to prepare the music scores, in conjunction
with Timidity. On Linux-based systems it appears necessary to configure the
sequencer devices before trying to use MIDI-enabled software, and this can be
achieved as follows (as root or using sudo):

  modprobe snd-seq-device
  modprobe snd-seq-midi

Timidity can then be run as a software synthesiser as follows:

  timidity -iA -OR -s 44100 &

This uses the ALSA interface and sends the output via artsd at 44100Hz.
NoteEdit can then produce sounds while score editing is taking place.

Preparing the Music
-------------------

To prepare the final tracks in other formats - useful to avoid making other
people configure MIDI playback - a tool is provided to run the Timidity
software to convert the tracks to more typical audio files, and to use the sox
utility to remove superfluous silence from the end of the tracks:

  python tools/music.py

Specifying a format (by default "ogg" is used, but alternatives include "wav")
will change the kind of audio files produced; these are stored in the
data/music directory.

Note that the above configuration for Linux-based systems appears not to be
necessary when just preparing sound files containing the recorded music:
Timidity can presumably synthesize the instrument noises without relying on
various kernel modules.

Requirements for Music Preparation
----------------------------------

The following tools and accessories have been tested:

  timidity      2.13.2 (using the 2.13.2-5ubuntu1 package)
  freepats      20040611-1 (Ubuntu package)
  noteedit      2.7.1 (using the 2.7.1-2 Ubuntu package)
  sox           12.17.5 (using the 12.17.5-4 Ubuntu package)

Release Procedures
------------------

Update the rally7.py __version__ attributes.
Change the version number and package filename/directory in the documentation.
Update the release notes (see above).
Check the setup.py file (if eventually written).
Check the release information in the PKG-INFO file and in the package
changelog (and other files).
Tag, export.
Generate the resources (for the non-packaged full version).
Remove generated .pyc files: rm `find . -name "*.pyc"`
Archive, upload.
Update the pygame.org record.

Making Packages
---------------

To make Debian-based packages:

  1. Create new package directories under packages if necessary.
  2. Make a symbolic link in the distribution's root directory to keep the
     Debian tools happy. Try one of the following:

     ln -s packages/ubuntu-hoary/rally7/debian/
     ln -s packages/ubuntu-feisty/rally7/debian/

  3. Run the package builder:

     dpkg-buildpackage -rfakeroot

  4. Locate and tidy up the packages in the parent directory of the
     distribution's root directory.
