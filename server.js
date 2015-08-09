var mosca = require('mosca');
var settings = {
    id: 'mosca-broker',
    logger: {
        level: 'info'
    },
    secure: {
        keyPath: '',
        certPath: ''
    }
};

var server = mosca.Server(settings);
server.on('ready', function(){
    console.log('Mosca has started');
});
