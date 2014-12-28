==========
AEI Readme
==========

This package provides a specification for the Arimaa Engine Interface (AEI).
It also includes some tools for using engines that implement AEI. Including an
interface to the arimaa.com gameroom. A full description of AEI can be found in
the file ``aei-protocol.txt``.

The link used for communication is not specified by the AEI protocol. This
implementation uses either stdio or a socket for the communication. Stdio is
the preferred method for general operation, but in certain programming
languages or environments it may be easier to use socket communication.

When using a socket the controller will listen on an ip and port given to the
engine by adding "--server <dotted quad ip>" and "--port <port number>" options
to its command line. The engine should connect to the specified address and
expect the AEI protocol identifier from the controller.

The scripts included for working with an AEI engine are:

``analyze``
  A simple script that runs an engine and has it search a given position or
  move sequence.
``gameroom``
  AEI controller that connects to the arimaa.com gameroom and plays a game.
``postal_controller``
  Keeps a bot making moves as needed in any postal games it is a participant
  in.
``roundrobin``
  Plays engines against each other in a round robin tournament.
``simple_engine``
  Very basic AEI engine, just plays random step moves.

Basic examples of using the scripts can be found in the file ``usage.rst``.

The pyrimaa package also includes modules implementing the controller side of
the AEI protocol (``aei.py``), the Arimaa position representation (as bitboards
in ``board.py`` and x88 in ``x88board.py``), and a few utility functions for
handling Arimaa timecontrols (``util.py``).

setup.py can be used to install the package. It depends on python-setuptools
which might need to be installed first.

The pyrimaa package needs to end up on the PYTHONPATH somehow. The intended way for this to happen is for AEI to be installed with setup.py using something like "python setup.py install".

One gotcha though is you probably don't really want it installed into the system python directories (which would also require root). If you use python for lots of different projects I'd recommend setting up a virtualenv for it.

But the easiest thing to do is a user install with "python setup.py install --user" run from the AEI directory. This will install to "~/.local". Python automatically has ~/.local/lib/blah in it's pythonpath so the scripts will work. Also if you add ~/.local/bin to your shell path then you can run the scripts using "gameroom", "analyze", etc..
