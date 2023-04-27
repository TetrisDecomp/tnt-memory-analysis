const net = require('net')
const fs = require('fs')

const handleConnection = (connection) => {
    console.log('client connected')

    const onConnData = (data) => {  
        fs.writeFile(`./bin/dump.data`, data, err => {
            if (err) {
                console.error(err)
            }
        })
    }

    const onConnClose = (remoteAddress) => {  
        console.log('connection from %s closed', remoteAddress);  
    }

    const onConnError = (err) => {  
        console.log('Connection %s error: %s', remoteAddress, err.message);  
    }
    const remoteAddress = connection.remoteAddress + ':' + connection.remotePort

    connection.on('data', onConnData)
    connection.on('close', onConnClose)
    connection.on('error', onConnError)
}

const server = net.createServer()
server.on('connection', handleConnection)

server.listen(4000, () => {
   console.log('server listening to %j', server.address());  
})

