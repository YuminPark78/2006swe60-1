function Guide() {
	window.location.href = '/guides/Recyclo_Guide_Ewaste.pdf';
}



function storerecyclingtype() {
    const ICTSelected = document.getElementById("ICT").checked;
    const batteriesSelected = document.getElementById("Batteries").checked;
    const othersSelected = document.getElementById("Others").checked;
    const lampsSelected = document.getElementById("lamps").checked;


    if (othersSelected){
        sessionStorage.setItem("category", "others");
    }
    else if ((batteriesSelected) && (lampsSelected) && (ICTSelected))  {
        sessionStorage.setItem("category", "ictbattlamps");
 
    }
    else if ((batteriesSelected) && (lampsSelected)) {
        sessionStorage.setItem("category", "battlamps");
  
    }
    else if ((batteriesSelected) && (ICTSelected)) {
        sessionStorage.setItem("category", "ictbatt");
    }

    else if (batteriesSelected)
    {
        sessionStorage.setItem("category", "batteries");
    }

}

function nextpage() {
    const checkboxes = document.querySelectorAll('.checkbox');
    if(!Array.from(checkboxes).some(checkbox => checkbox.checked))
    {
        alert("Select at least one category");
        return;
    }
    storerecyclingtype()
    window.location.href="/map";
}
