==============================
mod_twitter
==============================

kovot 用の Twitter mod をいれるための mod

.. code-block:: python

    tw = ModTwitter()
    md = ModDefault("mod/default/kov_default.txt")

    # twitter modules
    tw.add_module(md)
    kovot.add_module(tw)
