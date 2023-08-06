==========================================
mpa.SimulateLibrary
==========================================

.. contents::

**Overview**

``SimulateLibrary`` is a program within the mpathic package which creates a library of
random mutants from an initial wildtype sequence and mutation rate.


**Usage**

    >>> import mpathic as mpa
    >>> mpa.simulate_library_class(wtseq="TAATGTGAGTTAGCTCACTCAT")


**Example Output Table**::

    ct            seq
    100           ACAGGGTTAC
    50            ACGGGGTTAC
    ...


Class Details
-------------

.. autoclass:: mpathic.src.simulate_library.SimulateLibrary
    :members:
