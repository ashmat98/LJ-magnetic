#!/usr/bin/env python3
import hashlib
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename')
    parser.add_argument('machine')
    args = parser.parse_args()
    m = hashlib.md5(open(args.filename, 'rb').read() + str.encode(args.machine))
    print(m.hexdigest()[::2])
