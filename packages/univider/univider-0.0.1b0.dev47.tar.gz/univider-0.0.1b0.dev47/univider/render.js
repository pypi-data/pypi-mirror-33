var page = require('webpage').create(),
  system = require('system');

address = system.args[1];
loadimg = system.args[2];
timeout = system.args[3] * 1000;

page.settings.loadImages = loadimg;
page.settings.resourceTimeout = timeout;
//page.onResourceError = function(e) {
//	console.log(e.errorCode);
//	console.log(e.errorString);
//	console.log(e.url);
//	phantom.exit(1);
//};
page.onResourceTimeout = function(e) {
    var sc = page.content;
    window.setTimeout(function(){
      console.log(sc);
      phantom.exit();
    },100);
	//console.log(e.errorCode);   // it'll probably be 408
	//console.log(e.errorString); // it'll probably be 'Network timeout on resource'
	//console.log(e.url);		 // the url whose request timed out
	//phantom.exit(1);
};
page.open(address, function(status) {
  if (status !== 'success') {
    console.log("901");
	console.log('FAIL to load the address');
	console.log(address);
    phantom.exit(1);
  } else {
    var sc = page.content;
    window.setTimeout(function(){
      console.log(sc);
      phantom.exit();
    },100);
  }
});