# AES-Encryptor
A python3 program to encrypt or decrypt your files and folders.  
This code uses AES-128 bit to encrypt files with random IV (Initialisation Vector) every time.  
**Also works on Termux with some tinkering.**

## Requirements:-
- Hashlib
  - `pip install hashlib` to install it. It should be pre-installed
- Pycrypto
  - `pip install pycrypto` to install it. It should be pre-installed.
- Struct
  - `pip install struct` to install it. It should be pre-installed.
- Py7zr
  - `pip install py7zr` to install it.
- Shutil
  - `pip install shutil` to install it. It should be pre-installed.


## Usage:-
### Syntax:-
`python encryptor.py <option> <filepath>`
### Options:-
- `--encrypt` or `-e` to encrypt a file.
- `--encrypt-folder` or `-ef` to encrypt a folder.
- `--decrypt` or `-d` to decrypt a file or folder.

### Help:-
`--help` or `-h` to get help.
### Examples:-
- `python encryptor.py --encrypt C:\users\secret.txt`
  - To encrypt a file named secret.txt
- `python encryptor.py --decrypt C:\users\secret.txt`
  - To decrypt a file named secret.txt
- `python encryptor.py --help`
  - To get help
- `encryptor.py --encrypt-folder C:\users\secret`
  - To encrypt a folder named secret
