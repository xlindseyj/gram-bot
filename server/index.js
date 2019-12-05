const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const findConfig = require('find-config');
// const http = require('http');
const app = express();

require('dotenv').config({ path: findConfig('.env') });

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cors());

app.listen(process.env.NODE_PORT, () => {
    console.log(`Server listening on ${process.env.NODE_HOST}:${process.env.NODE_PORT}`)
});

app.get('/', (response) => {
    response.json({ 
        message: 'Welcome to GramBot',
        author: 'Jake Lindsey'
    });
});

// app.get('/likeByHashtag', likeByHashtag);
// app.get('/followByHashtag', followByHashtag);
app.get('/ping', ping);

function ping(req, res) {

    let spawn = ("child_process").spawn; // -require
    
	let process = spawn(
        'python', [
            "./scripts/ping.py"
        ]
    );

	process.stdout.on('data', function(data) {
		res.send(data.toString());
	});
}

function likeByHashtag(req, res) {

    let spawn = require("child_process").spawn; // -require
    
	let process = spawn(
        'python', [
            "./scripts/likeByHashtag.py", // change to other repo later
            // req.query.
        ]
    );

	process.stdout.on('data', function(data) {
		res.send(data.toString());
	});
}

function followByHashtag(req, res) {

    let spawn = require("child_process").spawn; // -require
    
	let process = spawn(
        'python', [
            "./scripts/followByHashtag.py", // change to other repo later
            // req.query.
        ]
    );

	process.stdout.on('data', function(data) {
		res.send(data.toString());
	});
}
