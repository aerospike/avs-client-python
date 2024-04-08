import urllib.request
import tarfile

urllib.request.urlretrieve(
    "ftp://ftp.irisa.fr/local/texmex/corpus/siftsmall.tar.gz", "siftsmall.tar.gz"
)


# open file
file = tarfile.open("siftsmall.tar.gz")

# extracting file
file.extractall("./")

file.close()
