//variables
const perfil={
    src:["./static/img/imagen.jpg", "./static/img/imagen.jpg", "./static/img/imagen.jpg", "./static/img/imagen.jpg", "./static/img/imagen.jpg"],
    titulo:["Idrovo Jhon", "Morales Josué", "Morocho Jair", "Salgado Juan", "Raza Sebastian"],
    cargo:["Software Engineer - Web Developer", "Software Engineer - Web Developer", "Software Engineer - Web Developer", "Software Engineer - Web Developer", "Software Engineer - Web Developer"],
    descripcion:["Lorem ipsum dolor sit amet, consectetur adipisicing elit. Ad ut hic consequuntur quo qui culpa veritatis, blanditiis corrupti perspiciatis illo a laudantium illum sunt deleniti, nihil doloremque! Obcaecati, at, cupiditate.", "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Ad ut hic consequuntur quo qui culpa veritatis, blanditiis corrupti perspiciatis illo a laudantium illum sunt deleniti, nihil doloremque! Obcaecati, at, cupiditate.", "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Ad ut hic consequuntur quo qui culpa veritatis, blanditiis corrupti perspiciatis illo a laudantium illum sunt deleniti, nihil doloremque! Obcaecati, at, cupiditate.", "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Ad ut hic consequuntur quo qui culpa veritatis, blanditiis corrupti perspiciatis illo a laudantium illum sunt deleniti, nihil doloremque! Obcaecati, at, cupiditate.", "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Ad ut hic consequuntur quo qui culpa veritatis, blanditiis corrupti perspiciatis illo a laudantium illum sunt deleniti, nihil doloremque! Obcaecati, at, cupiditate."]
}

const redes_sociales={
    href:["#", "#", "#", "#"],
    class:["fa fa-facebook-square", "fa fa-twitter-square", "fa fa-google-plus-square", "fa fa-github-square"], 
    aria:["true", "true", "true", "true"]
}


function cargarRedes(){
    var texto=""; 
    for(var i=0; i<redes_sociales.href.length; i++){
        texto+=
        `<ul>
        <li><a href="${redes_sociales.href[i]}"><i class="${redes_sociales.class[i]}" aria-hidden="${redes_sociales.aria[i]}"></i></a></li>
      </ul>`
    }
    return texto;
};



function cargarPefil(){
    var texto="";
    for(var i=0; i<perfil.src.length; i++){
        texto+=`<section class="box">
        <img src="${perfil.src[i]}" width="180" alt="" class="box-img">
        <h1>${perfil.titulo[i]}</h1>
        <h2>${perfil.cargo[i]}</h2>
        <p>${perfil.descripcion[i]}</p>
        ${cargarRedes()}
      </section>`;
    }
    return texto;
};

document.getElementById("prueba").innerHTML=cargarPefil();