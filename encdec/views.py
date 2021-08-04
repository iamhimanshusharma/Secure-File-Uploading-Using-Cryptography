from django.shortcuts import render
from django.http import HttpResponse
from .models import Product
from fsplit.filesplit import Filesplit
from .algo import Encryptor
import os
import shutil
from hashlib import md5, sha256
from datetime import datetime


# def split_cb(f, s):
#     print("file: {0}, size: {1}".format(f, s))


# Create your views here.
def index(request):
    folders = []
    products = Product.objects.all()
    params = {'len':len(products), 'product':products}
    return render(request, 'encdec/index.html', params)

def uploads(request):
    now = datetime.now()
    timestamp = now.strftime("%d%m%Y%H%M%S")
    fs = Filesplit()
    if request.method == 'POST':
        files = request.FILES['files']
        file_type = request.POST.get('file_type')
        real_key = request.POST.get('keyed')
        key_mode = request.POST.get('key')

        if key_mode == 'dflt':
            key = b'[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e'
            fernet_key = b'skZ9uZYBJXOOnbkZeCA2vMeoECm_Z0bVRDKS6ofxOrc='
        elif key_mode == 'kinp':
            key = bytes(md5(real_key.encode("ascii")).hexdigest(), 'utf-8')
            f_key = sha256(real_key.encode('ascii')).hexdigest()
            fernet_key = f_key[:44]
        
        hello = Encryptor(key)
        plaintext = files.read()
        enc = hello.encrypt(plaintext, key)
        folder_name = str(files)[:-4]+"_"+timestamp
        path = 'media/encdec/files/'+folder_name
        os.mkdir(path)
        with open(path+ "/"+str(files) + ".enc", 'wb') as fo:
            fo.write(enc)
        datt = Product(product_folder=folder_name,product_type=file_type, key_type=key_mode, product_name=str(files)+".enc")
        datt.save()
        fs.split(file=path+ '/'+str(files) + '.enc', split_size=100, output_dir=path+ '/')
        os.remove(path+'/'+str(files)+".enc")
        remover_file = hello.getAllFiles(path)
        hello.encrypt_all_files(path)
        print(remover_file)
        for f in remover_file:
            os.remove(f)
        thank=True
        params = {'thank':thank}
        return render(request, 'encdec/upload.html', params)
    return render(request, 'encdec/upload.html')

def dec(request):
    fs = Filesplit()
    files = request.GET.get('product_n')
    folder = request.GET.get('product_f')

    if request.GET.get('keyed'):
        real_key = request.GET.get('keyed')
        key = bytes(md5(real_key.encode("ascii")).hexdigest(), 'utf-8')
    else:
        key = b'[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e'
    
    hello = Encryptor(key)
    file_path = 'media/encdec/files/'+folder+"/"
    hello.decrypt_all_files(file_path)
    fs.merge(file_path)
    with open(file_path + files, 'rb') as fo:
        ciphertext = fo.read()
    dec = hello.decrypt(ciphertext, key)
    with open(file_path + files[:-4], 'wb') as fo:
        fo.write(dec)
    removing_file = hello.getAllFiles(file_path)
    for f in removing_file:
        if f == file_path + '\\' + files[:-4]:
            continue
        os.remove(f)
    datt = Product.objects.filter(product_folder=folder).update(product_type="TXT", product_name=files[:-4])
    # datt.save()
    params = {'folder':folder ,'file':files[:-4]}
    return render(request, 'encdec/download.html', params)


def again_uploads(request):
    fs = Filesplit()
    if request.method == 'POST':
        # files = request.FILES['files']
        file_type = request.POST.get('file_type')
        real_key = request.POST.get('keyed')
        key_mode = request.POST.get('key')
        folder_path = request.POST.get('pro_folder')
        folder_file = request.POST.get('pro_file')
        folder_name = request.POST.get('folder_name')

        if key_mode == 'dflt':
            key = b'[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e'
            fernet_key = b'skZ9uZYBJXOOnbkZeCA2vMeoECm_Z0bVRDKS6ofxOrc='
        elif key_mode == 'kinp':
            key = bytes(md5(real_key.encode("ascii")).hexdigest(), 'utf-8')
            f_key = sha256(real_key.encode('ascii')).hexdigest()
            fernet_key = f_key[:44]
        
        hello = Encryptor(key)
        print(folder_path)
        with open(folder_path + "/"+ folder_file, 'rb') as files:
            plaintext = files.read()
        enc = hello.encrypt(plaintext, key)
        with open(folder_path + "/"+ folder_file + ".enc", 'wb') as fo:
            fo.write(enc)
        datt = Product.objects.get(product_folder=folder_name)
        datt.product_type= file_type
        datt.key_type=key_mode
        datt.product_name=str(folder_file)+".enc"
        datt.save()
        fs.split(file=folder_path + "/"+ folder_file + '.enc', split_size=100, output_dir=folder_path+ '/')
        os.remove(folder_path + "/"+ folder_file+".enc")
        remover_file = hello.getAllFiles(folder_path)
        hello.encrypt_all_files(folder_path)
        os.remove(folder_path + "/"+folder_file+".enc")
        print(remover_file)

        for f in remover_file:
            os.remove(f)
        thank=True
        params = {'thank':thank}
        return render(request, 'encdec/upload.html', params)
    return render(request, 'encdec/upload.html')

def delete_data(request):
    fs = Filesplit()
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        folder = request.POST.get('pro_folder')

        datt = Product.objects.get(product_folder=folder_name)
        datt.delete()

        shutil.rmtree(str(folder))
        
        thank=True
        params = {'thank':thank}
        return render(request, 'encdec/delete.html', params)
    return render(request, 'encdec/delete.html')
