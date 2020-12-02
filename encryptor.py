import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os, struct, sys
import py7zr
import shutil



def encrypt(key, path, in_filename, is_dir=False, chunk_size=64*1024):											######## Encrypt function ########

	out_filename = os.path.splitext(in_filename)[0] + '.lock'

	file_or_dir = b'f'

	iv = get_random_bytes(16)																					######## Creating initial vector ########

	cipher = AES.new(key, AES.MODE_CBC, iv)

	file_ext = os.path.splitext(in_filename)[1]
	file_ext+= ' ' * (10 - len(file_ext) % 10)

	if is_dir:
		file_or_dir = b'd'


	filesize = os.path.getsize(os.path.join(path, in_filename))

	try:

		with open(os.path.join(path, in_filename), 'rb') as infile:
			with open(os.path.join(path, out_filename), 'wb') as outfile:

				outfile.write(struct.pack('<10s Q c 16s', file_ext.encode(), filesize, file_or_dir, cipher.encrypt(key)))	######## Writting file extension and file size to the file ########
				outfile.write(iv)

				while True:

					chunk = infile.read(chunk_size)
					if len(chunk) == 0:
						break
					elif len(chunk) % 16 != 0:
						chunk += b' ' * (16 - len(chunk) % 16)

					outfile.write(cipher.encrypt(chunk))

	except :
		print(f"Unable to encrypt, read, locate or write file {in_filename}")
		exit()
	
	else:
		print(f"Successfully encrypted file: {in_filename} to {out_filename}")

def decrypt(key, path, in_filename, chunk_size=64*1024):														######## Decrypt function ########

	out_filename = os.path.splitext(in_filename)[0]

	
	try:

		with open(os.path.join(path, in_filename), 'rb') as infile:
			
			file_ext = struct.unpack('<10s', infile.read(struct.calcsize('10s')))[0].decode('utf8').strip()		######## Getting back the ########
			origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]								######## extension and file size ########
			file_or_dir = struct.unpack('<c', infile.read(struct.calcsize('c')))[0].decode('utf8')				######## Checking for directory or file ########
			key_hash = struct.unpack('<16s', infile.read(struct.calcsize('16s')))[0]
			iv = infile.read(16)

			decryptor = AES.new(key, AES.MODE_CBC, iv)

			key_hash = decryptor.decrypt(key_hash)

			if key != key_hash:
				print("Incorrect password!")
				exit()

			out_filename+=file_ext

			with open(os.path.join(path, out_filename), 'wb') as outfile:
				while True:
					
					chunk = infile.read(chunk_size)

					if len(chunk) == 0:
						break

					outfile.write(decryptor.decrypt(chunk))

				outfile.truncate(origsize)

	except FileNotFoundError:
		print(f"Unable to locate file {in_filename}")
		exit()

	except PermissionError:
		print(f"Unable to read or write file {in_filename}")
		exit()

	except :
		print(f"Unable to decrypt file {in_filename}")
		exit()

	
	else:
		print(f"Successfully decrypted file: {in_filename} to {out_filename}")
		return(file_or_dir)


def get_key(from_encrypt=False):																				######## Function to get the key ########

	
	key1 = input('\nEnter Key: ')

	if from_encrypt:
		key2 = input('Confirm key: ')

		if key1 == key2:

			key_hash = hashlib.scrypt(key1.encode(), salt=b'salt', n=2, r=8, p=1,  dklen=16)

			return(key_hash)

	else:
		key_hash = hashlib.scrypt(key1.encode(), salt=b'salt', n=2, r=8, p=1,  dklen=16)

		return(key_hash)

	print("\nKeys doesnot match!")
	exit()


def archive(path, folder_name):																					######## Function to zip the folder ########
	foldername = folder_name + '.7z'
	
	with py7zr.SevenZipFile(os.path.join(path, foldername), 'w') as archive:
		archive.writeall(os.path.join(path,folder_name), folder_name)

	print(f'Successfully zipped {folder_name} to {foldername}')


def extract(path, file_name):																					######## Funtion to extract the folder ########
	try:
		with py7zr.SevenZipFile(os.path.join(path, file_name), 'r') as archive:
			archive.extractall(path)

		print(f'Successfully unzipped {file_name}')
	except :
		print("Unable to extract data!")
		exit()

def help():
	print('''Help --

syntax:-
	python encryptor.py <option> <filepath>

option:-
	--encrypt / -e 	:	To encrypt a file
	--encrypt-folder / -ef : To encrypt a folder
	--decrypt / -d 	:	To decrypt a file or folder
	
Help:-
	--help / -h 	    :	To get help

Example:-
	encryptor.py --encrypt C:\\users\\secret.txt
		To encrypt a file named secret.txt

	encryptor.py --decrypt C:\\users\\secret.txt
		To decrypt a file or folder named secret.txt

	encryptor.py --help
		To get help

	encryptor.py --encrypt-folder C:\\users\\secret
		To encrypt a folder named secret''')


def delete(path, filename):
	try:
		os.remove(os.path.join(path, filename))
	except:
		shutil.rmtree(os.path.join(path, filename))


def main():																										######## Main Function ########
	if len(sys.argv) < 2:
		help()
		exit()


	if sys.argv[1] == '--help' or sys.argv[1] == '-h':															######## Help ########
		help()
		exit()


	elif len(sys.argv) < 3 or len(sys.argv) > 3:
		print("Incorrect arguments!!!\n")
		help()
		exit()

	full_path = sys.argv[2]
	
	if '\\' not in full_path:
		full_path = os.path.join(os.getcwd(), full_path)

	path, filename = os.path.split(full_path)

	if sys.argv[1] == '--decrypt' or sys.argv[1] == '-d':														######## Decrypt ########
		key = get_key()

		print("Decrypting your file...")
		file_or_folder = decrypt(key, path, filename)
		delete(path, filename)
		if file_or_folder == 'd':
			print("Unzipping files...")
			extract(path, os.path.splitext(filename)[0]+'.7z')
			delete(path, os.path.splitext(filename)[0]+'.7z')

		exit()

	elif sys.argv[1] == '--encrypt' or sys.argv[1] == '-e':														######## Encrypt ########
		key = get_key(from_encrypt=True)

		print("Encrypting your file...")
		encrypt(key, path, filename)
		delete(path, filename)
		exit()

	elif sys.argv[1] == '--encrypt-folder' or sys.argv[1] == '-ef':												######## Encrypt Folder ########
		key = get_key(from_encrypt=True)

		print("\nZipping your files...\nPlease wait...")
		archive(path, filename)
		delete(path, filename)
		print("Encrypting files...")
		encrypt(key, path, filename + '.7z', is_dir=True)
		delete(path, filename + '.7z')
		exit()


	else:
		help()
		exit()



if __name__ =='__main__':
	main()