const SPRITE_COUNT = 2;
const MAX_IMAGES = 12;
const STUDENT_NAME = "Mari Iochi"

let isFirstStudentResponse = true;
let spriteType = "normal"; // Default to "normal"
var lastEmotion = "neutral"

document.getElementById("student-image").alt = STUDENT_NAME;

document.getElementById("send-btn").addEventListener("click", sendMessage);
document.getElementById("user_input").addEventListener("keydown", function(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault(); // Prevent other default actions
        sendMessage();
    }
});

// Function to generate a random session ID
function generateRandomString(length) {
    let characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length));
    }
    return result;
}

// Function to get a cookie value by name
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

// Function to get or create session ID
function getSessionID() {
    let sessionID = getCookie("SESS_ID");
    if (!sessionID) {
        sessionID = generateRandomString(16);
        document.cookie = "SESS_ID=" + sessionID + "; expires=Session; path=/";
    }
    return sessionID;
}

function updateStudentImage(expression) {
    const StudentImage = document.getElementById("student-image");
    StudentImage.src = `assets/sprites/${spriteType}/${expression}.png`;
    StudentImage.classList.add("move-up-down");
    StudentImage.addEventListener('animationend', function() {
        StudentImage.classList.remove("move-up-down");
    });
}

async function sendMessage() {
    var userInput = document.getElementById("user_input").value;
    let SESS_ID = getSessionID();
    const request = new Request("/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Cookie": SESS_ID
        },
        body: JSON.stringify({message: userInput})
    });
    
    if (userInput) {
        var chatDisplay = document.getElementById("chat-display");

        // Display user input
        var userDiv = document.createElement("div");
        userDiv.classList.add("user");
        userDiv.innerText = "You: " + userInput;
        chatDisplay.appendChild(userDiv);
        document.getElementById("user_input").value = "";
        userInput = userInput.replace(/"/g, "'"); // Sanitize input

        // Send the input to the server
        StudentDiv = document.createElement("div");
        StudentDiv.classList.add("student");
        StudentDiv.innerText = "Mari: ";
        chatDisplay.appendChild(StudentDiv);

        chatDisplay.scrollTop = chatDisplay.scrollHeight;
        var response = await fetch(request)
        const decoder = new TextDecoder("utf-8");
        const reader = response.body.getReader();
        let assistant_message = "";
        let token_count = 0;
        // Stream response body
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            // Decode the incoming chunk
            const chunk = decoder.decode(value, { stream: true });
            token_count++;
            // Use the generator to yield parsed message content
            console.log("Assistant says:", chunk);
            assistant_message += chunk;
            StudentDiv.innerText += chunk;
            chatDisplay.scrollTop = chatDisplay.scrollHeight;
        }
        console.log("Stream completed");
        console.log("Calling updateEmotion with message:", assistant_message);
        updateEmotion(assistant_message);

        // Play background music when Student responds for the first time
        if (isFirstStudentResponse) {
            var bgMusic = document.getElementById("bg-music");
            bgMusic.volume = 0.2; // Set volume to 20%
            bgMusic.play();
            isFirstStudentResponse = false;
        }

        // Scroll to the bottom of the chat display
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
    }
}

function updateEmotion(text) {
    //calls endpoint to classify text
    fetch("/emotion", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({message: text})
    })
    .then(response => response.json())
    .then(data => {
        //sprite gets changed to corresponding emotion
        lastEmotion = data["predicted_emotion"]
        updateStudentImage(lastEmotion)
    })
}

// For background change
var bgbtn = document.getElementById("background-btn");
var bgnumber = 1;

document.getElementById("student-container").style.backgroundImage = `url('assets/backgrounds/Background${bgnumber}.jpg')`;
bgbtn.onclick = function() {
    bgnumber = (bgnumber % MAX_IMAGES) + 1;
    document.getElementById("student-container").style.backgroundImage = `url('assets/backgrounds/Background${bgnumber}.jpg')`;
    console.log("BACKGROUND CHANGED TO ", bgnumber);
}

spriteChangeBtn = document.getElementById("sprite-btn");
spriteChangeBtn.onclick = function() {
    if (SPRITE_COUNT == 3) {
        if (spriteType === "normal") {
            spriteType = "alt";
        } else if (spriteType === "alt") {
            spriteType = "alt2";
        } else {
            spriteType = "normal";
        }
    } 
    else {
        spriteType = spriteType === "normal" ? "alt" : "normal";
    }
    console.log("SPRITE TYPE CHANGED TO ", spriteType);
    updateStudentImage(lastEmotion); // Reset to neutral expression
};