from django.shortcuts import render
from django.http import HttpResponse
from .models import Product
from fsplit.filesplit import Filesplit
from .algo import Encryptor
import os
import shutil
from hashlib import md5, sha256
from datetime import datetime

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

        aes = []
        fernet = []
        des = []
        media_list = ['jpeg', '.jpg', '.png', '.gif', '.mkv', '.mp4']

        if key_mode == 'dflt':
            key = b'[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e'
            fernet_key = b'skZ9uZYBJXOOnbkZeCA2vMeoECm_Z0bVRDKS6ofxOrc='
            des_key = b'fYHBWInR'
        elif key_mode == 'kinp':
            key = bytes(md5(real_key.encode("ascii")).hexdigest(), 'utf-8')
            f_key = sha256(real_key.encode('ascii')).hexdigest()
            fer_key = f_key[:43]+"="
            fernet_key = bytes(fer_key, 'utf-8')
            des_key = bytes(f_key[:8], 'utf-8')
     
        hello = Encryptor(key)
        hello_f = Encryptor(fernet_key)
        hello_d = Encryptor(des_key)

        if str(files)[-4:] in media_list:#== 'jpeg' or str(files)[-3:] == 'png' or str(files)[-3:] == 'jpg' or str(files)[-3:] == 'ico'  or str(files)[-3:] == 'mp4':
            plaintext = files.read()
            folder_name = str(files)[:-4]+"_"+timestamp
            path = 'media/encdec/files/'+folder_name
            os.mkdir(path)
            with open(path+ "/"+str(files), 'wb') as fo:
                fo.write(plaintext)
            datt = Product(product_folder=folder_name,product_type=file_type, key_type=key_mode, product_name=str(files)+".enc")
            datt.save()
            # fs.split(file=path+ '/'+str(files), split_size=1000, output_dir=path+ '/')
            # remover_file = hello.getAllFiles(path)

            with open(path +"/"+str(files), 'rb') as fo:
                plaintext = fo.read()
            enc = hello.encrypt(plaintext, key)
            with open(path +"/"+str(files) + ".enc", 'wb') as fo:
                fo.write(enc)
            os.remove(path +"/"+str(files))

        else:
            plaintext = files.read()
            folder_name = str(files)[:-4]+"_"+timestamp
            path = 'media/encdec/files/'+folder_name
            os.mkdir(path)
            with open(path+ "/"+str(files), 'wb') as fo:
                fo.write(plaintext)
            datt = Product(product_folder=folder_name,product_type=file_type, key_type=key_mode, product_name=str(files)+".enc")
            datt.save()
            fs.split(file=path+ '/'+str(files), split_size=1000, output_dir=path+ '/')
            remover_file = hello.getAllFiles(path)

            for i in range(0, len(remover_file), 3):
                aes.append(remover_file[i])

            for j in range(1, len(remover_file), 3):
                fernet.append(remover_file[j])

            for x in range(2, len(remover_file), 3):
                des.append(remover_file[x])

            if len(aes)>0:
                for k in aes:
                    with open(k, 'rb') as fo:
                        plaintext = fo.read()
                    enc = hello.encrypt(plaintext, key)
                    with open(k + ".aenc", 'wb') as fo:
                        fo.write(enc)
                    os.remove(k)

            if len(fernet)>0:
                for l in fernet:
                    with open(l, 'rb') as fo:
                        plaintext = fo.read()
                    enc = hello_f.fernet_encrypt(plaintext, fernet_key)
                    with open(l + ".fenc", 'wb') as fo:
                        fo.write(enc)
                    os.remove(l)

            if len(des)>0:
                for y in des:
                    with open(y, 'rb') as fo:
                        plaintext = fo.read()
                    enc = hello_d.des_encrypt(plaintext, des_key)
                    with open(y + ".denc", 'wb') as fo:
                        fo.write(enc)
                    os.remove(y)

        thank=True
        params = {'thank':thank}
        return render(request, 'encdec/upload.html', params)
    return render(request, 'encdec/upload.html')

def dec(request):
    fs = Filesplit()
    files = request.GET.get('product_n')
    folder = request.GET.get('product_f')
    aes = []
    fernet = []
    des = []
    media_list = ['jpeg.enc', '.jpg.enc', '.png.enc', '.gif.enc', '.mkv.enc', '.mp4.enc']

    if request.GET.get('keyed'):
        real_key = request.GET.get('keyed')
        key = bytes(md5(real_key.encode("ascii")).hexdigest(), 'utf-8')
        f_key = sha256(real_key.encode('ascii')).hexdigest()
        fer_key = f_key[:43]+"="
        fernet_key = bytes(fer_key, 'utf-8')
        des_key = bytes(f_key[:8], 'utf-8')
    else:
        key = b'[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e'
        fernet_key = b'skZ9uZYBJXOOnbkZeCA2vMeoECm_Z0bVRDKS6ofxOrc='
        des_key = b'fYHBWInR'
        

    hello = Encryptor(key)
    hello_f = Encryptor(fernet_key)
    hello_d = Encryptor(des_key)

    file_path = 'media/encdec/files/'+folder+"/"
    all_files = os.listdir(file_path)

    if str(files)[-8:] in media_list:#== ".jpeg.enc" or str(files)[-8:] == ".png.enc" or str(files)[-8:] == ".jpg.enc"  or str(files)[-8:] == ".ico.enc"  or str(files)[-8:] == ".mp4.enc":
        for k in all_files:
            with open(file_path + k, 'rb') as fo:
                enctext = fo.read()
            dec = hello.decrypt(enctext, key)
            with open(file_path + k[:-4], 'wb') as fo:
                fo.write(dec)
            os.remove(file_path + k)

    else: 
        for i in all_files:
            if i[-5:] == ".aenc":
                aes.append(i)
            elif i[-5:] == ".fenc":
                fernet.append(i)
            else:
                des.append(i)
        
        for k in aes:
            with open(file_path + k, 'rb') as fo:
                enctext = fo.read()
            dec = hello.decrypt(enctext, key)
            with open(file_path + k[:-5], 'wb') as fo:
                fo.write(dec)
            os.remove(file_path + k)

        for l in fernet:
            with open(file_path + l, 'rb') as fo:
                enctext = fo.read()
            plaintext = hello_f.fernet_decrypt(enctext, fernet_key)
            with open(file_path + l[:-5], 'wb') as fo:
                fo.write(plaintext)
            os.remove(file_path + l)

        for y in des:
            with open(file_path + y, 'rb') as fo:
                enctext = fo.read()
            plaintext = hello_d.des_decrypt(enctext, des_key)
            with open(file_path + y[:-5], 'wb') as fo:
                fo.write(plaintext)
            os.remove(file_path + y)

        fs.merge(file_path)
        removing_file = hello.getAllFiles(file_path)
        for f in removing_file:
            if f == file_path + '\\' + files[:-4]:
                continue
            os.remove(f)
    datt = Product.objects.filter(product_folder=folder).update(product_type="TXT", product_name=files[:-4])
    params = {'folder':folder ,'file':files[:-4]}
    return render(request, 'encdec/download.html', params)


def again_uploads(request):
    fs = Filesplit()
    if request.method == 'POST':
        file_type = request.POST.get('file_type')
        real_key = request.POST.get('keyed')
        key_mode = request.POST.get('key')
        folder_path = request.POST.get('pro_folder')
        folder_file = request.POST.get('pro_file')
        folder_name = request.POST.get('folder_name')

        aes = []
        fernet = []
        des = []
        media_list = ['jpeg', '.jpg', '.png', '.gif', '.mkv', '.mp4']


        if key_mode == 'dflt':
            key = b'[EX\xc8\xd5\xbfI{\xa2$\x05(\xd5\x18\xbf\xc0\x85)\x10nc\x94\x02)j\xdf\xcb\xc4\x94\x9d(\x9e'
            fernet_key = b'skZ9uZYBJXOOnbkZeCA2vMeoECm_Z0bVRDKS6ofxOrc='
            des_key = b'fYHBWInR'
        elif key_mode == 'kinp':
            key = bytes(md5(real_key.encode("ascii")).hexdigest(), 'utf-8')
            f_key = sha256(real_key.encode('ascii')).hexdigest()
            fer_key = f_key[:43]+"="
            fernet_key = bytes(fer_key, 'utf-8')
            des_key = bytes(f_key[:8], 'utf-8')
        
        hello = Encryptor(key)
        hello_f  = Encryptor(fernet_key)
        hello_d = Encryptor(des_key)

        if folder_file[-4:] in media_list:#=='.jpeg' or folder_file[-4:] == '.png' or folder_file[-4:] == '.jpg'  or folder_file[-4:] == '.ico' or folder_file[-4] == '.mp4':
            with open(folder_path+"/"+folder_file, 'rb') as fo:
                plaintext = fo.read()
            enc = hello.encrypt(plaintext, key)
            with open(folder_path+"/"+folder_file + ".enc", 'wb') as fo:
                fo.write(enc)
            os.remove(folder_path+"/"+folder_file)
        else:
            fs.split(file=folder_path + "/"+ folder_file, split_size=1000, output_dir=folder_path+ '/')
            remover_file = hello.getAllFiles(folder_path)
            for i in range(0, len(remover_file), 3):
                aes.append(remover_file[i])

            for j in range(1, len(remover_file), 3):
                fernet.append(remover_file[j])

            for x in range(2, len(remover_file), 3):
                des.append(remover_file[x]) 

            for k in aes:
                with open(k, 'rb') as fo:
                    plaintext = fo.read()
                enc = hello.encrypt(plaintext, key)
                with open(k + ".aenc", 'wb') as fo:
                    fo.write(enc)
                os.remove(k)

            for l in fernet:
                with open(l, 'rb') as fo:
                    plaintext = fo.read()
                enc = hello_f.fernet_encrypt(plaintext, fernet_key)
                with open(l + ".fenc", 'wb') as fo:
                    fo.write(enc)
                os.remove(l)

            for y in des:
                with open(y, 'rb') as fo:
                    plaintext = fo.read()
                enc = hello_d.des_encrypt(plaintext, des_key)
                with open(y + ".denc", 'wb') as fo:
                    fo.write(enc)
                os.remove(y)

        datt = Product.objects.get(product_folder=folder_name)
        datt.product_type= file_type
        datt.key_type=key_mode
        datt.product_name=str(folder_file)+".enc"
        datt.save()
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
