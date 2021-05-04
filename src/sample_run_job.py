import tarfile

f_in = open("sample-output-file.txt", "w")
f_in.write("some results")
f_in.close()
tf = tarfile.open("tarfile-of-results.tar.gz", "x:gz")
tf.add("sample-output-file.txt")
tf.close()
# kojo@ftplus-dev.bu.edu
# ftsubmit@ftplus-dev
