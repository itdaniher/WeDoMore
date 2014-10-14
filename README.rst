About the WeDo
--------------

The `Lego WeDo`_ is a tethered-over-USB sensing and robotics toolkit produced by Lego for the educational market.

It's gotten lots of press, including a favorable review on the One Laptop Per Child blog, on `deployments and training in Peru`_.

It's supported by Scratch(on Windows and OSX) and by Lego's proprietary software(on Windows.)

It prominently features the LB1836_ motor driver and the LM358_ op-amp, as well as an epoxy blob with USB support.

The digital communication protocol used by the Power Functions system is documented on `Philo's Awesome Page`_.

Requirements
------------

- Python 2.7+
- pyusb (setup.py should take care of installing the dependency)

Installation
------------

From pypi:

    pip install wedo

From the source tree:

    ./setup.py install


How to Use it
-------------

    >>> from wedo import WeDo
    >>> wd = WeDo()
    # Activating the first motor full forward:
    >>> wd.motor_a = 100
    # Activating the second motor half speed/force backward:
    >>> wd.motor_b = -50
    # Current value of the tilt sensor:
    >>> wd.tilt
    # Current distance value in meters of the distance sensor:
    >>> wd.distance

Contributors
------------

`Ian Daniher`_

Tony Forster

`Walter Bender`_

`Guillaume Binet`_

`Joshua Coxwell`_

`Alan Aguiar`_

.. _`Lego WeDo`: http://education.lego.com/en-us/lego-education-product-database/wedo/9580-lego-education-wedo-construction-set/
.. _LB1836: http://semicon.sanyo.com/en/ds_e/EN3947F.pdf
.. _LM358: http://www.national.com/ds/LM/LM158.pdf
.. _`deployments and training in Peru`: http://blog.laptop.org/2011/02/12/lego-wedo-oloc-peru/
.. _`Philo's Awesome Page`: http://www.philohome.com/pf/LEGO_Power_Functions_RC.pdf
.. _`Guillaume Binet`: https://github.com/gbin
.. _`Ian Daniher`: https://github.com/itdaniher
.. _`Walter Bender`: https://github.com/walterbender
.. _`Joshua Coxwell`: https://github.com/JCoxwell
.. _`Alan Aguiar`: https://github.com/alanjas

