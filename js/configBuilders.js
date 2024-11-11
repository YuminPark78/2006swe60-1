class paramBuildTemplate {
    constructor(preinit, colourinit, zoominit, colorset, config, uri){
        this.preInitialiser = preinit
        this.initialiseColorList = colourinit
        this.initialiseZoom = zoominit;
        this.colourset = colorset;
        this.config = config;
        this.uri = uri
    }
    build(pointlist, start=null, selected=null){
        this.temp = pointlist.slice();
        this.pointlist = pointlist;
        console.log("MainBuild",pointlist[0])
        const reference = start??selected??pointlist[0];
        this.left = parseFloat(reference.get("long"));
        this.right = this.left
        this.top = parseFloat(reference.get("lat"));
        this.bottom = this.top;
        this.colourlist = [];
        this.elementno = 0;
        this.zoom = 0;
        return this.uri(this.config(this));
    }
}

class urlBuilder{
    constructor() {
        this.preInitialiser = ()=>{}
        this.initialiseColorList = defaultColorInitialiser;
        this.initialiseZoom = defaultZoomInitialiser;
        this.config = defaultconfig
        this.colourset = omsm
        this.url = displayPinsUri
    }
    ColorInit(colorinit){
        this.initialiseColorList = colorinit;
        return this
    }
    ZoomInit(zoominit){
        this.initialiseZoom = zoominit;
        return this
    }
    preInit(preinit){
        this.preInitialiser = preinit;
        return this;
    }
    colorset(colourset){
        this.colourset = colourset
        return this;
    }
    conf(config){
        this.config = config;
        return this
    }
    uri(urlbuilder){
        this.url = urlbuilder
        return this;
    }
    build(){
        return new paramBuildTemplate(
            this.preInitialiser,
            this.initialiseColorList,
            this.initialiseZoom,
            this.colourset,
            this.config,
            this.url
        )
    }
}