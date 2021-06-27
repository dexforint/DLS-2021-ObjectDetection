let uploadButtonWrapper = document.getElementById('upload-button-wrapper');
let uploadButton = document.getElementById('upload-button');
let closeButton = document.getElementById('close-button');
let imageWrapper = document.getElementById('image-wrapper');
let image = document.getElementById('image');
// let canvasWrapper = document.getElementById('canvas-wrapper');
// const canvas = document.getElementById('canvas');
// const ctx = canvas.getContext("2d");

function obj2data(obj) {
    let fd = new FormData();
    obj = JSON.stringify(obj);
    fd.append('json', obj);
    return fd;
}

let cls2color = {
    'cat': 'green'
}

// function drawRect(x_min, y_min, x_max, y_max, cls){
//     let width = (x_max - x_min);
//     let height = (y_max - y_min);
//     let x = x_min * 2;
//     let y = y_min * 2;


//     let color = cls2color[cls];
//     ctx.strokeStyle = color;
//     ctx.fillStyle = color;
//     ctx.font = "24px serif";
//     ctx.strokeRect(x, y, width, height);

//     let textObj = ctx.measureText(cls);
    
//     ctx.fillRect(x - 1, y, textObj.width + 6, 36);
    
//     ctx.fillStyle = "white";
//     ctx.fillText(cls, x + 3 - 1, y + 24);
// }

function serialize(form) {
    let fd = new FormData();
    for (let el of form.querySelectorAll('[name]')) {
        let name = el.getAttribute('name');
        let value;
        if (el.type == 'file') {
            value = el.files[0];
        } else if (el.value !== undefined) value = el.value;
        else value = el.innerHTML;
        fd.append(name, value);
    }
    return fd;
}

async function ajax(url, data, response_handler = null) {
    if (data.__proto__ == ({}).__proto__) data = obj2data(data);
    let response = await fetch(url, {
        method: 'POST',
        // headers: {
        //     'Content-Type': 'application/json;charset=utf-8'
        // },
        body: data
    });
    if (response.ok) {
        if (response_handler) response_handler(await response.json());
    } else console.log("Ошибка HTTP: " + response.status);

}

function clearInputFile(f) {
    if (f.value) {
        try {
            f.value = ''; //for IE11, latest Chrome/Firefox/Opera...
        } catch (err) {}
        if (f.value) { //for IE5 ~ IE10
            var form = document.createElement('form'),
                parentNode = f.parentNode,
                ref = f.nextSibling;
            form.appendChild(f);
            form.reset();
            parentNode.insertBefore(f, ref);
        }
    }
}

uploadButton.addEventListener('change', (event) => {
    if (!uploadButton.files || !uploadButton.files[0]) return;

    let file = uploadButton.files[0];

    let fd = new FormData();
    fd.append('image', file);

    ajax('/detect-object', fd, (response) => {
        console.log(response);
        if (response['ok']){
            imageWrapper.style.maxWidth = (document.body.clientWidth - 50) + "px";
            imageWrapper.style.maxHeight = (document.body.clientHeight - 2 * document.querySelector('.head').offsetHeight - 50) + "px";


            let path = response['path'];
            image.src = path;
        }
    });

    image.addEventListener('load', (event) => {
        imageWrapper.style.display = 'block';
        uploadButtonWrapper.style.display = 'none';
    });
    
    // let containerRatio = maxWidth / maxHeight;

    

    // const FR = new FileReader();
    // FR.addEventListener("load", (evt) => {
    //     const img = new Image();
    //     // img.addEventListener("load", () => {
    //     //     let width, height;
    //     //     // let ratio = img.width / img.height;
            
    //     //     // if (ratio >= containerRatio) {
    //     //     //     width = maxWidth;
    //     //     //     height = maxWidth / ratio;
    //     //     // } else {
    //     //     //     height = maxHeight;
    //     //     //     width = ratio * height;
    //     //     // }

    //     //     canvas.width = img.width;
    //     //     canvas.height = img.height;
    //     //     // ctx.drawImage(img, 0, 0, width, height);

    //     //     ajax()

    //     //     canvasWrapper.style.display = 'block';
    //     //     uploadButtonWrapper.style.display = 'none';
    //     // });
    //     // img.src = evt.target.result;
    // });
    // FR.readAsDataURL(uploadButton.files[0]);
});



closeButton.addEventListener('click', (event) => {
    imageWrapper.style.display = 'none';
    uploadButtonWrapper.style.display = 'block';
    clearInputFile(uploadButton);
});