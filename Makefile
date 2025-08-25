CC = g++

GSL_DIR = /usr

INC = -I$(GSL_DIR)
# Debug build: use -g for debug symbols, -O0 for no optimization
# Release build: use -O3 for optimization
DEBUG_FLAGS = -g -O0
RELEASE_FLAGS = -O3

# Default to debug build - change to $(RELEASE_FLAGS) for optimized build
CFLAGS = $(DEBUG_FLAGS) $(INC) 

LIB_DIRS = -L$(GSL_DIR)/lib
LIBS = -lgsl -lgslcblas -lm
LFLAGS = $(DEBUG_FLAGS) $(LIB_DIRS) $(LIBS)

BIN = seq2exp
all: $(BIN)

clean:
	rm -f $(BIN) *.o

Tools.o : Tools.h Tools.cpp
	$(CC) $(CFLAGS) -c Tools.cpp
ExprPredictor.o : Tools.h ExprPredictor.h  ExprPredictor.cpp
	$(CC) $(CFLAGS) -c ExprPredictor.cpp
seq2exp.o : Tools.h ExprPredictor.h seq2exp.cpp
	$(CC) $(CFLAGS) -c seq2exp.cpp

seq2exp : Tools.o ExprPredictor.o seq2exp.o 
	$(CC) -o $@ Tools.o ExprPredictor.o seq2exp.o $(LFLAGS) 


