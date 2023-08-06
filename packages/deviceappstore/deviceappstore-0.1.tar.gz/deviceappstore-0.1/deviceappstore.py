#!/usr/bin/env python
import json
import urllib2
import tempfile
import sys
import os
import subprocess
import platform
import hashlib
import gzip
import zipfile
import commands

#p = subprocess.Popen(['ls', '-lah', '/dev/cu*'], stdout=subprocess.PIPE, 
#                                                 stderr=subprocess.PIPE)
#out, err = p.communicate()
#print out

#print subprocess.check_output(['ls', '-lah', '/dev/cu*'])

# Import esptool
try:
    from shutil import which
except ImportError:
    from distutils.spawn import find_executable as which


bindir = os.path.dirname(which('esptool.py'))
sys.path.append(bindir)  # after this line, esptool becomes importable

import esptool

def eprint(txt):
  sys.stderr.write('\x1b[1;31m' + txt.strip() + '\x1b[0m\n')

def sprint(txt):
  sys.stdout.write('\x1b[1;32m' + txt.strip() + '\x1b[0m\n')

def checksum(fname):
  hash_md5 = hashlib.md5()
  with open(fname, "rb") as f:
    for chunk in iter(lambda: f.read(4096), b""):
       hash_md5.update(chunk)
  return hash_md5.hexdigest()

def download(info, retry=True):
  # Download the file first
  new_file, filename = tempfile.mkstemp()
  url = info['url']
  request = urllib2.Request(url, headers={'Accept-Encoding': 'gzip'})
  u = urllib2.urlopen(request)
  meta = u.info()
  file_name = url.split('/')[-1]
  #u = urllib2.urlopen(url)
  #f = open(file_name, 'wb')
  file_size = int(meta.getheaders("Content-Length")[0])
  # TODO: Check if it's zip, for now we just accept zip
  # contentType = meta.getheaders("Content-Type")[0]
  print "Downloading: %s Bytes: %s" % (file_name, file_size)
 
  file_size_dl = 0
  block_sz = 8192
  while True:
    buffer = u.read(block_sz)
    if not buffer:
      break

    file_size_dl += len(buffer)
    os.write(new_file, buffer)
    status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
    status = status + chr(8)*(len(status)+1)
    print status,

  os.close(new_file)

  '''md5 = checksum(new_file)
  if md5 != info.checksum:
    print('Downloaded file is corrupted try to download the file again')
    if retry:
      # We just retry one time
      return download(info, False)'''
  #_, raw = tempfile.mkstemp()
  #with gzip.open(filename, 'rb') as f_in, open(raw, 'wb') as f_out:
  #  f_out.write(f_in.read())
  
  zip_ref = zipfile.ZipFile(filename, 'r')
  zip_ref.extractall(filename + '_files')
  zip_ref.close()

  return filename + '_files/rom.bin'

if len(sys.argv) != 2:
  print('Usage: --version | [APP PATH]')
elif sys.argv[1] == '--version':
  print('Version 0.1')
else:
  # Get meta data
  # TODO: Handle 404
  appPath = sys.argv[1]
  try:
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'deviceappstore-installer/0.1'), ('Accept-Encoding', 'xz')]
    info = json.load(urllib2.urlopen('http://deviceappstore.com/app/' + appPath))
    # {
    #   type: 'esp',
    #   files: {
    #     rom: {
    #       url: '',
    #       checksum: ''
    #     },
    #     spiffs: {
    #       url: '',
    #       checksum: ''
    #     }
    #   }
    # }
  except urllib2.HTTPError, e:
    if e.code == 404:
      eprint("The application with ID '" + appPath + "' did not find. Please check the app code and try again")
    else:
      print e.code
      print e.msg
      print e.headers
      print e.fp.read()
    exit()
  except urllib2.URLError, e:
    print('Error to connect to the server, check the internet connection or update the app')
    exit()

  # print info['type']
  # TODO: Get the type of setup tools from device param
  type = 'esp8266'

  if type == 'esp8266':
    # Find the port
    platformName = platform.system()
    if platformName == 'Darwin' or platformName == 'Linux':
      output = subprocess.check_output(['ls', '-lah', '/dev/'])
      if 'ttyUSB0' in output:
        port = '/dev/ttyUSB0'
      elif 'tty.SLAB_USBtoUART' in output:
        port = '/dev/tty.SLAB_USBtoUART'
      else:
        eprint('Could not find the device, are you sure the device is connected?')
        exit(1)
    else:
      eprint('Could not detect your OS')
      exit(1)

    version = info['versions'][0]

    # Download the ROM
    rom_info = version['rom']
    rom = download(rom_info)

    if 'spiffs' in version:
      spiffs = download(version['spiffs'])

    params = rom_info['params'].split()
    params.insert(0, '')
    params.insert(1, '--port')
    params.insert(2, port)
    params.append(rom)
    sys.argv[:] = params
    esptool.main()

    if 'spiffs' in locals():
      params = spiffs['params'].split()
      params.insert(0, '')
      params.append(spiffs)
      sys.argv[:] = params
      esptool.main()
    
    sprint("Congradulation, it's done!")
  else:
    eprint('The application type does not support, please update the installer app')