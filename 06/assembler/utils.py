def dec2bin(decimal, num_bits):
    binary = bin(decimal)[2:]
    if (len(binary) > num_bits):
        start_bit = len(binary) - num_bits
        binary = binary[start_bit:]
    elif (len(binary) < num_bits):
        binary = binary.zfill(num_bits)
    return binary