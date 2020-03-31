//http://expressjs.com/en/api.html#app
//https://medium.com/javascript-in-plain-english/algorithms-101-count-primes-in-javascript-97f1ff85e040
//http://lendulet.tmit.bme.hu/~retvari/k8s/kubernetes_intro.html
//https://buddy.works/guides/how-dockerize-node-application

var express = require('express')
var app = express()

var countPrimes = function(n) {

    //build array to mark
    let nums = [...Array(n).keys()]
    
    for(let i = 2; i*i < n; i++){
        if(nums[i] !== "nope"){
            for(let j = i*i; j < n; j += i){
                nums[j] = "nope"
            }
        }
    }

    let primes = []

    for(let i = 0; i < nums.length; i++) {
        if(nums[i] > 1){
            primes.push(nums[i])
        }
    }

    //console.log(primes)
    return primes.length 
};

var handleRequest = function(request, response) {
    console.log('Received request for URL: ' + request.url);
    response.writeHead(200);
    maxNumber = request.params.max;
    response.end('Primes: ' + countPrimes(parseInt(maxNumber)));
};

app.get('/num/:max', handleRequest)
app.listen(8080)