import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os, struct, sys
import py7zr
import shutil



def encrypt(key, path, in_filename, out_filename=None, chunk_size=64*1024):############### Encrypt function ##################

	if not out_filename:
		out_filename = os.path.splitext(in_filename)[0] + '.lock'

	iv = get_random_bytes(16)#################### Creating initial vector ###############################

	cipher = AES.new(key, AES.MODE_CBC, iv)

	file_ext = os.path.splitext(in_filename)[1]
	file_ext+= ' ' * (10 - len(file_ext) % 10)


	filesize = os.path.getsize(os.path.join(path, in_filename))

	try:

		with open(os.path.join(path, in_filename), 'rb') as infile:
			with open(os.path.join(path, out_filename), 'wb') as outfile:

				outfile.write(struct.pack('<10s Q', file_ext.encode(), filesize))#### Writting file extension and file size to the file ####
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

def decrypt(key, path, in_filename, out_filename=None, chunk_size=64*1024):############### Decrypt function ################

	if not out_filename:
		out_filename = os.path.splitext(in_filename)[0]

	
	try:

		with open(os.path.join(path, in_filename), 'rb') as infile:
			
			file_ext = struct.unpack('<10s', infile.read(struct.calcsize('10s')))[0].decode('utf8').strip()####### Getting back the #######
			origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]######################## extension and file size ##########
			iv = infile.read(16)

			decryptor = AES.new(key, AES.MODE_CBC, iv)

			out_filename+=file_ext

			with open(os.path.join(path, out_filename), 'wb') as outfile:
				while True:
					
					chunk = infile.read(chunk_size)

					if len(chunk) == 0:
						break

					outfile.write(decryptor.decrypt(chunk))

				outfile.truncate(origsize)

	except :
		print(f"Unable to decrypt, read, locate or write file {in_filename}")
		exit()
	
	else:
		print(f"Successfully decrypted file: {in_filename} to {out_filename}")


def get_key():############################ Function to get the key ############################

	print("\nCheck your password twice before entering!!!")
	print("If the password is wrong, your data will be deleted!\n")
	key1 = input('Enter Key: ')

	key2 = input('Confirm key: ')

	if key1 == key2:

		key_hash = hashlib.scrypt(key1.encode(), salt=b'salt', n=2, r=8, p=1,  dklen=16)

		return(key_hash)

	print("\nKeys doesnot match!")
	exit()


def archive(path, folder_name):############################# Function to zip the folder ###############################
	foldername = folder_name + '.7z'
	
	with py7zr.SevenZipFile(os.path.join(path, foldername), 'w') as archive:
		archive.writeall(os.path.join(path,folder_name), folder_name)

	print(f'Successfully zipped {folder_name} to {foldername}')


def extract(path, file_name):################################ Funtion to extract the folder
	# filename = file_name + '.7z'
	try:
		with py7zr.SevenZipFile(os.path.join(path, file_name), 'r') as archive:
			archive.extractall(path)

		print(f'Successfully unzipped {file_name}')
	except :
		print("Wrong password! you lost your data :)")

def help():
	print('''Help --

syntax:-
	python encryptor.py <option> <filepath>

option:-
	--encrypt / -e 	:	To encrypt a file
	--decrypt / -d 	:	To decrypt a file
	--encrypt-folder / -ef : To encrypt a folder
	--decrypt-folder / -df : To decrypt a folder

Help:-
	--help / -h 	    :	To get help

Example:-
	encryptor.py --encrypt C:\\users\\secret.txt
		To encrypt a file named secret.txt

	encryptor.py --decrypt C:\\users\\secret.txt
		To decrypt a file named secret.txt

	encryptor.py --help
		To get help

	encryptor.py --encrypt-folder C:\\users\\secret
		To encrypt a folder named secret

	encryptor.py --decrypt-folder C:\\users\\secret
		To decrypt a folder named secret


    ############## CAUTION ###############

    INCORRECT PASSWORD WILL RUIN YOUR DATA

    ######################################''')


def delete(path, filename):
	try:
		os.remove(os.path.join(path, filename))
	except:
		shutil.rmtree(os.path.join(path, filename))


def main():
	if len(sys.argv) < 2:
		help()
		exit()


	if sys.argv[1] == '--help' or sys.argv[1] == '-h':
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

	if sys.argv[1] == '--decrypt' or sys.argv[1] == '-d':
		key = get_key()

		print("Decrypting your file...")
		decrypt(key, path, filename)
		delete(path, filename)
		exit()

	elif sys.argv[1] == '--encrypt' or sys.argv[1] == '-e':
		key = get_key()

		print("Encrypting your file...")
		encrypt(key, path, filename)
		delete(path, filename)
		exit()

	elif sys.argv[1] == '--encrypt-folder' or sys.argv[1] == '-ef':
		key = get_key()

		print("\nZipping your files...\nPlease wait...")
		archive(path, filename)
		delete(path, filename)
		print("Encrypting files...")
		encrypt(key, path, filename + '.7z')
		delete(path, filename + '.7z')
		exit()

	elif sys.argv[1] == '--decrypt-folder' or sys.argv[1] == '-df':
		key = get_key()

		print("Decrypting your files...")
		decrypt(key, path, filename)
		delete(path, filename)
		print("Unzipping files...")
		extract(path, os.path.splitext(filename)[0]+'.7z')
		delete(path, os.path.splitext(filename)[0]+'.7z')



	else:
		help()
		exit()



if __name__ =='__main__':
	main()