gcc -c -fPIC WeDoLinux.c -o WeDoPlugin.o
gcc -shared -Wl,-soname,so.WeDoPlugin -o so.WeDoPlugin 
