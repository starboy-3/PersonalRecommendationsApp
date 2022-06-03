async function doRequest() {
    var data = document.getElementById("search").value;
    var url = "http://10.77.15.146:8080/search/" + data
    var text = "";
    let response = await fetch(url, {
      methode: 'GET',
      mode: 'cors',
      headers: {
        'Access-Control-Allow-Origin':'*'
      }
    });

    if (response.ok) {
      text = await response.text();
      alert(text);
    } else {
      alert("Возникли некоторые ошибки");
    }
    const json = JSON.parse(text);
    const indices = JSON.parse(json.indices);
    alert(indices[0]);

    let doc = document.implementation.createHTMLDocument("New Document");
    var i;
    for (i = 0; i < indices.length; i += 1) {
        let p = doc.createElement("p");
        p.textContent = "This is a new paragraph.";
        try {
            doc.body.appendChild(p);
        } catch (e) {
            console.log(e);
        }
    }
  
    // Copy the new HTML document into the frame

    let destDocument = frame.contentDocument;
    let srcNode = doc.documentElement;
    let newNode = destDocument.importNode(srcNode, true);

    destDocument.replaceChild(newNode, destDocument.documentElement);
}
