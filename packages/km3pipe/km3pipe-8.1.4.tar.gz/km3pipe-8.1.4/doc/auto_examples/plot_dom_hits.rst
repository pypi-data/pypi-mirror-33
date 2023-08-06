

.. _sphx_glr_auto_examples_plot_dom_hits.py:


==================
DOM hits.
==================

Estimate track/DOM distances using the number of hits per DOM.




.. image:: /auto_examples/images/sphx_glr_plot_dom_hits_001.png
    :align: center


.. rst-class:: sphx-glr-script-out

 Out::

    Loading style definitions from '/Users/tamasgal/Dev/km3pipe/km3pipe/kp-data/stylelib/km3pipe.mplstyle'
    Detector: Parsing the DETX header
    Detector: Reading PMT information...
    Detector: Done.
    km3pipe.io.hdf5.HDF5Pump: Reading group information from '/group_info'.
    Pipeline and module initialisation took 0.034s (CPU 0.022s).
    --------------------------[ Blob     100 ]---------------------------
    --------------------------[ Blob     200 ]---------------------------
    --------------------------[ Blob     300 ]---------------------------
    --------------------------[ Blob     400 ]---------------------------
    --------------------------[ Blob     500 ]---------------------------
    ================================[ . ]================================
           n_hits    distance
    0           3  319.432073
    1           3   84.027581
    2           4   74.933425
    3           4   82.240334
    4           2  102.219993
    5           2   89.088059
    6           2  398.380855
    7           3   70.289436
    8           8   61.301031
    9           6   52.498108
    10          5   43.992152
    11          2   35.994317
    12         11   28.929146
    13         16   23.647904
    14         15   21.507544
    15         23   23.386937
    16         34   28.501691
    17          2  378.369175
    18          2  113.416443
    19          2   71.812430
    20          4   53.919127
    21          2   45.320313
    22          3   37.170048
    23          2   29.838187
    24          5   24.084136
    25         18   21.231982
    26          6   22.418112
    27          7   27.117701
    28          7   33.899718
    29          7   41.761648
    ...       ...         ...
    20888       2  511.669102
    20889      14   36.874603
    20890      16   31.723224
    20891      11   28.047885
    20892       7   26.470722
    20893       5   30.492830
    20894       6   35.283296
    20895       3   47.709439
    20896       2   54.702576
    20897       2   61.985865
    20898       2   69.468104
    20899       5   84.817689
    20900       2   69.092469
    20901       8   61.235423
    20902       5   53.474098
    20903      12   45.857122
    20904      14   38.470331
    20905      16   31.476205
    20906      42   25.203789
    20907      25   20.332357
    20908      43   18.035324
    20909      33   19.257086
    20910      22   23.454044
    20911      11   29.377599
    20912       2   87.368194
    20913       5   79.212811
    20914       7   71.062168
    20915       6   62.918109
    20916       4   54.783569
    20917      17   46.663528

    [20918 rows x 2 columns]
    ============================================================
    500 cycles drained in 10.130037s (CPU 9.477818s). Memory peak: 301.16 MB
      wall  mean: 0.020000s  medi: 0.014575s  min: 0.004644s  max: 2.171816s  std: 0.096654s
      CPU   mean: 0.018758s  medi: 0.013724s  min: 0.004645s  max: 2.130131s  std: 0.094766s




|


.. code-block:: python

    from __future__ import absolute_import, print_function, division

    # Author: Tamas Gal <tgal@km3net.de>
    # License: BSD-3

    from collections import defaultdict, Counter

    import numpy as np
    import pandas as pd

    import matplotlib.pyplot as plt
    from matplotlib.colors import LogNorm

    import km3pipe as kp
    from km3pipe.dataclasses import Table
    from km3pipe.math import pld3
    from km3modules.common import StatusBar
    import km3pipe.style
    km3pipe.style.use("km3pipe")

    filename = "data/km3net_jul13_90m_muatm50T655.km3_v5r1.JTE_r2356.root.0-499.h5"
    cal = kp.calib.Calibration(
        filename="data/km3net_jul13_90m_r1494_corrected.detx")


    def filter_muons(blob):
        """Write all muons from McTracks to Muons."""
        tracks = blob['McTracks']
        muons = tracks[tracks.type == 5]
        blob["Muons"] = Table(muons)
        return blob


    class DOMHits(kp.Module):
        """Create histogram with n_hits and distance of hit to track."""

        def configure(self):
            self.hit_statistics = defaultdict(list)

        def process(self, blob):
            hits = blob['Hits']
            muons = blob['Muons']

            highest_energetic_muon = Table(muons[np.argmax(muons.energy)])
            muon = highest_energetic_muon

            triggered_hits = hits.triggered_rows

            dom_hits = Counter(triggered_hits.dom_id)
            for dom_id, n_hits in dom_hits.items():
                try:
                    distance = pld3(cal.detector.dom_positions[dom_id], muon.pos,
                                    muon.dir)
                except KeyError:
                    self.log.warning("DOM ID %s not found!" % dom_id)
                    continue
                self.hit_statistics['n_hits'].append(n_hits)
                self.hit_statistics['distance'].append(distance)
            return blob

        def finish(self):
            df = pd.DataFrame(self.hit_statistics)
            print(df)
            sdf = df[(df['distance'] < 200) & (df['n_hits'] < 50)]
            bins = (max(sdf['distance']) - 1, max(sdf['n_hits']) - 1)
            plt.hist2d(
                sdf['distance'],
                sdf['n_hits'],
                cmap='plasma',
                bins=bins,
                norm=LogNorm())
            plt.xlabel('Distance between hit and muon track [m]')
            plt.ylabel('Number of hits on DOM')
            plt.show()


    pipe = kp.Pipeline()
    pipe.attach(kp.io.HDF5Pump, filename=filename)
    pipe.attach(StatusBar, every=100)
    pipe.attach(filter_muons)
    pipe.attach(DOMHits)
    pipe.drain()

**Total running time of the script:** ( 0 minutes  17.440 seconds)



.. only :: html

 .. container:: sphx-glr-footer


  .. container:: sphx-glr-download

     :download:`Download Python source code: plot_dom_hits.py <plot_dom_hits.py>`



  .. container:: sphx-glr-download

     :download:`Download Jupyter notebook: plot_dom_hits.ipynb <plot_dom_hits.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.readthedocs.io>`_
