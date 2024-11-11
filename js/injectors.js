

function defaultColorInitialiser(paramBuilder){
    for(let i=0; i<paramBuilder.pointlist.length; i++){
        console.log(paramBuilder.pointlist[i])
        let y = parseFloat(paramBuilder.pointlist[i].get("lat"));
        let x = parseFloat(paramBuilder.pointlist[i].get("long"));
        if(y>paramBuilder.top) paramBuilder.top = y;
        if(y<paramBuilder.bottom) paramBuilder.bottom = y;
        if(x>paramBuilder.right) paramBuilder.right = x;
        if(x<paramBuilder.left) paramBuilder.left = x;
        paramBuilder.colourlist.push(paramBuilder.colourset.others);
    }
    console.log(paramBuilder.top, paramBuilder.bottom)
    console.log(paramBuilder.left, paramBuilder.right)
}

function defaultZoomInitialiser(paramBuilder){
    console.log(paramBuilder.top, paramBuilder.bottom)
    console.log(paramBuilder.left, paramBuilder.right)
    console.log(Math.ceil(16.01-Math.log2((paramBuilder.right-paramBuilder.left)/0.00452185866)))
    console.log(Math.ceil(16.01-Math.log2((paramBuilder.top-paramBuilder.bottom)/0.00452185866)))
    paramBuilder.zoom =  Math.min(
        Math.ceil(16.01-Math.log2((paramBuilder.right-paramBuilder.left)/0.00452185866)),
        Math.ceil(16.01-Math.log2((paramBuilder.top-paramBuilder.bottom)/0.00452185866))
    )
    console.log(paramBuilder.zoom)
}

function startPreinitialiser(paramBuilder){
    paramBuilder.colourlist = [paramBuilder.colourset.start];
    paramBuilder.pointlist = [start].concat(paramBuilder.pointlist);
}

function selectedPreinitialiser(paramBuilder){

    paramBuilder.colourlist = [paramBuilder.colourset.start, paramBuilder.colourset.selected]
    paramBuilder.pointlist = [start, selected].concat(
        paramBuilder.pointlist.filter(map=>
            map.get("lat")!==selected.get("lat") ||
            map.get("long")!==selected.get("long")
        )
    );
}

function defaultconfig(paramBuilder){
    paramBuilder.preInitialiser(paramBuilder);
    paramBuilder.initialiseColorList(paramBuilder);
    paramBuilder.initialiseZoom(paramBuilder);
    return {
        width: 500,
        height: 500,
        scale: paramBuilder.zoom,
        centre: new Map([["lat",(paramBuilder.top+paramBuilder.bottom)/2],["long",(paramBuilder.left+paramBuilder.right)/2]]),
        pointlist: paramBuilder.pointlist,
        colourlist: paramBuilder.colourlist
    }
}

function displayPinsUri(params){
    const { width, height, scale, centre, pointlist, colourlist } = params;
    let uri =
        `https://www.onemap.gov.sg/api/staticmap/getStaticImage?layerchosen=default` +
        `&zoom=${scale}&height=${height}&width=${width}` +
        `&lat=${centre.get('lat')}&lng=${centre.get('long')}&points=`;

    let i = 0; while (pointlist.length>0)
    {
        uri +=
            `%5B${pointlist[i].get("lat")}%2C${pointlist[i].get("long")}%2C` +
            `%22${colourlist[i][0]}%2C${colourlist[i][1]}%2C${colourlist[i][2]}%22%5D`;

        if (++i<pointlist.length) uri += "%7C"; // this is the delimiter, |
        else break;
    }
    document.getElementById("debug").innerText = uri;
    return uri;
}
function displayPinsUri2(params){
    const { width, height, scale, centre, pointlist, colourlist } = params;
    let uri =
        `https://www.onemap.gov.sg/amm/amm.html?mapStyle=Default` +
        `&zoomLevel=${scale}` +
        `&marker=latLng=${centre.get('lat')},${centre.get('long')}`;

    let i = 0; while (i<pointlist.length)
        uri += `&marker=latLng:${pointlist[i].get("lat")},${pointlist[i].get("long")}!colour:${colourlist[i++]}`
    uri += `&popupWidth=200`
    console.log(uri)
    document.getElementById("debug").innerText = uri;
    return uri;
}