const startAddress = 0x8029EBC0
const blockSize = 3200

var client = new Socket()
client.connect(4000, 'localhost', function() {
    var response = '';

    client.on('data', function(data) {
        response += data.toString();
    });

    client.on('end', function() {
        console.log(response);
    });
})

function sendMemory() {
    const memory = mem.getblock(startAddress, blockSize)
    client.write(memory)
}
setInterval(sendMemory, 25)