# Overview

Pelops is a set of microservices that are coupled via mqtt. The idea is to provide small programs that are configured and drive raspberry pi controlled sensors and actuators. Thus - ideally - rich solutions can be built without any programming and with little engineering efford. It can be used for example to make a stand alone solution on one raspi, make a distributed system where several devices interact (maybe even via internet services like AWS IoT), or interact with home automation systems like openhab. Focus is on ePapers for display devices (currently supported are three epapers/einks from Waveshare).

![Component Overview](img/Microservice Overview.png)

Currently, five microservices are available:
 * [Alcathous](https://gitlab.com/pelops/alcathous) - This software subscribes to mqtt-topics that contain raw sensor data and publishes average values for configurable time spans.
 * [Argaeus](https://gitlab.com/pelops/argaeus) - GUI/Frontend for a room thermostat with epaper
 * [Copreus](https://gitlab.com/pelops/copreus) - This library provides a framework to write device driver for the raspberry pi that are connected to MQTT.
 * [Epidaurus](https://gitlab.com/pelops/epidaurus) - PID controller for thermostat
 * [Eurydike](https://gitlab.com/pelops/eurydike) - Eurydike is a simple event detection. Reacts to above-threshold, below-threshold, and outside value-band.  
 * [Hippasos](https://gitlab.com/pelops/hippasos) - Mqtt microservice to play sounds.  
 * [Nikippe](https://gitlab.com/pelops/nikippe) - A general purpose gui image generator/display server - takes values from mqtt and sends image to mqtt.

Planned microservices:
 * [Archippe](https://gitlab.com/pelops/archippe) - Archippe is a data persistence micro service for pelops. Targets are influxdb and csv-files. 
 * [Hippodamia](https://gitlab.com/pelops/hippodamia) - Hippodamia observe the state of all registered microservices (aka watch dog).
 * [Lysidike](https://gitlab.com/pelops/lysidike) - Lysidike publishes incoming mqtt messages to various internet services like email.
  

The project [Pelops](https://gitlab.com/pelops/pelops) provides common classes like mqtt-client, pyyaml wrapper. Thus it is not a microservice itself.

# Example

For the example we use a simple setup with two raspis - one raspi "Sensor" has a sensor for temperature/humidity/pressure connected via I2C-bus, the other one "Display" has an e-Paper connected via SPI. The goal is to display the humidity  readings from room "A" on the epaper in room "B" regularly.

## Introduction

![Setup](img/example_setup.png)

The [bme280](https://www.bosch-sensortec.com/bst/products/all_products/bme280) sensor from bosch can usullay be connected via SPI and I2C. In this example we are using a breakout board that provides I2C connectivity (e.g. CJMCU-280E). As e-paper we are using the raspberri pi hat module from Waveshare: [2.13inch e-Paper HAT](https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT). It is a black/white e-paper, that connects via SPI and in this form is attached as hat-module to the raspberri pi.

![Display](img/test_renderer.png)

On the e-paper the humiditiy should be displayed. Three different graphical elements are used:
  * A bar showing the current value relative to a min and a max value.
  * A chart showing the history of all received values with auto-scale.
  * The current value printed in text.

Both raspis are running raspbian stretch lite with python3. On raspi "Display" a mqtt message broker (mosquitto) is installed. The ip-addresses are 192.168.10.1 ("Sensor") and 192.168.10.2 ("Display").

![MQTT message sequence](img/mqtt_message_sequence.png)

Four instances of the microservices are used:
  * The bem280 driver on "Sensor" is an instance of Copreus.
  * Data preperation running on "Sensor" is an instance of Alcathous.
  * Display driver running on "Display" is an instance of Nikippe.
  * Finally, the epaper driver runnint on "Display" is again an instance of Copreus.

Topics for pub/sub are:
  * "/A/humidity/raw" - raw humidity value / updated every 15 seconds
  * "/A/humidity/avg" - average humidity value / 5 minute average sliding window updated every minute
  * "/B/display" - image that should be displayed on the epaper

## Raspi "Sensor"
### Hardware
The ```bme280``` needs four connections to the raspi: 3.3V, GND, SDA, SCL. On raspberry pi 1 b models the data pins are labeled SDA0 and SCL0, on newer models they are labeled SDA1 and SCL1. On all models the pins are the same:
  * pin 1: 3.3V
  * pin 3: SDA
  * pin 5: SCL
  * pin 6: GND

The pins of the breakout board can be directly connected to the raspi.

### Installation
#### Prerequisites
```
sudo apt install python3 python3-pip
```
#### Device Driver
```
sudo pip3 install RPi.GPIO paho-mqtt pyyaml setuptools
sudo pip3 install copreus
sudo pip3 install smbus2 RPi.bme280
```
#### Data Preparation
```
sudo pip3 install alcathous
```

### Configuration
#### Activate I2C
The bme280 sensor is connected via the I2C bus. The dedicated pins must be activated.
```
sudo raspi-config
```
'5 Interfacing Options' > 'P5 I2C' > 'YES' > 'OK' > 'Finish'

#### mqtt credentials
Create a file that stores the mqtt credentials for the microservices.
```
nano /home/pi/credentials.yaml
```
Copy/paste the following lines:
```
mqtt:
    mqtt-user: mqtt_username
    mqtt-password: super-secret-password
```

#### Copreus
```
mkdir /home/pi/sensor_services
nano /home/pi/sensor_services/a_copreus.yaml
```
Copy/paste the following lines:
```
mqtt:
    mqtt-address: 192.168.10.2
    mqtt-port: 1883
    mqtt-credentials: ~/credentials.yaml

device:
    poll-interval: 15
    type: bme_280
    port: 1
    address: 0x76
    use-calibration-temperature: False
    calibration-temperature:
        # - [ref_value, raw_value]
    use-calibration-humidity: False
    calibration-humidity:
        # - [ref_value, raw_value]        
    use-calibration-pressure: False
    calibration-pressure:
        # - [ref_value, raw_value]        
    topics-pub:
        temperature: /A/temperature/raw
        humidity: /A/humidity/raw
        pressure: /A/pressure/raw
```
To determine port and address the tool i2cdetect can be used: ```sudo apt install i2c-tools```. The command ```sudo i2cdetect -y 1``` generates a list of all connected I2C-devices and their addresses. For raspberries prior to 2013 port may be 0 - newer devices should have port 1.

#### Alcathous
```
nano /home/pi/sensor_services/a_alcathous.yaml
```
Copy/paste the following lines:
```
mqtt:
    mqtt-address: 192.168.10.2
    mqtt-port: 1883
    mqtt-credentials: ~/credentials.yaml

general:
    no_data_behavior: last_valid  # mute, last_valid, empty_message
    update_cycle: 60  # new values published each ... seconds
    number_worker: 1  # how many worker threads should be spawned to process task queue

methods:
    avg_5min:
        topic-pub-suffix: avg
        algorithm: avg  # avg - average, wavg - weighted average
        time_window: 5  # use the values from the last ... minutes

datapoints:
    - topic-sub: /A/humidity/raw
      topic-pub-prefix: /A/humidity/
      zero_is_valid: False  # 0 is valid or rejected
      methods: avg_5min
```
This is the simplest possible configuration for Alcathous - one subscription is processed by one method.

#### start script

The direct start commands for the two services are:
  * ```copreus_bme_280 -c /home/pi/sensor_services/a_copreus.yaml```
  * ```alcathous -c /home/pi/sensor_services/a_alcathous.yaml```

There are many ways to run them permanently as background tasks. In this example, the shell program ```screen```.

```
sudo apt install screen
nano /home/pi/sensor_services/a_start_script.sh
```
Copy/paste the following lines:
```
#!/bin/bash
screen -d -m -S copreus bash -c 'copreus_bme_280 -c /home/pi/sensor_services/a_copreus.yaml'
screen -d -m -S alcathous bash -c 'alcathous -c /home/pi/sensor_services/a_alcathous.yaml'
```

The advantage of screen with these parameters is, that you can reattach to the session with ```screen -r copreus```. This comes handy when you are debugging - don't forget to use the additional parameter ```-v``` for ```copreus_bme_280``` and ```alcathous``` which turns on verbose debugging info.

Finally, make the script run-able with
```
chmod +x /home/pi/sensor_services/a_start_script.sh
```

What this approach does not do for you is to start the microservices automatically upon startup of the raspi.

### Run it
Starting is straight forward:
```
/home/pi/sensor_services/a_start_script.sh
```

You can test what messages are published with the mosquitto sub client:
```
mosquitto_sub -h 192.168.10.2 -p 1883 -u mqtt_username -P super-secret-password -v -t /A/humidity/#
```

Every 15 seconds a message with topic ```/A/humidity/raw``` and a float value as well as every 60 seconds a message with topic ```/A/humidity/avg``` and a float value should be written to the shell.

A typical output would be:
```
/A/humidity/avg (null)
/A/humidity/raw 53.62083402524287
/A/humidity/raw 53.47098143613163
/A/humidity/raw 53.485963186677566
/A/humidity/raw 53.47170033378046
/A/humidity/avg 53.51236974545813
/A/humidity/raw 53.423118669621644
/A/humidity/raw 53.384921836545054
/A/humidity/raw 53.38516047209545
/A/humidity/raw 53.39530683302252
/A/humidity/avg 53.45474834913965
/A/humidity/raw 53.1678391736137
/A/humidity/raw 52.936694177443975
/A/humidity/raw 52.86416288796717
/A/humidity/raw 52.807065091392346
/A/humidity/avg 53.28447901029454
/A/humidity/raw 52.89364172877349
/A/humidity/raw 53.126682155838424
/A/humidity/raw 53.116775776238136
/A/humidity/raw 53.010864342444755
/A/humidity/avg 53.22260700792682
/A/humidity/raw 53.14165994996869
/A/humidity/raw 53.11335306542827
/A/humidity/raw 52.58644878875868
/A/humidity/raw 52.567561245450115
/A/humidity/avg 53.14853675882175
```
The first value for ```/A/humidity/avg``` is ```(null)``` because Alcathous has not received any values yet.


## Raspi "Display"
### Hardware
The 2.13 e-paper hat is attached directly to a raspberri pi 3 zero w.

### Installation
#### MQTT Broker
In this example ```mosquitto``` is used as mqtt broker.
```
sudo apt install mosquitto mosquitto-clients
```
As credentials username and password are used:
```
cd /etc/mosquitto
sudo mosquitto_passwd -r passwords mqtt_username
```
Enter a super-secret password twice.

#### Prerequisites
```
sudo apt install python3 python3-pip
sudo pip3 install pelops
```
#### Device Driver
```
sudo pip3 install RPi.GPIO paho-mqtt pyyaml setuptools
sudo pip3 install copreus
sudo apt install libopenjp2-7 libtiff5
sudo pip3 install spidev Pillow
```
#### Display Server
```
sudo apt install python-pil
sudo pip3 install nikippe
```

Font-package:
```
sudo apt install fonts-dejavu
```

### Configuration
#### Activate I2C
The epaper is connected via the SPI interface which must be activated.
```
sudo raspi-config
```
'5 Interfacing Options' > 'P4 SPI' > 'YES' > 'OK' > 'Finish'

#### mqtt credentials
Create a file that stores the mqtt credentials for the microservices.
```
nano /home/pi/credentials.yaml
```
Copy/paste the following lines:
```
mqtt:
    mqtt-user: mqtt_username
    mqtt-password: super-secret-password
```

#### Copreus
```
mkdir /home/pi/display_services
nano /home/pi/display_services/b_copreus.yaml
```
Copy/paste the following lines:
```
mqtt:
    mqtt-address: 192.168.10.2
    mqtt-port: 1883
    mqtt-credentials: ~/credentials.yaml

device:
    model: 2.13
    type: epaper
    spi:
        pin_cs: -1 # use spi cs mechanism. GPIO08/SPI_CE0_N
        bus: 0
        device: 0
        maxspeed: 2000000
    transpose: 90
    pin_rst:  17  # default values from spec
    pin_dc:   25  # default values from spec
    pin_busy: 24  # default values from spec
    VCOM: -3.3  # default values from spec
    autodeepsleep: True
    topics-sub:
        full_image: /B/display/full_image
        full_image_twice: /B/display/full_image_twice
        part_image: /B/display/part_image
        part_image_twice: /B/display/part_image_twice
    topics-pub:
        message_queue_size: /B/display/message_queue_size
```

#### Nikippe
```
nano /home/pi/display_services/b_nikippe.yaml
```
Copy/paste the following lines:
```
mqtt:
    mqtt-address: localhost
    mqtt-port: 1883
    mqtt-credentials: ~/credentials.yaml

display-server:
    epaper_full_image: /B/display/full_image
    epaper_full_image_twice: /B/display/full_image_twice
    send-on-change: True  # send new image to epaper if any element reports that it received an update
    send-interval: 60  # seconds. if 0 interval is disabled.
    wipe-screen:
        every-nth-day: 1  # 0 for never
        time: 03:15 # wipe-screen will be called at the first update after this time. ignored if every-nth-day==0
        at-start-up: True
        
renderer:
    width: 250
    height: 122
    background: /home/pi/display_services/gui_background_2.13.png  # optional
    background-color: 255  # either 0 or 255.
    elements:
      - name: humidity-chart
        type: chart
        active: True
        group-by: 300  # in seconds. 0==no grouping
        aggregator: avg  # aggregator for group-by. valid values: avg, min, max, median. can be omitted if group-by=0.
        connect-values: True  # if true - values are connected with lines, other wise they are independent dots
        pixel-per-value: 2  # a new value/dot is drawn every n-th pixel on the x-axis. must be > 0.        
        topic-sub: /A/humidity/avg
        width: 210
        height: 60
        border-top: False
        border-bottom: True
        border-left: True
        border-right: False
        x: 30
        y: 5
        foreground-color: 0  # either 0 or 255.
        background-color: 255  # either 0 or 255.

      - name: current-humidity
        type: bar
        active: True
        x: 5
        y: 5
        width: 20
        height: 60
        border: True
        orientation: up  # up, down, left, right
        foreground-color: 0  # either 0 or 255.
        background-color: 255  # either 0 or 255.
        topic-sub: /A/humidity/avg
        min-value: 5
        max-value: 23

      - name: humidity-value
        type: mqtttext
        active: True
        x: 5
        y: 65
        width: 55
        height: 25
        foreground-color: 0  # either 0 or 255.
        background-color: 255  # either 0 or 255.
        font: /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
        size: 16
        string: "{0:.1f}%"
        topic-sub: /A/humidity/avg

      - name: design
        type: statictext
        active: True
        x: 88
        y: 96
        width: 76
        height: 10
        foreground-color: 0  # either 0 or 255.
        background-color: 255  # either 0 or 255.
        font: /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
        size: 8
        string: "design by tgd1975"
```

Finally, the background image must either be downloaded or the option in the yaml file must be removed.
```
cd /home/pi/display_services
wget https://gitlab.com/pelops/nikippe/raw/master/resources/gui_background_2.13.png
```

#### start script

The direct start commands for the two services are:
  * ```copreus_epaper -c /home/pi/display_services/b_copreus.yaml```
  * ```nikippe -c /home/pi/display_services/b_nikippe.yaml```

There are many ways to run them permanently as background tasks. In this example, the shell program ```screen```.

```
sudo apt install screen
nano /home/pi/display_services/b_start_script.sh
```
Copy/paste the following lines:
```
#!/bin/bash
screen -d -m -S copreus bash -c 'copreus_epaper -c /home/pi/display_services/b_copreus.yaml'
screen -d -m -S nikippe bash -c 'nikippe -c /home/pi/display_services/b_nikippe.yaml'
```

The advantage of screen with these parameters is, that you can reattach to the session with ```screen -r copreus```. This comes handy when you are debugging - don't forget to use the additional parameter ```-v``` for ```copreus_epaper``` and ```nikippe``` which turns on verbose debugging info.

Finally, make the script run-able with
```
chmod +x /home/pi/display_services/b_start_script.sh
```

What this approach does not do for you is to start the microservices automatically upon startup of the raspi.

### Run it
Starting is straight forward:
```
/home/pi/display_services/b_start_script.sh
```

## Wrap-Up
If the start-up scripts have been executed successfully on both raspis, the epaper should display the current humidity.
