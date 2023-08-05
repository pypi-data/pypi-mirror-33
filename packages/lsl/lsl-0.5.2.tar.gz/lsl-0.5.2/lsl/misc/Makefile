CFLAGS = $(shell python-config --includes) $(shell python -c "import numpy; print '-I' + numpy.__path__[0] + '/core/include/numpy/'")

_basic.so: basic.o
	gcc $(CFLAGS) -o _basic.so basic.o -lm -shared -lcblas -fopenmp

basic.o:
	gcc -c $(CFLAGS) -fPIC -o basic.o basic.c -funroll-loops -O3 -fopenmp


_fir.so: fir.o
	gcc $(CFLAGS) -o _fir.so fir.o -lm -shared -lcblas -fopenmp

fir.o:
	gcc -c $(CFLAGS) -fPIC -o fir.o fir.c -funroll-loops -O3 -fopenmp



