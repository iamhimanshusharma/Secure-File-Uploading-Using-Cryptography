from django.shortcuts import render
from django.http import HttpResponse
from .models import Product
from fsplit.filesplit import Filesplit
from .algo import Encryptor
import os
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
    key = b'[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e'
    hello = Encryptor(key)
    now = datetime.now()
    timestamp = now.strftime("%d%m%Y%H%M%S")
    fs = Filesplit()
    if request.method == 'POST':
        files = request.FILES['files']
        file_type = request.POST.get('file_type')
        plaintext = files.read()
        enc = hello.encrypt(plaintext, key)
        folder_name = str(files)[:-4]+"_"+timestamp
        path = 'media/encdec/files/'+folder_name
        os.mkdir(path)
        with open(path+ "/"+str(files) + ".enc", 'wb') as fo:
            fo.write(enc)
        datt = Product(product_folder=folder_name,product_type=file_type, product_name=str(files)+".enc")
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
    key = b'[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e'
    hello = Encryptor(key)
    fs = Filesplit()
    files = request.GET.get('product_n')
    folder = request.GET.get('product_f')
    file_path = 'media/encdec/files/'+folder+"/"
    hello.decrypt_all_files(file_path)
    fs.merge(file_path)
    with open(file_path + files, 'rb') as fo:
        ciphertext = fo.read()
    dec = hello.decrypt(ciphertext, key)
    with open(file_path + files[:-4], 'wb') as fo:
        fo.write(dec)
    removing_file = hello.getAllFiles(file_path)
    print(removing_file)
    for f in removing_file:
        if f == file_path + '\\' + files[:-4]:
            continue
        os.remove(f)
    datt = Product.objects.filter(product_folder=folder).update(product_type="TXT", product_name=files[:-4])
    # datt.save()
    params = {'folder':folder ,'file':files[:-4]}
    return render(request, 'encdec/download.html', params)