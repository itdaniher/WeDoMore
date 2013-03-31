##About the WeDo


The [Lego WeDo](http://education.lego.com/en-us/lego-education-product-database/wedo/9580-lego-education-wedo-construction-set/) is a tethered-over-USB sensing and robotics toolkit produced by Lego for the educational market.

It's gotten lots of press, including a favorable review on the One Laptop Per Child blog, on [deployments and training in Peru.](http://blog.laptop.org/2011/02/12/lego-wedo-oloc-peru/)

It's supported by Scratch(on Windows and OSX) and by Lego's proprietary software(on Windows.)

It prominently features the [LB1836](http://semicon.sanyo.com/en/ds_e/EN3947F.pdf) motor driver and the [LM358](http://www.national.com/ds/LM/LM158.pdf) op-amp, as well as an epoxy blob with USB support.

The digital communication protocol used by the Power Functions system is documented on [Philo's Awesome Page](http://www.philohome.com/pf/LEGO_Power_Functions_RC.pdf).

##Requirements

- Python 2.7+
- pyusb (setup.py should take care of installing the dependency)

##Installation

From pypi:

```bash
pip install wedo
```

From the source tree:

```bash
./setup.py install
```

##How to Use it

```python
>>> from wedo import WeDo
>>> wd = WeDo()

# Activating the first motor full forward:
>>> wd.motor_a = 100

# Activating the second motor half speed/force backward:
>>> wd.motor_b = -50

# Current value of the tilt sensor:
>>> wd.tilt

# Current distance value in meters of the distance sensor:
>>> wd.distance```

## Contributors
[Ian Daniher](https://github.com/itdaniher)
Tony Forster
Walter Bender
[Guillaume Binet](https://github.com/gbin)