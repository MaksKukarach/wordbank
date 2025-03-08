// static/js/main.js

let currentExerciseIndex = 0;
let exercises = exercise.exercises;
let currentMatchingSelection = null;  
let currentMatchingCount = 0;

// For fill in blanks exercise: store user inputs in an array.
let fillAnswers = [];
// For word options exercise: store selected answer.
let wordOptionAnswer = "";

function displayCurrentExercise() {
  let container = document.getElementById("exercise-container");
  container.innerHTML = "";
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
              <a class="btn skip-btn" onclick="skipExercise()">Пропустить</a>
            </div>`;
  } else if (current.type === "sentence_assembly") {
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
              <a class="btn skip-btn" onclick="skipExercise()">Пропустить</a>
            </div>`;
  } else if (current.type === "reverse_assembly") {
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
              <a class="btn skip-btn" onclick="skipExercise()">Пропустить</a>
            </div>`;
  } else if (current.type === "fill_in_blanks") {
    // The backend returns a fill_in_sentence string with "___" for blanks.
    let parts = current.fill_in_sentence.split("___");
    let blanksCount = parts.length - 1;
    fillAnswers = new Array(blanksCount).fill("");
    html += `<div id="fill-in-blanks">
              <p class="instruction-small">Заполните пропуски, кликнув по ним для ввода.</p>
              <h1 class="main-sentence">`;
    for (let i = 0; i < parts.length; i++) {
      html += parts[i];
      if (i < blanksCount) {
        // The blank is rendered as an inline span that will turn into an input on click.
        html += `<span class="blank" data-index="${i}" onclick="editBlank(this)">______</span>`;
      }
    }
    html += `</h1>
             <h2 class="instruction-small">Перевод: ${current.translated_sentence}</h2>
             <a class="btn" onclick="submitCurrentExercise()">Отправить</a>
             <a class="btn skip-btn" onclick="skipExercise()">Пропустить</a>
             </div>`;
  } else if (current.type === "word_options") {
    html += `<div id="word-options">
              <p class="instruction-small">Выберите правильное слово по переводу:</p>
              <h2 class="main-sentence">"${current.prompt_translation}"</h2>
              <div id="options-container">`;
    current.options.forEach(option => {
      html += `<button class="brick" onclick="selectWordOption(this)">${option}</button>`;
    });
    html += `</div>
              <a class="btn" onclick="submitCurrentExercise()">Отправить</a>
              <a class="btn skip-btn" onclick="skipExercise()">Пропустить</a>
            </div>`;
  }
  
  container.innerHTML = html;
  // Reset variables.
  currentMatchingSelection = null;
  currentMatchingCount = 0;
  wordOptionAnswer = "";
}

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

function selectAssembly(element) {
  if (element.dataset.removed === "true") return;
  element.dataset.removed = "true";
  let assemblyContainer = document.getElementById("assembly-bricks");
  assemblyContainer.removeChild(element);
  const word = element.textContent;
  const span = document.createElement("span");
  span.textContent = word;
  span._button = element;
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

function selectWordOption(button) {
  let options = document.querySelectorAll("#options-container .brick");
  options.forEach(opt => opt.classList.remove("selected"));
  button.classList.add("selected");
  wordOptionAnswer = button.textContent;
}

function editBlank(blankElement) {
  let index = blankElement.getAttribute("data-index");
  let input = document.createElement("input");
  input.type = "text";
  input.className = "blank-input";
  // If there's already a value saved in fillAnswers, use it.
  input.value = fillAnswers[index] || "";
  blankElement.innerHTML = "";
  blankElement.appendChild(input);
  input.focus();
  input.addEventListener("blur", function() {
    let val = input.value.trim();
    fillAnswers[index] = val;
    blankElement.textContent = val === "" ? "______" : val;
  });
  input.addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
      input.blur();
    }
  });
}

function submitCurrentExercise() {
  let current = exercises[currentExerciseIndex];
  let userAnswer;
  if (current.type === "word_matching") {
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
  } else if (current.type === "fill_in_blanks") {
    // Collect answers from all blanks. For blanks that never turned into an input, treat them as empty.
    userAnswer = [];
    let blanks = document.querySelectorAll(".blank");
    blanks.forEach(blank => {
      // Check if there's an input inside the blank.
      let input = blank.querySelector("input");
      if (input) {
        userAnswer.push(input.value.trim());
      } else {
        let text = blank.textContent.trim();
        userAnswer.push(text === "______" ? "" : text);
      }
    });
  } else if (current.type === "word_options") {
    userAnswer = wordOptionAnswer;
  }
  
  console.log("User answer:", userAnswer);
  
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
        setTimeout(() => { window.location.href = "/"; }, 2000);
      }
    } else {
      displayMessage("Неправильно, попробуйте снова.", "error");
      // Reset for assembly exercises.
      if (current.type === "sentence_assembly" || current.type === "reverse_assembly") {
        const assembled = document.getElementById("assembledSentence");
        const assemblyContainer = document.getElementById("assembly-bricks");
        assembled.querySelectorAll("span").forEach(span => {
          let btn = span._button;
          if (btn) {
            assemblyContainer.appendChild(btn);
            btn.dataset.removed = "false";
          }
          span.remove();
        });
        document.querySelectorAll("#assembly-bricks .brick").forEach(btn => {
          btn.disabled = false;
          btn.classList.remove("selected");
        });
      }
      if (current.type === "fill_in_blanks") {
        // Clear each blank input.
        document.querySelectorAll(".blank-input").forEach(input => {
          input.value = "";
        });
      }
      if (current.type === "word_options") {
        let options = document.querySelectorAll("#options-container .brick");
        options.forEach(opt => opt.classList.remove("selected"));
        wordOptionAnswer = "";
      }
    }
  });
}

function skipExercise() {
  displayMessage("Упражнение пропущено", "info");
  currentExerciseIndex++;
  if (currentExerciseIndex < exercises.length) {
    setTimeout(displayCurrentExercise, 1000);
  } else {
    displayMessage("Все упражнения выполнены!", "success");
    setTimeout(() => { window.location.href = "/"; }, 2000);
  }
}

function displayMessage(message, type) {
  const messageDiv = document.getElementById("message");
  messageDiv.textContent = message;
  messageDiv.className = "";
  messageDiv.classList.add(type === "success" ? "message-success" : (type === "info" ? "message-info" : "message-error"));
  messageDiv.style.opacity = 1;
  messageDiv.style.display = "block";
  setTimeout(() => {
    messageDiv.style.opacity = 0;
    setTimeout(() => { messageDiv.style.display = "none"; }, 500);
  }, 2000);
}

window.onload = function () {
  displayCurrentExercise();
};
