#!/usr/bin/env python3
import argparse
import sys
import os.path
from .packages import blockcipher, pkc, keyexchange, signature
from collections import namedtuple

def banner(description):
    print('''
                          _                        
                         | |                       
     ___ _ __ _   _ _ __ | |_ ___  _ __ __ _ _ __  
    / __| '__| | | | '_ \\| __/ _ \\| '__/ _` | '_ \\ 
   | (__| |  | |_| | |_) | || (_) | | | (_| | | | |
    \\___|_|   \\__, | .__/ \\__\\___/|_|  \\__,_|_| |_|
             __/ | |                             
            |___/|_|                             ''')
    print('    ---------------------', description.upper(),'---------------------')

errors = {
    'keyfile': 'Key file contains invalid data, most likely data is corrupt',
    'decNoKey': 'A key must be provided for decryption operations!'
}

class Cryptoran:
    def __init__(self):
        blockciphers = ['aes', 'des']
        pubkeycrypto = ['rsa', 'elgamal']
        exchange = ['dh']
        signs = ['rsasig']
        allModules = blockciphers + pubkeycrypto + exchange + signs

        parser = argparse.ArgumentParser(
            description='Your Python3 crypto library',
            usage='cryptoran <command> [<args>]'
        )
        parser.add_argument('command', help='cryptographic primitive to be used', choices=allModules)
        args = parser.parse_args(sys.argv[1:2])
        if not hasattr(self, args.command):
            self._displayError('Unrecigonized command ' + args.command, parser)
            print('Unrecognized command:', args.command)
            parser.print_help()
            exit(1)
        banner(args.command)
        getattr(self, args.command)()

    def _openFileRead(self, filename: str):
        fo = None
        try:
            fo = open(filename, 'r')
        except FileNotFoundError:
            self._displayError('File not found: ' + filename)
        return fo

    def _removeExtension(self, filename: str):
        return '.'.join(filename.split('.')[:-1])

    def _openFileWrite(self, filename: str, extension: str):
        filename = filename + '.' + extension
        if os.path.isfile(filename):
            filename = self._removeExtension(filename) + '_1.' + extension
        while os.path.isfile(filename):
            filename = self._removeExtension(filename)
            filename = filename[:-1] + str(int(filename.split('_')[-1]) + 1) + extension
        fo = open(filename, 'w')
        return fo

    def _readRaw(self, filename):
        fo = self._openFileRead(filename)
        document = fo.read()
        fo.close()
        return document
        
    def _readBlocks(self, blocksize: int, filename: str):
        
        fo = self._openFileRead(filename)
        
        blocks = []
        while True:
            chunk = fo.read(blocksize)
            if chunk:
                blocks.append(int(chunk, 16))
            else:
                break
        fo.close()
        return blocks

    def _readSig(self, filename: str):
        # Signature file template:
        # line 1: signature type (i.e. an integer representing signature type)
        # each of the following lines are distinct parameters of the signature
        fo = self._openFileRead(filename)
        def readRSA():
            params = []
            for line in fo:
                if line[0] == '#': # comment line
                    continue
                params.append(int(line, 16))
            return params
        
        sigtypes = { '0': readRSA }
        sigtype = fo.readline()
        if sigtype[-1] == '\n':
            sigtype = sigtype[:-1]
        return sigtypes[sigtype]()

    def _writeSig(self, sigtype: str, sigfilename: str, privatefilename: str,
            publicparams: list, privateparams: list, signature):
        lineWriter = lambda params: [str(hex(x)) + '\n' for x in params]
        sigfo = self._openFileWrite(sigfilename, 'sig')
        privfo = self._openFileWrite(privatefilename, 'key')

        def writeRSA():
            # write signature file
            sigfo.writelines(['0\n', '# -----BEGIN RSA PUBLIC KEY-----\n'])
            sigfo.writelines(lineWriter(publicparams))
            sigfo.write('# -----END RSA PUBLIC KEY-----\n')
            sigfo.write('# -----BEGIN RSA SIGNATURE----\n')
            sigfo.write(hex(signature))
            sigfo.write('\n# -----END RSA SIGNATURE----')
            
            # write key file
            privfo.writelines(['0\n', '# -----BEGIN RSA PUBLIC KEY-----\n'])
            privfo.writelines(lineWriter(publicparams))
            privfo.write('# -----END RSA PUBLIC KEY-----\n')
            privfo.write('# -----BEGIN RSA PRIVATE KEY----\n')
            privfo.writelines(lineWriter(privateparams))
            privfo.write('# -----END RSA PRIVATE KEY-----')
        
        sigtypes = { '0': writeRSA }
        sigtypes[sigtype]()
        sigfo.close()
        privfo.close()
        return sigfo.name, privfo.name

    def _writeKey(self, keytype: str, keyfile: str, key: dict):
        # key is expected to be of format: { 'description': int_value }
        fo = self._openFileWrite(keyfile, 'key')
        for desc in key.keys():
            fo.write('----BEGIN ' + desc + '----\n')
            fo.write(hex(key[desc]))
            fo.write('\n----END ' + desc + '----\n')
        return fo.name

    def _readKey(self, keytype: str, keyfile: str):
        fo = self._openFileRead(keyfile)
        def readAES():
            params = []
            fo.seek(0)
            for line in fo:
                if line[0] == '#':
                    continue
                if line[0] == '-':
                    if 'END' in line:
                        continue
                    nextLine = fo.readline()
                    params.append(int(nextLine, 16))
            return params
        
        keytypes = { '1': readAES }
        keyType = fo.readline()
        if keyType[-1] == '\n':
            keyType = keyType[:-1]
        return keytypes[keytype]()

    def _writeBlocks(self, blocks: list, filename: str):
        fo = self._openFileWrite(filename, 'enc')
        for block in blocks:
            fo.write(hex(block)[2:])
        fo.close()
        return fo.name

    def _writeRaw(self, document: str, filename: str):
        fo = self._openFileWrite(filename, 'dec')
        fo.write(document)
        fo.close()
        return fo.name

    def _displayError(self, error, command = None):
        print('Error:', error)
        if command:
            print('cryptoran ' + command + ' -h for more info')
        exit(1)

    def _blockcipherOperation(self, commandName: str, cipherClass: blockcipher.BlockCipher):
        parser = argparse.ArgumentParser(
            description=commandName,
            usage='cryptoran ' + commandName + ' mode file [args]'
        )
        parser.add_argument('mode', help='mode of operation', choices=['cbc', 'ecb'])
        parser.add_argument('file', help='input file')
        parser.add_argument('-k', help='key file')
        parser.add_argument('-iv', help='initial vector for CBC mode')
        parser.add_argument('-e', help='encrypt', action='store_true')
        parser.add_argument('-d', help='decrypt', action='store_true')
        parser.add_argument('-ok', help='output key file')
        parser.add_argument('-o', help='output file name (for encrypted or plaintext file)')

        args = parser.parse_args(sys.argv[2:])

        # read the keyfile if existent
        key = None
        iv = None
        #try:
        if args.k:
            key, iv = self._readKey('1', args.k)
        #except:
            #self._displayError(errors['keyfile'], 'aes')
        
        if args.d:
            if not args.k:
                self._displayError(errors['decNoKey'], commandName)
            if args.mode == 'cbc' and not iv:
                self._displayError(errors['keyfile'], commandName)
        elif not args.e:
            self._displayError('Encryption or decryption operation not specified!', commandName)
            key, iv = self._readKey('aes', args.k)

        # set the output files
        keyfile = args.ok if args.ok else args.file
        outputFile = args.o if args.o else args.file

        # encrypt / decrypt
        try:
            cipher = cipherClass(args.mode, key, iv)
            if args.e: # encryption
                inData = self._readRaw(args.file)
                if inData == '':
                    self._displayError('Input file is empty', 'aes')
                encOutput = self._writeBlocks(cipher.encrypt(inData), outputFile)
                print('Encryption result written to', encOutput)
                keyOutput = self._writeKey('1', keyfile, cipher.getKeys())
                print('Key stored in', keyOutput)
            else: # decryption
                inData = self._readBlocks(32, args.file) #error!
                if inData == []:
                    self._displayError('Input file is empty', 'aes')
                plainOutput = self._writeRaw((cipher.decrypt(inData)), outputFile)
                print('Output written to', plainOutput)
        except FileNotFoundError:
            self._displayError('Cannot open file: ' + args.file, commandName) 

    def aes(self):
        self._blockcipherOperation('aes', blockcipher.AES)

    def des(self):
        self._blockcipherOperation('des', blockcipher.DES)

    def rsasig(self):
        # 1 - parsing command line arguments
        parser = argparse.ArgumentParser(
            description='RSA signature',
            usage='cryptoran rsasig file [args]'
        )

        parser.add_argument('file', help='input file')
        parser.add_argument('-s', '--sign', help='sign the input file', action='store_true')
        parser.add_argument('-v', '--verify', help='verify the signature', action='store_true')
        parser.add_argument('-osig', help='signature output file name')
        parser.add_argument('-ok', help='key output file name')
        parser.add_argument('-sig', help='name of signature file')
        parser.add_argument('-k', help='private key file')
        args = parser.parse_args(sys.argv[2:])

        # 2 - read the signature and key files if existent
        if not args.verify and not args.sign:
            self._displayError('No operation provided, sign or verify must be given')

        document = self._readRaw(args.file)
        encExp, modulus, decExp, sigdata = None, None, None, None
        if args.sig: # 2.1 - read the signature file
            try:
                encExp, modulus, sigdata = self._readSig(args.sig)
            except ValueError:
                self._displayError(errors['keyfile'])

            if any([encExp, modulus, sigdata]) and not all([encExp, modulus, sigdata]):
                self._displayError('Invalid signature file, parameters missing!')

        if args.k: # 2.2 - read the key file
            try:
                encExp, modulus, decExp = self._readSig(args.k)
            except:
                self._displayError('Invalid hexadecimal numbers provided within the signature file!')
            if not decExp:
                self._displayError('Invalid key file!')

        # 3 - sign / verify the document
        signer = signature.RSAsig(encExp, decExp, modulus, 2048) 
        if args.verify: # 3.1 - verification
            if not args.sig:
                self._displayError('A signature file must be provided for verification')
                
            if signer.verify(document, sigdata):
                print('Signature is valid, verification resulted in success!')
            else:
                print('Signature does not match, verification resulted in failure!')
        else: # 3.2 - signing
            if not all([encExp, modulus, decExp]):
                print('Generating 1024 bit RSA keys...')
                keydata = signer.generateKeys()
                encExp, modulus, decExp = keydata[0][0], keydata[0][1], keydata[1][0]
            
            sigdata = signer.sign(document)
            sigOutFile = args.osig if args.osig else args.file
            keyOutFile = args.ok if args.ok else args.file
            sigfilename, keyfilename = self._writeSig('0', sigOutFile, keyOutFile, [encExp, modulus], [decExp], sigdata)
            print('Signature written to', sigfilename, 'and key written to', keyfilename)

def main():
    # main routine
    Cryptoran()
    


if __name__ == '__main__':
    main()