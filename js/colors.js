class ColorSet{
    constructor(start, selected, others){
        this.start = start;
        this.selected = selected;
        this.others = others;
        Object.freeze(this)
    }
}

const omsm = new ColorSet([0, 0, 100],[255,0,0],[0,0,0]);
const omamm = new ColorSet("red","blue","cadetblue");