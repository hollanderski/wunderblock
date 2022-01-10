const express = require('express');
var bodyParser = require('body-parser');
var mysql = require('mysql');
const path = require('path');
var cors = require('cors');
const fs = require('fs');



const app = express();
app.use(cors({origin: '*'}));
app.use(express.static('public'));
var server = require('http').createServer(app);

const io = require('socket.io')(server, {
    cors: {
        origin: "http://localhost:3000",
        methods: ["GET", "POST"],
        transports: ['websocket', 'polling'],
        credentials: true
    },
    allowEIO3: true
});


const port = 3000;

var connection;

fs.readFile('db.txt', function(err, data) {
    if(err) throw err;

    const cred = data.toString().replace(/\r\n/g,'\n').split('\n');

    connection = mysql.createConnection({
      host: cred[0],
      user: cred[1],
      password: cred[2],
      database: cred[3]
    })


});





var jsonParser = bodyParser.json();
var urlencodedParser = bodyParser.urlencoded({ extended: false })



// https://www.tutsmake.com/node-js-fetch-and-display-data-from-mysql-database-in-html-list/ 
// https://www.bezkoder.com/node-js-rest-api-express-mysql/

const Trace = function(trace) {
  this.id = trace.id;
  this.x = trace.x;
  this.y = trace.y;
  this.map = trace.map;
  this.bump = trace.bump;
  //this.sound = trace.breath;
};

Trace.getAll = (title, result) => {

	connection.query('SELECT id, x, y, map, bump FROM traces', function (err, rows, fields) {
		if (err){
			console.log("error ", err);
			result(null, err);
			return;
		}
		console.log(rows);
		result(null, rows);
	})


}

Trace.create = (newTrace, result) => {

	connection.query("INSERT INTO traces SET ?", newTrace, (err, res) => {
    if (err) {
      console.log("error: ", err);
      result(err, null);
      return;
    }

    console.log("created trace: ", { id: res.insertId, ...newTrace });
    result(null, { id: res.insertId, ...newTrace });
  });

};



 app.get('/traces', function(req, res){
  const title = "";

  Trace.getAll(title, (err, data) => {
    if (err)
      res.status(500).send({
        message:
          err.message || "Some error occurred while retrieving traces."
      });
    else res.send(data);
  });
});

app.post('/traces', jsonParser, function(req, res){
	console.log(req.body);
  // Validate request
  if (!req.body) {
    res.status(400).send({
      message: "Content can not be empty!"
    });
  }

  // Create a Trace
  const trace = new Trace({
    x: req.body.x,
    y: req.body.y,
    map: req.body.map,
    bump: req.body.bump
  });

  // Save file /!\ 

  // Save Trace in the database
  Trace.create(trace, (err, data) => {
    if (err)
      res.status(500).send({
        message:
          err.message || "Some error occurred while creating the Trace."
      });
    else{

      io.sockets.emit("foo", req.body);
      res.send(data);
    }
  });
});


const msg = `NodeJS ${process.version} server for Wunderblock\ncreated by Ninon Lize Masclef & Sylvain Reynal`;


app.get('/about', function(req, res){

 	res.send(msg);
});

app.get('/', function(req, res) {
  res.sendFile(path.join(__dirname, '/bloom.html'));
});


server.listen(3000);
