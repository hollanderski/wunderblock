const express = require('express');
var bodyParser = require('body-parser');
const fileUpload = require('express-fileupload');
var mysql = require('mysql');
const path = require('path');
var cors = require('cors');
const fs = require('fs');
var dateTime = require('node-datetime');

const THREE = global.THREE = require('three');
require('three/examples/js/math/MeshSurfaceSampler.js');
var perlin = require('./public/js/perlin2');




const geometry = new THREE.PlaneGeometry(  2000, 2000, 256, 256);
const material = new THREE.MeshPhongMaterial(); 
mesh = new THREE.Mesh( geometry, material );
var peak = 100;
        var smoothing = 150; //300

        var vertices = mesh.geometry.attributes.position.array;
          for (var i = 0; i <= vertices.length; i += 3) {
            vertices[i+2] = peak * perlin.noise.perlin2(
                (mesh.position.x + vertices[i])/smoothing, 
                (mesh.position.z + vertices[i+1])/smoothing
            );
        }

      mesh.geometry.rotateX( - Math.PI / 2 );

        mesh.geometry.attributes.position.needsUpdate = true;
        mesh.geometry.computeVertexNormals();


sampler = new THREE.MeshSurfaceSampler( mesh )
            .setWeightAttribute( 'color' )
            .build();



const app = express();

// enable files upload
app.use(fileUpload({
    createParentPath: true
}));

app.use(cors({origin: '*'}));
var jsonParser = bodyParser.json();
var urlencodedParser = bodyParser.urlencoded({ extended: false })

app.use(express.static('public'));
var server = require('http').createServer(app);

const io = require('socket.io')(server, {
    cors: {
        origin: "http://xoqhbtq.cluster030.hosting.ovh.net",
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





// https://www.tutsmake.com/node-js-fetch-and-display-data-from-mysql-database-in-html-list/ 
// https://www.bezkoder.com/node-js-rest-api-express-mysql/

const Trace = function(trace) {
  this.id = trace.id;
  this.day = trace.day;
  this.hour = trace.hour;
  this.x = trace.x;
  this.y = trace.y;
  this.z = trace.z;
  this.freq = trace.freq;
  this.map = trace.map;
  this.bumpmap = trace.bumpmap;
  this.sound = trace.sound;
};

Trace.getAll = (title, result) => {

	connection.query('SELECT id, DATE_FORMAT(day, "%Y-%m-%d") as day, hour, x, y, z, freq, map, bumpmap, sound FROM traces', function (err, rows, fields) {
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



const msg = `NodeJS ${process.version} server for Wunderblock\ncreated by Ninon Lize Masclef & Sylvain Reynal`;


app.get('/about', function(req, res){

 	res.send(msg);
});

app.get('/', function(req, res) {
  res.sendFile(path.join(__dirname, '/index.html'));
});

/* https://attacomsian.com/blog/uploading-files-nodejs-express */
app.post('/traces', (req, res) => {
    try {

        if(!req.files) {
            res.send({
                status: false,
                message: 'Data empty'
            });
        } else {
            //Use the name of the input field to retrieve the uploaded file
            let audio = req.files.audio;
            let bumpmap = req.files.bumpmap;
            let map = req.files.map;

            if(!audio || !bumpmap || !map){
                res.send({
                  status: false,
                  message: 'Missing files'
              });
            }
            else{

              console.log("moving files")


              //Use the mv() method to place the file in upload directory 
              audio.mv('./public/sound/' + audio.name);
              bumpmap.mv('./public/texture/cv/' + bumpmap.name);
              map.mv('./public/texture/cv/' + map.name);

                const position = new THREE.Vector3();
                sampler.sample( position );

                var dt = dateTime.create();
 
                 // Create a Trace
                  const trace = new Trace({
                    day :  dt.format('Y-m-d'),
                    hour : dt.format('H:M:S'),
                    x: position.x,
                    y: position.y,
                    z: position.z,
                    freq: Math.random(),
                    map: map.name,
                    bumpmap: bumpmap.name,
                    sound: audio.name
                  });

                  console.log(trace);


                  io.sockets.emit("createTrace", trace);

                  // Save file /!\ 

                  // Save Trace in the database
                  Trace.create(trace, (err, data) => {
                    if (err)
                      res.status(500).send({
                        message:
                          err.message || "Some error occurred while creating the Trace."
                      });
                    else{

                      res.send(trace);
                    }
                  }); 

            }
            
        }
    } catch (err) {
        res.status(500).send(err);
    }
});




server.listen(3000);
//app.listen(3000);
