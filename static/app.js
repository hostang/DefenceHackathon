/* Tiny header clock on right top of the page, getting the dom element */
const clockTime = document.getElementById('clockTime');
const clockDate = document.getElementById('clockDate');

/*  Update clock every second from local system*/
function tick(){
  const d = new Date();
  clockTime.textContent = d.toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
  clockDate.textContent = d.toLocaleDateString([], {weekday:'long', day:'numeric', month:'long', year:'numeric'});
}
tick(); setInterval(tick, 1000); /* update every second */

/* ===== Tasks ===== hard coded mock tasks to display in the */
const TASKS = [
  { name:"Northern Ridge Alpha",    grid:"5123 2068", lat:51.883063, lng:-1.312870, deadline:"14:30", status:"New" },
  { name:"Route Charlie Assessment",grid:"5146 2051", lat:51.881900, lng:-1.309900, deadline:"16:00", status:"New" },
  { name:"Hazard Zone Beta",        grid:"5098 2040", lat:51.881000, lng:-1.317300, deadline:"15:15", status:"New" },
  { name:"Farm Track Survey",       grid:"5069 2019", lat:51.879100, lng:-1.321200, deadline:"17:00", status:"New" },
  { name:"Woodline Bravo",          grid:"5181 2104", lat:51.886000, lng:-1.308300, deadline:"18:30", status:"Update" },
  { name:"Stream Crossing Recce",   grid:"5163 2130", lat:51.888300, lng:-1.310400, deadline:"19:00", status:"Update" }
];

const taskList = document.getElementById('taskList');

function renderTasks(){
  taskList.innerHTML = '';
  TASKS.forEach((t,i)=>{
    // Create div for each task while looking and assigning it class name to style it
    const tile = document.createElement('div');
    tile.className = 'task';
    tile.dataset.name = t.name; tile.dataset.grid = t.grid; tile.dataset.lat = t.lat; tile.dataset.lng = t.lng;
    tile.innerHTML = `
      <div class="d-flex justify-content-between">
        <strong>${t.name}</strong>
        <span class="badge ${t.status==='Update'?'text-bg-primary':'text-bg-dark'}">${t.status}</span>
      </div>
      <div class="text-muted small mt-1">
        📍 <span class="mono">${t.grid}</span><br>
        🌐 <span class="mono">${t.lat.toFixed(5)}, ${t.lng.toFixed(5)}</span><br>
        🕒 ${t.deadline}
      </div>`;
    tile.onclick = () => selectTask(tile);
    taskList.appendChild(tile);
    if(i===0) setTimeout(()=>selectTask(tile),0);
  });
}

/* ===== Map ===== */
let map, marker;
window.initMap = function(){
  const start = {lat:TASKS[0].lat, lng:TASKS[0].lng};
  map = new google.maps.Map(document.getElementById('map'), { center:start, zoom:16, mapTypeId:'satellite' });
  marker = new google.maps.Marker({ position:start, map, draggable:true, title:'LZ' });

  renderTasks();
};

/* ===== Task click -> fill form only site name and grid ref on selection ===== */
function selectTask(tile){
  document.querySelectorAll('.task').forEach(t=>t.classList.remove('active'));
  tile.classList.add('active');
  siteName.value = tile.dataset.name;
  gridRef.value  = tile.dataset.grid;
  const lat = parseFloat(tile.dataset.lat), lng = parseFloat(tile.dataset.lng);
  setLatLng(lat, lng);
  marker.setPosition({lat, lng});
  map.panTo({lat, lng});
}

/* ===== Form refs getting the DOMS ===== */
const siteName   = document.getElementById('siteName');
const areaSize   = document.getElementById('areaSize');
const gridRef    = document.getElementById('gridRef');
const slope      = document.getElementById('slope');
const elevation  = document.getElementById('elevation');
const lighting   = document.getElementById('lighting');
const details    = document.getElementById('details');
const reporter   = document.getElementById('reporter');
const callsign   = document.getElementById('callsign');
const reportTime = document.getElementById('reportTime');
const latH       = document.getElementById('lat');
const lngH       = document.getElementById('lng');
const submitBtn  = document.getElementById('submitBtn');

function setLatLng(lat, lng){
  latH.value = lat;
  lngH.value = lng;
}

   /*
    const form = document.getElementById('reportForm');
    const toast = document.getElementById('toast');

    form.addEventListener('submit', async (e)=>{
    e.preventDefault();
    try{
        submitBtn.disabled = true;
        const fd = new FormData(form);
        // change fetch URL to your deployed Cloud Run
        const res = await fetch('/api/reports', { method:'POST', body:fd });
        if(!res.ok) throw new Error(await res.text());
        const data = await res.json();
        toast.innerHTML = `<div class="alert alert-success py-2 my-2">Report saved. ID: ${data.id}</div>`;
        form.reset(); updateProgress();
    }catch(err){
        toast.innerHTML = `<div class="alert alert-danger py-2 my-2">Failed to submit: ${err.message}</div>`;
    }finally{
        submitBtn.disabled = false;
    }
    });
    */
