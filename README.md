# tnt-memory-analysis

## client.js
a Project64 script that can write a memory dump to a TCP server.
You will need to put it in the Project64 Scripts directory to run it.
startAddress is the address that the memory dump will begin at.
blockSize is the size of the dump in bytes. The max is 64000 as that's the max that can be sent over a TCP socket.

## server.js
a Nodejs program that will host a TCP server that will write sends from a connected client to a file.
It will overwrite the file each time.

## visualize_memory.py 
loads a memory dump from a file and renders it as an RGBA image.
It loops forever and constantly checks the file.

## visualize_board.py 
loads a 3200 byte memory dump from file, expected to be The New Tetris' game logic section.
It loops forever and renders a version of the game board in real time.