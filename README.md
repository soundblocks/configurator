# SoundBlocks Configurator

SoundBlocks Configurator is a cross-platform graphical application designed for configuring and managing interactive sound module systems. Its interface simplifies the assignment of behaviors and relationships between devices, allowing users to customize the logic of sound interaction without requiring programming skills.

Key Features:
- Communication Network Management: Supports both centralized and decentralized modes using OSC messages and custom protocols.

- Sensor Configuration: Enables definition of the number and type of sensor responses.

- Sound Function Assignment: Allows each module to be assigned specific sound functions, including synthesis parameters and audio playback.

The software is built using open-source technologies and is available for Windows, macOS, and Linux. It is distributed free of charge and includes detailed documentation in both Spanish and English.

Authors: Sabrina García, Laurence Bender, Germán Ito

---

# Reference SoundBlocks Configurator

Each line of the configurator begins with the ID of the module to be configured. The next element in the line defines the module's behavior, indicating whether it will send or receive information.

---

## Send

If the element contains `->` it means that the module will send information.

**Syntax:**

```
module_send -> sensor_send : module_receives
```

### Sensor

Sensors must be separated by commas and can only be selected from the following list:

- `t1` to `t7`: touch sensor (7 in total)  
- `ax`, `ay`, `az`: accelerometer values (X, Y, Z axes)  
- `gx`, `gy`, `gz`: angular velocity (gyroscope)  
- `yaw`, `pitch`, `roll`: orientation (yaw, pitch, and roll)

### Modules that receive

Up to three numerical ranges of destination modules can be defined.  
The ranges are separated by commas, and a hyphen indicates a continuous range.  
To send to a single module, simply specify its number.

**Example:**

```
122->t1,ax:102,105-108
```

Module `122` sends the data from sensor `t1` and the `ax` axis of the accelerometer to modules `102`, `105`, `106`, `107`, and `108`.

---

## Receives

If the element is `<-` it means that the module receives information from another module.

**Syntax:**

```
module_receive <- sensor : module_send @ actuator [map]
```

### Sensor

The specific sensor from which information is received.

### Module that sends

ID of the module that sends the information.

### Actuator

Device or function that is activated based on the received information.  
Available options:

- `dfPlay`: reproduce a sample  
- `dfPause`: pause a sample  
- `dfStop`: stop a sample  
- `dfResume`: resume a sample  
- `dfSetEq`: configures the equalizer  
  - values: `0=Off`, `1=Pop`, `2=Rock`, `3=Jazz`, `4=Classic`, `5=Bass`  
- `dfVolume`: adjusts the volume (`range: 0 to 30`)  
- `dfPlayStop`: toggles between play and stop  
- `dfPlayPause`: toggles between play (or resume) and pause  
- `dfPlayTouch`: plays while the touch is held down  

### Map

It is used to adjust the range of values received by the actuator.  
It can be a single value (maximum) or two values (minimum and maximum).  
If not specified, the default value is `[0,0]`.

**Examples:**

```
108<-ax:122@dfVolume[0,15]
102<-t7:108@dfPlay[3]
```

---

## Comments

Comments are added by prefixing `#` at the beginning of the line or the end of an instruction.

**Example:**

```
122->ax:102,105-108 # Module 122 sends ax to modules 102 and from 105 to 108.
# 102 <- ax : 122 @ dfVolume [0,15]
```
