let start = new Map(), selected = new Map();
let locationjson;
const defaultdisplayNo = 8;
let displayedElementNo = defaultdisplayNo;
let maptype = false;
const iframe = document.createElement("iframe");
iframe.id = "map"
const image = document.createElement("img");
image.id = "map"

const changeMap = () => {
    document.getElementById("map-container").removeChild(
        document.getElementById("map")
    )
    maptype = !maptype
    document.getElementById("map-container").appendChild(maptype?iframe:image);
}
const locationDirectDistanceComparator = (a, b) =>
    ((a["Longitude"]-start.get("long"))**2+(a["Latitude"]-start.get("lat"))**2)**0.5 -
    ((b["Longitude"]-start.get("long"))**2+(b["Latitude"]-start.get("lat"))**2)**0.5;
function compareMaps(map1, map2) {
    let testVal;
    if (map1.size !== map2.size) {
        return false;
    }
    for (let [key, val] of map1) {
        testVal = map2.get(key);
        // in cases of an undefined value, make sure the key
        // actually exists on the object so there are no false positives
        if (testVal !== val || (testVal === undefined && !map2.has(key))) {
            return false;
        }
    }
    return true;
}
const addressResolverUri = str =>
    `https://www.onemap.gov.sg/api/common/elastic/search?searchVal=${str}&returnGeom=Y&getAddrDetails=N`;


function updateMap(pointlist, mode=0){
    const map = document.getElementById("map");
    console.log("update map",mode)
    switch(mode){
        case 0:
            try{
                map.src = new urlBuilder().preInit(startPreinitialiser).build().build(pointlist, start, selected)
            }catch(error) {
                console.error(error)
            }
            break;
        case 1:
            map.src = new urlBuilder().preInit(selectedPreinitialiser).build().build(pointlist, start, selected)
            break;
        case 2:
            try{
                map.src = new urlBuilder().preInit(startPreinitialiser).colorset(omamm).uri(displayPinsUri2).build().build(pointlist, start, selected)
            } catch(error){
                console.error(error)
            }
            break;
        case 3:
            try{
                map.src = new urlBuilder().preInit(selectedPreinitialiser).colorset(omamm).uri(displayPinsUri2).build().build(pointlist, start, selected)
            } catch(error){
                console.error(error)
            }break;
    }
}


function regenerateSidebar(){
    const displaystring = locationjson.
    sort(locationDirectDistanceComparator).
    slice(0,displayedElementNo).
    map(location =>
        `${location["Name"]}\nAddress: ${location["Address"]}\nOpening Hours: ${location["Opening Hours"]}`
    );
    const locationcoords = locationjson.
    slice(0,displayedElementNo).
    map(location =>
        new Map([["long",location["Longitude"]],["lat",location["Latitude"]]]
        ));
    document.getElementById("sidebar").textContent = '';
    for(let i=0;i<displaystring.length;i++){
        const newbutton = document.createElement("button");
        newbutton.innerText = displaystring[i];
        newbutton.onclick = () => highlightSelected(locationcoords[i]);
        document.getElementById("sidebar").appendChild(newbutton);

        const hrline=document.createElement("hr");
        hrline.style.border = "3px solid ";
        document.getElementById("sidebar").appendChild(hrline);
    }
}
function highlightSelected(coord){
    selected = coord;
    const locationcoords = locationjson.
    slice(0,displayedElementNo).
    map(location =>
        new Map([["long",location["Longitude"]],["lat",location["Latitude"]]]
        ));
    if(!maptype)
        updateMap(locationcoords,1);
    else
        updateMap(locationcoords,3);
    document.getElementById("submit").style.display="block";
}
async function submitLocationAsync() {
    //Set displayed locations to 10 first. See more raises this
    displayedElementNo = defaultdisplayNo;
    const input = document.getElementById('userInput').value;
    const params = new URLSearchParams({
        category: sessionStorage.getItem("category")
    }).toString();
    try {
        // Await multiple fetch requests simultaneously
        let startjson;
        [startjson, locationjson] = await Promise.all([
            fetch(addressResolverUri(input))
                .then(response1 => {
                    if (!response1.ok) throw new Error(`Error fetching from address resolver: ${response1.statusText}`);
                    return response1.json();
                }),
            fetch(`${window.location.href}api/location?${params}`)
                .then(response2 => {
                    if (!response2.ok) throw new Error(`Error fetching from location database: ${response2.statusText}`);
                    return response2.json();
                })
        ])
            .catch(error => {
                console.error("Error fetching data:", error);
                // Handle the error (e.g., show an error message to the user)
            });


        const results = startjson.results[0];
        start.set('lat', results["LATITUDE"]);
        start.set('long', results["LONGITUDE"]);

        const locationcoords = locationjson.
        sort(locationDirectDistanceComparator).
        slice(0,displayedElementNo).
        map(location =>
            new Map([["long",location["Longitude"]],["lat",location["Latitude"]]]
            ));
        document.getElementById("debug").innerText = locationcoords.toString();
        if(maptype)
            updateMap(locationcoords,2)
        else updateMap(locationcoords,0);
        regenerateSidebar();
        // Display the results
    } catch (error) {
        // Handle any errors
        document.getElementById("debug").textContent = `Error: ${error.message}`;
    }
}
function redirectToFinal(){
    sessionStorage.setItem("lat",selected.get("lat"));
    sessionStorage.setItem("long",selected.get("long"));
    window.location.href = "./final";
}