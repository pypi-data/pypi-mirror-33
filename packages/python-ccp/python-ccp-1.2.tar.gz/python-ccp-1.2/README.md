# ccp

The copy and paste program with clip-server use stdin and stdout. I have problem with send text or file between host is hard so just send it with the relay server.

Github [https://github.com/bongtrop/ccp](https://github.com/bongtrop/ccp)

## Requirements

- Python 2 but i think that code can use in python 3
- Python module that you can see in requirements.txt
- [clip-server](https://github.com/bongtrop/clip-server) by default it point to [http://clip.rop.sh](http://clip.rop.sh)

## Installation

It's simple like the other python project.

### pip 

```bash
pip install python-ccp
```

### Manual

```bash
git clone https://github.com/bongtrop/ccp.git
cd ccp
pip install -r requirements.txt
python setup.py install
```

## Usage

just ```ccp -h```. If you want to change clip server address, Change the `CLIP_SERVER` environment.

```bash
copy paste program with clip-server use stdin and stdout version 1.1

Usage:      ccp copy <name> [-p <password>]
            ccp paste <name> [-p <password>]

Option:     -e Encrypt with secret key

Example:    echo "this_is_data" | ccp copy this_is_name
            ccp paste this_is_name
```

## Contribution

I dont mind the way that you will contribute. Just do it. below is example.

- email
- create issue
- pull request
- carrier pigeon
- tell my friend to tell me
- foo bar

## License

Please see [LICENSE](LICENSE) file.
