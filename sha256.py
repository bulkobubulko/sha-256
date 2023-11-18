import os
import math
from itertools import count, islice
import struct

# Functions

def right_shift(x, n):
    return x >> n

def right_rotate(x, n, size=32):
    return (x >> n) | (x << size - n) & (2**size - 1)

def sigma_0(x):
    return right_rotate(x, 7) ^ right_rotate(x, 18) ^ right_shift(x, 3)

def sigma_1(x):
    return right_rotate(x, 17) ^ right_rotate(x, 19) ^ right_shift(x, 10)

def capital_sigma_0(x):
    return right_rotate(x, 2) ^ right_rotate(x, 13) ^ right_rotate(x, 22)

def capital_sigma_1(x):
    return right_rotate(x, 6) ^ right_rotate(x, 11) ^ right_rotate(x, 25)

def choice(x, y, z):
    return (x & y) ^ (~x & z)

def majority(x, y, z):
    return (x & y) ^ (x & z) ^ (y & z)

# Additional functions

def b2i(b):
    """Convert bytes to integer"""
    return struct.unpack('>I', b)[0]

def i2b(i):
    """Convert integer to bytes"""
    return struct.pack('>I', i)

def is_prime(n):
    return not any(f for f in range(2,int(math.sqrt(n))+1) if n%f == 0)

def first_n_primes(n):
    return islice(filter(is_prime, count(start=2)), n)

def frac_bin(x, n = 32):
    return int(((x - math.floor(x)) * (2 ** n)) % (2 ** n))

def pad(m):
    """Pad message to 512 bits"""
    m_len = len(m) * 8
    m.append(0x80)
    
    while (len(m * 8)) % 512 != 448:
        m.append(0x00)

    m.extend(struct.pack('>Q', m_len))
    
    return m
    
def sha256(input_bytes):
    """SHA-256 hash algorithm implementation
    
    Args:
        input_bytes(bytearray): Input bytes (text or file) to be hashed
        
    Returns:
        output(str): SHA-256 hash (hexadecimal) of input
    """
    try:
        message = pad(input_bytes)
        blocks = [message[i:i+64] for i in range(0, len(message), 64)]
        
        h = [frac_bin(p ** (1/2.0)) for p in first_n_primes(8)]
        k = [frac_bin(p ** (1/3.0)) for p in first_n_primes(64)]
        
        initial_h = h.copy()
        
        for block in blocks:
            # Message schedule
            words = [struct.pack('>I', b2i(block[i:i+4])) for i in range(0, len(block), 4)]

            for i in range(16, 64):
                word = i2b((sigma_1(b2i(words[i-2])) + b2i(words[i-7]) + sigma_0(b2i(words[i-15])) + b2i(words[i-16])) % 2**32)
                words.append(word)
                
            # Compression function
            for i in range(len(words)):    
                t1 = capital_sigma_1(h[4]) + choice(h[4], h[5], h[6]) + h[7] + k[i] + b2i(words[i])
                t2 = capital_sigma_0(h[0]) + majority(h[0], h[1], h[2])
                
                for j in range(7, 0, -1):
                    h[j] = h[j-1]

                h[0] = (t1 + t2)  % 2**32
                h[4] = (h[4] + t1) % 2**32
                
            for i in range(len(h)):
                h[i] = (initial_h[i] + h[i]) % 2**32
                
            initial_h = h.copy()
                
            output = ''.join([f"{i:08x}" for i in h])
            
    except Exception as e:
        raise ValueError(f"Error in SHA-256 algorithm: {e}")
        
    return output

def get_user_input():
    try:
        return input("Enter 'text:' followed by the text or 'file:' followed by the file path: \n")
    except EOFError:
        raise ValueError("Unexpected end of input. Please try again.")

def parse_user_input(user_input):
    try:
        if user_input.startswith('file:'):
            file_path = user_input[len('file:'):].strip()
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as file:
                    input_bytes = bytearray(file.read())
                return input_bytes, 'file'
            else:
                raise FileNotFoundError(f"File not found: {file_path}")
        elif user_input.startswith('text:'):
            text_input = user_input[len('text:'):].strip()
            return bytearray(text_input.encode('utf-8')), 'text'
        else:
            raise ValueError("Invalid input format. Please start with 'file:' or 'text:'.")
    except ValueError as ve:
        raise ve
    except FileNotFoundError as fnfe:
        raise fnfe
    except Exception as e:
        raise ValueError(f"Error: {e}")

def main():
    while True:
        user_input = input("\nEnter 'text: <your_text>' or 'file: <file_path>'. Type 'exit' to quit: \n").strip()

        if user_input.lower() == 'exit':
            break

        try:
            input_bytes, input_type = parse_user_input(user_input)
            result = sha256(input_bytes)
            print(f"SHA-256 hash of {input_type} is: {result}")

        except ValueError as ve:
            print(f"Error: {ve}")
        except FileNotFoundError as fnfe:
            print(f"Error: {fnfe}")

if __name__ == '__main__':
    main()