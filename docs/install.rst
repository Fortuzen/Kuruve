.. _install:

Installation
==================================

Download Kuruve from the github and run (after you have installed all the necessary dependencies)

.. code-block:: bash

   pip install .
   # or if you want to edit files
   pip install -e <pathToKuruve>



Dependencies
----------------------------------

The game itself only needs `pygame <https://www.pygame.org>`_

.. code-block:: bash

   pip install pygame

The environments need `gym <https://github.com/openai/gym>`_ and `numpy <https://scipy.org/install.html>`_

.. code-block:: bash

   pip install gym

If you want to run the examples, you need to have `stable-baselines <https://github.com/hill-a/stable-baselines/>`_ installed.
To install stable-baselines, refer to these `instructions <https://stable-baselines.readthedocs.io/en/master/guide/install.html>`_
Some examples might need `Pillow <https://pillow.readthedocs.io/en/latest/installation.html>`_.

