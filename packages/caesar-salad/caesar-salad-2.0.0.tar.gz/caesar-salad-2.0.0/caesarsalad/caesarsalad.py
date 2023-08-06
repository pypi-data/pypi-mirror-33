#!/usr/bin/env python3
"""
Command Line tool to crack ROT-n Caesar Ciphers given a sample of text
Released under a GNU GPLv3 licence
Created by Amith KK (http://amithkk.github.io)
"""
import os
from operator import itemgetter
from collections import OrderedDict
import argparse



words = [line.rstrip('\n').lower() for line in open(os.path.join(os.path.dirname(__file__), 'words.txt'))]


def rot_gen(n):
    from string import ascii_lowercase as l, ascii_uppercase as u
    lookup = str.maketrans(l + u, l[n:] + l[:n] + u[n:] + u[:n])
    return lambda x: x.translate(lookup)


def isValidWord(word):
    return word.lower() in words

def main():
    parser = argparse.ArgumentParser(
        description='Cracks ROT-n Caesar Ciphers by a brute force attack on a sample of text\nWritten '
                    'by Amith KK, [https://github.com/amithkk/caesar-salad]',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-d', '--decode-only', dest='decode_mode', action='store_const',
                        const=True, default=False,
                        help='Only output best guess of decoded string')
    parser.add_argument('ciphertext', metavar='STR', type=str, nargs='?',
                        help='ROT-encoded string to decipher')
    parser.add_argument('-w', '--which-rot', dest='find_encoding', action='store_const',
                        const=True, default=False,
                        help='Find best guess of type of encoding')

    args = parser.parse_args()

    if not args.ciphertext:
        s = input("Enter ROT-N Ciphertext: ")
    else:
        s = args.ciphertext
    confidence_list = {}

    # generate rot list from 1 to 25
    for i in range(1, 25):
        print("Calculating ROT", i, end='\r')
        valid_wordcount = 0
        wordlist = list(filter(lambda x: len(x) > 2, rot_gen(-i)(s).split(" ")))
        # print(wordlist)
        for word in wordlist:
            valid_wordcount += isValidWord(word)
        confidence_list[i] = valid_wordcount / len(wordlist)

    confidence_list = OrderedDict(sorted(confidence_list.items(), key=itemgetter(1), reverse=True))

    print(" " * 18, end='\r')

    if args.find_encoding:
        cipher, confidence = next(iter(confidence_list.items()))
        print("ROT", cipher)
        exit(0)

    if args.decode_mode:
        cipher, confidence = next(iter(confidence_list.items()))
        print(rot_gen(-cipher)(s))
        exit(0)

    for cipher, confidence in confidence_list.items():
        if confidence == 1:
            print("ROT%d: Perfect Match [%.1f]:\n%s\n" % (cipher, round(confidence * 100, 1), rot_gen(-cipher)(s)))
        elif confidence > 0:
            print("ROT%d: Confidence[%.1f]:\n%s\n" % (cipher, round(confidence * 100, 1), rot_gen(-cipher)(s)))


if __name__ == '__main__':
    main()