all: mythread.c 
	gcc -c mythread.c -o mythread.o
	ar rcs mythread.a mythread.o	