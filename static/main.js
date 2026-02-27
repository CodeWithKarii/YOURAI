let canvas = document.getElementById("myCanvas");

function startMenu() {
    let audio = new Audio("static/music.mp3");
    let startButton = document.getElementById("start-button");  
    let instructionsButton = document.getElementById("instructions-button");
    let exitButton = document.getElementById("exit-button");
    let menu = document.getElementById("start-menu");
    startButton.addEventListener("click", function() {
        audio.play();
        menu.style.display = "none";
        
    });
    instructionsButton.addEventListener("click", function() {
        alert('here are some instructions')
        

    });
    exitButton.addEventListener("click", function() {
       
    });
}

function snakeFood() {
    let foodX = Math.floor(Math.random() * 30) * 20;
    let foodY = Math.floor(Math.random() * 30) * 20;
    foodColor = canvas.getContext("2d").fillStyle = "red";
    foodShape = canvas.getContext("2d").fillRect(foodX, foodY, 20, 20); 
}

let snake = {
    x: 10,
    y: 10,
    size: 20,
    direction: "right",
    body: [{x: 10, y: 10}]

};


document.addEventListener("DOMContentLoaded", function() {
           startMenu();
           snakeFood();
           alert('async loaded')

          
});



    




