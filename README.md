# ArgumentParserUtils
For many command line scripts I found that I was writing the same ArgumentParser code over and over again. 
So I wrote this library to save all of that repeated work.

## Common Concepts
### Shard
In some use cases you may want to use a helper multiple times in the one script.
For example, a script that needs to open two serial ports, and you want to configure all the parameters for each port.
To do this you would pass in the `shard` option and all the parser parameters will be namespaced by the passed in shard
value.

###  Environment Variables
The default value for each cli option can be set with an environment variable of the same name, converted to uppercase 
and with '-' replaced with '_'. For example, if `shard='input'` then the environment variable for the SerialHelper cli 
option `--input-write-timeout` would be `INPUT_WRITE_TIMEOUT`.

This is particularly useful to pass cli options in IDEs that allow you to specify an environment file in a run profile 
or in use with in a systemd service file's 
[EnvironmentFile](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#EnvironmentFile=) parameter.
In the systemd service file case, there is another helper option `-e/--environment` which when passed into a script will
print out a list of known environment variables (which can be used for the 
[PassEnvironment](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#PassEnvironment=) parameter 
of the systemd service file). For example in the case of a SerialHelper configured with `shard='input'`
the helper will print out:

    Known Environment Variables: INPUT_BAUDRATE INPUT_BYTESIZE INPUT_DSRDTR INPUT_INTER_BYTE_TIMEOUT INPUT_PARITY INPUT_PORT INPUT_RTSCTS INPUT_STOPBITS INPUT_TIMEOUT INPUT_WRITE_TIMEOUT INPUT_XONXOFF

### Set defaults
The author of the script invoking a helper may set the defaults of any parameter by passing the value into the helpers
`add_parser_options method` as a key word argument. For example, if you were using the [SerialHelper](argparseutils/helpers/serialport.py) and wanted to change
the default `baudrate` to `115200` you would call `SerialHelper.add_parser_options` like this:
```python
SerialHelper.add_parser_options(parser, baudrate=115200)
```
### Order of Precedence
The order of precedence used to resolve the end value for a given cli option:

1. The value the user of the script has entered on the command line.
2. The value the user of the script passed via an environment variable.
3. The value the author of the script passed as a keyword parameter to the `add_parser_options method`. 

## [Python Logging Helper](argparseutils/helpers/pythonlogging.py)
This helper configures carries out a basic config for the python logging module.
It also adds another log level `TRACE` to python logging and adds the `logger.trace` method.


## [SerialHelper](argparseutils/helpers/serialport.py)
This helper configures all the parameters needed to configure a serial port. 

### SerialHelper Basic Example
The following [example](examples/serial_basic_example.py):
```python
from argparse import ArgumentParser

from argparseutils.helpers.serialport import SerialHelper


def main():
    parser = ArgumentParser("SerialHelper Test")
    SerialHelper.add_parser_options(parser)
    
    args = parser.parse_args()

    serial_port = SerialHelper.create_serial(args)

if __name__ == '__main__':
    main()
```

when run with the `--help` cli option will produce:

    usage: SerialHelper Test [-h] [-e] --port PORT [--baudrate BAUDRATE]
                             [--bytesize {5,6,7,8}]
                             [--parity {None,Even,Odd,Mark,Space}]
                             [--stopbits {1,1.5,2}] [--timeout TIMEOUT]
                             [--xonxoff {True,False}] [--rtscts {True,False}]
                             [--write-timeout WRITE_TIMEOUT]
                             [--dsrdtr {True,False}]
                             [--inter-byte-timeout INTER_BYTE_TIMEOUT]
    
    options:
      -h, --help            show this help message and exit
      -e, --environment     Displays the known ENVIRONMENT variables that are used
                            as default parser options. (default: False)
      --port PORT           The Serial port to connect to. (default: None)
      --baudrate BAUDRATE   The Serial port baudrate to use. (default: 9600)
      --bytesize {5,6,7,8}  The number of bits for each byte. (default: 8)
      --parity {None,Even,Odd,Mark,Space}
                            The parity algorithm to use. (default: None)
      --stopbits {1,1.5,2}  The number of stop bits to use. (default: 1)
      --timeout TIMEOUT     The read timeout to use (seconds). (default: None)
      --xonxoff {True,False}
                            Use software flow control. (default: False)
      --rtscts {True,False}
                            Use RTS/CTS hardware flow control. (default: False)
      --write-timeout WRITE_TIMEOUT
                            The write timeout to use (seconds). (default: None)
      --dsrdtr {True,False}
                            Use DSR/DTR hardware flow control. (default: False)
      --inter-byte-timeout INTER_BYTE_TIMEOUT
                            The inter byte timeout to use. Disabled by default.
                            (default: None)

### SerialHelper Sharded Example:
The following [example](examples/serial_shard_example.py):
```python
from argparse import ArgumentParser

from argparseutils.helpers.serialport import SerialHelper


def main():
    parser = ArgumentParser("SerialHelper Shard Test")
    SerialHelper.add_parser_options(parser, shard="input")
    SerialHelper.add_parser_options(parser, shard="output")
    
    args = parser.parse_args()

    serial_port = SerialHelper.create_serial(args)

if __name__ == '__main__':
    main()
```
when run with the `--help` cli option will produce:

    usage: SerialHelper Shard Test [-h] [-e] --input-port INPUT_PORT
                             [--input-baudrate INPUT_BAUDRATE]
                             [--input-bytesize {5,6,7,8}]
                             [--input-parity {None,Even,Odd,Mark,Space}]
                             [--input-stopbits {1,1.5,2}]
                             [--input-timeout INPUT_TIMEOUT]
                             [--input-xonxoff {True,False}]
                             [--input-rtscts {True,False}]
                             [--input-write-timeout INPUT_WRITE_TIMEOUT]
                             [--input-dsrdtr {True,False}]
                             [--input-inter-byte-timeout INPUT_INTER_BYTE_TIMEOUT]
                             --output-port OUTPUT_PORT
                             [--output-baudrate OUTPUT_BAUDRATE]
                             [--output-bytesize {5,6,7,8}]
                             [--output-parity {None,Even,Odd,Mark,Space}]
                             [--output-stopbits {1,1.5,2}]
                             [--output-timeout OUTPUT_TIMEOUT]
                             [--output-xonxoff {True,False}]
                             [--output-rtscts {True,False}]
                             [--output-write-timeout OUTPUT_WRITE_TIMEOUT]
                             [--output-dsrdtr {True,False}]
                             [--output-inter-byte-timeout OUTPUT_INTER_BYTE_TIMEOUT]
    
    options:
      -h, --help            show this help message and exit
      -e, --environment     Displays the known ENVIRONMENT variables that are used
                            as default parser options. (default: False)
      --input-port INPUT_PORT
                            The Serial port to connect to. [input] (default: None)
      --input-baudrate INPUT_BAUDRATE
                            The Serial port baudrate to use. [input] (default:
                            9600)
      --input-bytesize {5,6,7,8}
                            The number of bits for each byte. [input] (default: 8)
      --input-parity {None,Even,Odd,Mark,Space}
                            The parity algorithm to use. [input] (default: None)
      --input-stopbits {1,1.5,2}
                            The number of stop bits to use. [input] (default: 1)
      --input-timeout INPUT_TIMEOUT
                            The read timeout to use (seconds). [input] (default:
                            None)
      --input-xonxoff {True,False}
                            Use software flow control. [input] (default: False)
      --input-rtscts {True,False}
                            Use RTS/CTS hardware flow control. [input] (default:
                            False)
      --input-write-timeout INPUT_WRITE_TIMEOUT
                            The write timeout to use (seconds). [input] (default:
                            None)
      --input-dsrdtr {True,False}
                            Use DSR/DTR hardware flow control. [input] (default:
                            False)
      --input-inter-byte-timeout INPUT_INTER_BYTE_TIMEOUT
                            The inter byte timeout to use. Disabled by default.
                            [input] (default: None)
      --output-port OUTPUT_PORT
                            The Serial port to connect to. [output] (default:
                            None)
      --output-baudrate OUTPUT_BAUDRATE
                            The Serial port baudrate to use. [output] (default:
                            9600)
      --output-bytesize {5,6,7,8}
                            The number of bits for each byte. [output] (default:
                            8)
      --output-parity {None,Even,Odd,Mark,Space}
                            The parity algorithm to use. [output] (default: None)
      --output-stopbits {1,1.5,2}
                            The number of stop bits to use. [output] (default: 1)
      --output-timeout OUTPUT_TIMEOUT
                            The read timeout to use (seconds). [output] (default:
                            None)
      --output-xonxoff {True,False}
                            Use software flow control. [output] (default: False)
      --output-rtscts {True,False}
                            Use RTS/CTS hardware flow control. [output] (default:
                            False)
      --output-write-timeout OUTPUT_WRITE_TIMEOUT
                            The write timeout to use (seconds). [output] (default:
                            None)
      --output-dsrdtr {True,False}
                            Use DSR/DTR hardware flow control. [output] (default:
                            False)
      --output-inter-byte-timeout OUTPUT_INTER_BYTE_TIMEOUT
                            The inter byte timeout to use. Disabled by default.
                            [output] (default: None)

## MQTT Helper
