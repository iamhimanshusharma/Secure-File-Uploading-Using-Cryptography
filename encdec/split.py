from fsplit.filesplit import Filesplit

fs = Filesplit()

# def split_cb(f, s):
#     print("file: {0}, size: {1}".format(f, s))

fs.split(file="test.txt", split_size=100, output_dir="templates/")

# def merge_cb(f, s):
#     print("file: {0}, size: {1}".format(f, s))

fs.merge(input_dir="splitted/", callback=merge_cb)