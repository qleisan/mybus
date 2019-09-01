function loadDoc() {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var obj = JSON.parse(this.responseText);
      console.log("ajax call ok");
      document.body.style.backgroundColor = obj.colors[0];
      document.getElementById("time").innerHTML = obj.timetext;
      document.getElementById("time").style.color = obj.colors[1];
      document.getElementById("bus1").innerHTML = "["+obj.table[0][0]+"] "+obj.table[0][1]+" min";
      document.getElementById("bus1").style.color = obj.colors[2];
      document.getElementById("bus2").innerHTML = "["+obj.table[1][0]+"] "+obj.table[1][1]+" min";
      document.getElementById("bus2").style.color = obj.colors[2];
      document.getElementById("bus3").innerHTML = "["+obj.table[2][0]+"] "+obj.table[2][1]+" min";
      document.getElementById("bus3").style.color = obj.colors[2];
      document.getElementById("bus4").innerHTML = "["+obj.table[3][0]+"] "+obj.table[3][1]+" min";
      document.getElementById("bus4").style.color = obj.colors[2];
      document.getElementById("bus5").innerHTML = "["+obj.table[4][0]+"] "+obj.table[4][1]+" min";
      document.getElementById("bus5").style.color = obj.colors[2];
    } else if (this.status == 200)
    {
      // discard
    } else if (this.readyState == 1 && this.status == 0)
    {
      // this seems to be normal
    } else {
      //Modern browser return readyState=4 and status=0 if too much time passes before the server response.
      console.log("ajax call _FAILED_"); //not necessarily true
      console.log(this.readyState);
      console.log(this.status);
      count++;
      document.getElementById("err").innerHTML = "Error counter = " + count + "  Check browser console log";
    }
  };
  xhttp.open("GET", "ajax", true);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send();
}

var count = 0;
loadDoc() //first update asap
var interval = setInterval("loadDoc()", 10000);
