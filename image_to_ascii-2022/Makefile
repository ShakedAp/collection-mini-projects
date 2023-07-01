CC=gcc
INCDIRS=-Istb
OPT=-O0
DEBUG=-g
LIBFLAGS=-lm
CFLAGS=-Wall $(INCDIRS) $(OPT) $(DEBUG)

CFILES= main.c
OBJECTS= main.o

BINARY=bin

all: $(BINARY)


$(BINARY): $(OBJECTS)
	$(CC) -o $@ $^ $(LIBFLAGS)

%.o: %.c
	$(CC) $(CFLAGS) -c -o $@ $^

clean:
	rm -rf $(BINARY) $(OBJECTS)
