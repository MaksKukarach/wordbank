// static/js/main.js

// Global variables to track the current sub-exercise.
let currentExerciseIndex = 0;
let exercises = exercise.exercises;
let currentMatchingSelection = null;  // For word matching
let currentMatchingCount = 0;         // Count of correct matched pairs

// Render the current sub-exercise based on its type.
function displayCurrentExercise() {
  let container = document.getElementById("exercise-container");
  container.innerHTML = ""; // Clear previous content
  let current = exercises[currentExerciseIndex];
  let html = "";
  
  if (current.type === "word_matching") {
    html += `<div id="word-matching">
            <h3>Переведи слова!</h3>
            <div class="matching-container">
                <div class="column" id="source-column">`;
    current.learnable_words.forEach(word => {
      html += `<button class="brick source-brick" data-word="${word}" data-type="source" onclick="selectMatching(this)">${word}</button>`;
    });
    html += `</div>
                <div class="column" id="target-column">`;
    current.matching_target.forEach(word => {
      html += `<button class="brick target-brick" data-word="${word}" data-type="target" onclick="selectMatching(this)">${word}</button>`;
    });
    html += `</div></div>
            <a class="btn" onclick="submitCurrentExercise()">Отправить</a>
            </div>`;
  } else if (current.type === "sentence_assembly") {
    // In sentence assembly, display the original sentence (for context)
    html += `<div id="sentence-assembly">
           <p class="instruction-small">Соберите предложение, нажимая на переводы. Чтобы убрать слово, нажмите на него в собранном ответе.</p>
           <h1 class="main-sentence">${current.original_sentence}</h1>
           <div id="assembly-bricks">`;
    current.assembly_shuffled.forEach(word => {
      html += `<button class="brick" onclick="selectAssembly(this)">${word}</button>`;
    });
    html += `</div>
           <div id="assembly-result">
              <h3>Ваш перевод:</h3>
              <div id="assembledSentence"></div>
           </div>
           <a class="btn" onclick="submitCurrentExercise()">Отправить</a>
           </div>`;
  } else if (current.type === "reverse_assembly") {
    // In reverse assembly, display the translated sentence as context.
    html += `<div id="reverse-assembly">
           <p class="instruction-small">Соберите предложение, нажимая на слова. Чтобы убрать слово, нажмите на него в собранном ответе.</p>
           <h1 class="main-sentence">${current.translated_sentence}</h1>
           <div id="assembly-bricks">`;
    current.reverse_shuffled.forEach(word => {
      html += `<button class="brick" onclick="selectAssembly(this)">${word}</button>`;
    });
    html += `</div>
           <div id="assembly-result">
              <h3>Ваш ответ:</h3>
              <div id="assembledSentence"></div>
           </div>
           <a class="btn" onclick="submitCurrentExercise()">Отправить</a>
           </div>`;
  }
  
  container.innerHTML = html;
  // Reset selection variables for the new exercise.
  currentMatchingSelection = null;
  currentMatchingCount = 0;
}

// --- Word Matching Handlers ---
function selectMatching(element) {
  if (element.disabled) return;
  let type = element.getAttribute("data-type");
  if (!currentMatchingSelection) {
    currentMatchingSelection = { element: element, type: type, word: element.getAttribute("data-word") };
    element.classList.add("selected");
  } else {
    if (currentMatchingSelection.element === element) {
      element.classList.remove("selected");
      currentMatchingSelection = null;
      return;
    }
    if (currentMatchingSelection.type === type) {
      currentMatchingSelection.element.classList.remove("selected");
      currentMatchingSelection = { element: element, type: type, word: element.getAttribute("data-word") };
      element.classList.add("selected");
    } else {
      let isMatch = false;
      let current = exercises[currentExerciseIndex];
      if (currentMatchingSelection.type === "source" && type === "target") {
        if (current.translations[currentMatchingSelection.word] === element.getAttribute("data-word")) {
          isMatch = true;
        }
      }
      if (currentMatchingSelection.type === "target" && type === "source") {
        if (current.translations[element.getAttribute("data-word")] === currentMatchingSelection.word) {
          isMatch = true;
        }
      }
      if (isMatch) {
        currentMatchingSelection.element.disabled = true;
        element.disabled = true;
        currentMatchingSelection.element.classList.remove("selected");
        currentMatchingSelection.element.classList.add("matched");
        element.classList.add("matched");
        currentMatchingCount++;
        displayMessage("Правильно!", "success");
      } else {
        displayMessage("Неправильно, попробуйте снова.", "error");
        currentMatchingSelection.element.classList.remove("selected");
      }
      currentMatchingSelection = null;
    }
  }
}

// --- Assembly Handlers (for sentence and reverse assembly) ---
function selectAssembly(element) {
  // Check if already removed.
  if (element.dataset.removed === "true") return;
  
  // Mark as removed and remove from its container.
  element.dataset.removed = "true";
  let assemblyContainer = document.getElementById("assembly-bricks");
  assemblyContainer.removeChild(element);
  
  const word = element.textContent;
  const span = document.createElement("span");
  span.textContent = word;
  // Save a reference to the original button.
  span._button = element;
  
  // When the span is clicked, remove the span and reinsert the original button.
  span.onclick = function () {
    span.style.opacity = 0;
    setTimeout(() => {
      span.remove();
      assemblyContainer.appendChild(element);
      element.dataset.removed = "false";
    }, 200);
  };
  span.style.opacity = 0;
  document.getElementById("assembledSentence").appendChild(span);
  setTimeout(() => { span.style.opacity = 1; }, 50);
}

// --- Submission and Navigation ---
function submitCurrentExercise() {
  let current = exercises[currentExerciseIndex];
  let userAnswer;
  if (current.type === "word_matching") {
    // For word matching, answer is correct if all pairs are matched.
    userAnswer = (currentMatchingCount === current.learnable_words.length);
  } else if (current.type === "sentence_assembly") {
    userAnswer = [];
    document.querySelectorAll("#assembledSentence span").forEach(span => {
      userAnswer.push(span.textContent);
    });
  } else if (current.type === "reverse_assembly") {
    userAnswer = [];
    document.querySelectorAll("#assembledSentence span").forEach(span => {
      userAnswer.push(span.textContent);
    });
  }
  
  // Send answer to backend.
  fetch('/check_answer', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      exercise_index: currentExerciseIndex,
      exercise_type: current.type,
      user_answer: userAnswer,
      practiced_words: current.learnable_words
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.result === "correct") {
      displayMessage("Правильно!", "success");
      currentExerciseIndex++;
      if (currentExerciseIndex < exercises.length) {
        setTimeout(displayCurrentExercise, 1000);
      } else {
        displayMessage("Все упражнения выполнены!", "success");
        // Redirect to home screen after a short delay.
        setTimeout(() => {
          window.location.href = "/";
        }, 2000);
      }
    } else {
      displayMessage("Неправильно, попробуйте снова.", "error");
      // For assembly exercises, reinsert any removed buttons from the assembled area.
      if (current.type === "sentence_assembly" || current.type === "reverse_assembly") {
        const assembled = document.getElementById("assembledSentence");
        const assemblyContainer = document.getElementById("assembly-bricks");
        // For each span in the assembled area, reinsert the corresponding button.
        assembled.querySelectorAll("span").forEach(span => {
          let btn = span._button;
          if (btn) {
            assemblyContainer.appendChild(btn);
            btn.dataset.removed = "false";
          }
          span.remove();
        });
        // Also, re-enable any remaining buttons.
        document.querySelectorAll("#assembly-bricks .brick").forEach(btn => {
          btn.disabled = false;
          btn.classList.remove("selected");
        });
      }
    }
  });
}

function displayMessage(message, type) {
  const messageDiv = document.getElementById("message");
  messageDiv.textContent = message;
  messageDiv.className = "";
  messageDiv.classList.add(type === "success" ? "message-success" : "message-error");
  messageDiv.style.opacity = 1;
  messageDiv.style.display = "block";
  setTimeout(() => {
    messageDiv.style.opacity = 0;
    setTimeout(() => { messageDiv.style.display = "none"; }, 500);
  }, 2000);
}

// Initialize the first sub-exercise on page load.
window.onload = function () {
  displayCurrentExercise();
};
