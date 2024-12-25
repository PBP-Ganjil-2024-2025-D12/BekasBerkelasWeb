let currentQuestionId = null;
let currentReplyId = null;

function showDeleteModal(modalId) {
    const modal = document.getElementById(modalId);
    const modalContent = document.getElementById(`${modalId}Content`);

    modal.classList.remove("hidden");
    setTimeout(() => {
        modalContent.classList.remove("opacity-0", "scale-95");
        modalContent.classList.add("opacity-100", "scale-100");
    }, 50);
}

function hideDeleteModal(modalId) {
    const modal = document.getElementById(modalId);
    const modalContent = document.getElementById(`${modalId}Content`);

    modalContent.classList.remove("opacity-100", "scale-100");
    modalContent.classList.add("opacity-0", "scale-95");

    setTimeout(() => {
        modal.classList.add("hidden");
    }, 150);
}

window.deleteQuestion = function(questionId) {
    currentQuestionId = questionId;
    showDeleteModal('deleteQuestionModal');
}

window.deleteReply = function(questionId, replyId) {
    currentQuestionId = questionId;
    currentReplyId = replyId;
    showDeleteModal('deleteReplyModal');
}

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('confirmDeleteQuestion')?.addEventListener('click', async function() {
        try {
            const formData = new FormData();
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            formData.append('csrfmiddlewaretoken', csrfToken);

            const response = await fetch(`/forum/${currentQuestionId}/delete_question/`, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                window.location.href = '/forum/';
            } else {
                throw new Error('Failed to delete question');
            }
        } catch (error) {
            console.error('Error deleting question:', error);
        }
        hideDeleteModal('deleteQuestionModal');
    });

    document.getElementById('confirmDeleteReply')?.addEventListener('click', async function() {
        try {
            const formData = new FormData();
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            formData.append('csrfmiddlewaretoken', csrfToken);

            const response = await fetch(`/forum/${currentQuestionId}/delete_reply/${currentReplyId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                credentials: 'same-origin'
            });

            if (response.ok) {
                window.location.reload();
            } else {
                console.error('Failed to delete reply');
            }
        } catch (error) {
            console.error('Error:', error);
        }
        hideDeleteModal('deleteReplyModal');
    });

    document.querySelectorAll('.close-modal').forEach(button => {
        button.addEventListener('click', function() {
            const modalId = this.closest('[id$="Modal"]').id;
            hideDeleteModal(modalId);
        });
    });

    window.addEventListener('click', function(event) {
        const deleteQuestionModal = document.getElementById('deleteQuestionModal');
        const deleteReplyModal = document.getElementById('deleteReplyModal');
        
        if (event.target === deleteQuestionModal) {
            hideDeleteModal('deleteQuestionModal');
        }
        if (event.target === deleteReplyModal) {
            hideDeleteModal('deleteReplyModal');
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("car_search");
  const dropdown = document.getElementById("car_dropdown");
  const hiddenInput = document.getElementById("car_id");
  const options = dropdown.querySelectorAll(".car-option");
  const RESULTS_LIMIT = 5;
  let currentlyShown = 0;

  const showMoreButton = document.createElement("div");
  showMoreButton.className =
    "show-more-btn p-2 text-center text-indigo-600 hover:bg-indigo-50 cursor-pointer border-t";
  showMoreButton.textContent = "Selengkapnya";
  showMoreButton.style.display = "none";
  dropdown.appendChild(showMoreButton);

  function updateVisibleOptions(searchText = "") {
    let matchCount = 0;
    currentlyShown = 0;

    options.forEach((option) => {
      const label = option.getAttribute("data-label").toLowerCase();

      if (label.includes(searchText.toLowerCase())) {
        matchCount++;
        if (currentlyShown < RESULTS_LIMIT) {
          option.style.display = "block";
          currentlyShown++;
        } else {
          option.style.display = "none";
        }
      } else {
        option.style.display = "none";
      }
    });

    showMoreButton.style.display =
      matchCount > RESULTS_LIMIT ? "block" : "none";
  }

  function showAllMatching(searchText = "") {
    options.forEach((option) => {
      const label = option.getAttribute("data-label").toLowerCase();
      option.style.display = label.includes(searchText.toLowerCase())
        ? "block"
        : "none";
    });
    showMoreButton.style.display = "none";
  }

  searchInput.addEventListener("focus", () => {
    dropdown.classList.remove("hidden");
    updateVisibleOptions(searchInput.value);
  });

  document.addEventListener("click", (e) => {
    if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
      dropdown.classList.add("hidden");
    }
  });

  searchInput.addEventListener("input", (e) => {
    updateVisibleOptions(e.target.value);
  });

  options.forEach((option) => {
    option.addEventListener("click", () => {
      const value = option.getAttribute("data-value");
      const label = option.getAttribute("data-label");

      searchInput.value = label;
      hiddenInput.value = value;
      dropdown.classList.add("hidden");
    });
  });

  showMoreButton.addEventListener("click", () => {
    showAllMatching(searchInput.value);
  });

  updateVisibleOptions();
  loadQuestions();

  let searchTimeout;
  const forumSearchInput = document.querySelector(
    'input[placeholder="Cari Diskusi..."]'
  );
  forumSearchInput.addEventListener("input", function () {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => loadQuestions(), 300);
  });

  const filterSelects = document.querySelectorAll("select");
  filterSelects.forEach((select) => {
    select.addEventListener("change", () => loadQuestions());
  });

  const carEntryForm = document.getElementById("carEntryForm");
  carEntryForm.addEventListener("submit", (e) => {
    e.preventDefault();
    addForumEntry();
  });
});

function showModal() {
  const modal = document.getElementById("crudModal");
  const modalContent = document.getElementById("crudModalContent");

  modal.classList.remove("hidden");
  setTimeout(() => {
    modalContent.classList.remove("opacity-0", "scale-95");
    modalContent.classList.add("opacity-100", "scale-100");
  }, 50);
}

function hideModal() {
  const modal = document.getElementById("crudModal");
  const modalContent = document.getElementById("crudModalContent");

  modalContent.classList.remove("opacity-100", "scale-100");
  modalContent.classList.add("opacity-0", "scale-95");

  setTimeout(() => {
    modal.classList.add("hidden");
  }, 150);
}

function getCategoryLabel(category) {
  const categories = {
    UM: "Umum",
    JB: "Jual Beli",
    TT: "Tips & Trik",
    SA: "Santai",
  };
  return categories[category] || category;
}

function createForumCard(question) {
  const categoryLabel = getCategoryLabel(question.fields.category);
  const categoryColorClass = {
      UM: "bg-blue-100 text-blue-800 albert-sans-semibold",
      JB: "bg-green-100 text-green-800 albert-sans-semibold",
      TT: "bg-purple-100 text-purple-800 albert-sans-semibold",
      SA: "bg-yellow-100 text-yellow-800 albert-sans-semibold",
  }[question.fields.category] || "bg-gray-100 text-gray-800 albert-sans-semibold";

  const sanitizedContent = DOMPurify.sanitize(question.fields.content);

  return `
      <div class="p-4 hover:bg-gray-50 transition duration-150 ease-in-out">
          <div class="flex items-start space-x-4">
              <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-2 mb-1">
                      <span class="px-2.5 py-0.5 rounded-full text-xs ${categoryColorClass}">
                          ${categoryLabel}
                      </span>
                      <span class="text-sm text-gray-500">${question.fields.created_at}</span>
                  </div>
                  <a href="/forum/${question.pk}" class="block">
                      <h3 class="text-lg font-semibold text-gray-900 hover:text-blue-600 mb-2 truncate">
                          ${question.fields.title}
                      </h3>
                  </a>
                  <div class="content-wrapper">
                      <p class="text-gray-600 mb-3 truncate-2-lines">${sanitizedContent}</p>
                  </div>
                  <div class="flex items-center justify-between">
                      <div class="flex items-center space-x-4">
                          <div class="flex items-center text-sm text-gray-500">
                              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z">
                                  </path>
                              </svg>
                              ${question.fields.username}
                          </div>
                          <div class="flex items-center text-sm text-gray-500">
                              <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                      d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z">
                                  </path>
                              </svg>
                              ${question.fields.reply_count} balasan
                          </div>
                      </div>
                      <a href="/forum/${question.pk}" class="flex items-center text-sm text-blue-600 hover:text-blue-800 albert-sans-semibold group">
                          <span class="mr-1">Selengkapnya</span>
                          <svg class="w-4 h-4 transform transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                          </svg>
                      </a>
                  </div>
              </div>
          </div>
      </div>
  `;
}

function createPagination(totalPages, currentPage) {
  let paginationHTML = '<div class="flex justify-center space-x-2">';

  paginationHTML += `
        <button class="px-3 py-1 rounded-md ${
          currentPage === 1
            ? "bg-gray-100 text-gray-400 cursor-not-allowed"
            : "bg-white text-gray-700 hover:bg-gray-50"
        }"
            ${currentPage === 1 ? "disabled" : ""} onclick="loadQuestions(${
    currentPage - 1
  })">
            Previous
        </button>
    `;

  for (let i = 1; i <= totalPages; i++) {
    paginationHTML += `
            <button class="px-3 py-1 rounded-md ${
              currentPage === i
                ? "bg-blue-500 text-white"
                : "bg-white text-gray-700 hover:bg-gray-50"
            }"
                onclick="loadQuestions(${i})">
                ${i}
            </button>
        `;
  }

  paginationHTML += `
        <button class="px-3 py-1 rounded-md ${
          currentPage === totalPages
            ? "bg-gray-100 text-gray-400 cursor-not-allowed"
            : "bg-white text-gray-700 hover:bg-gray-50"
        }"
            ${
              currentPage === totalPages ? "disabled" : ""
            } onclick="loadQuestions(${currentPage + 1})">
            Next
        </button>
    </div>`;

  return paginationHTML;
}

async function loadQuestions(page = 1) {
  const searchQuery = document.querySelector(
    'input[placeholder="Cari Diskusi..."]'
  ).value;
  const categorySelect = document.querySelector(
    'select[name="filter_category"]'
  );
  const sortSelect = document.querySelector('select[name="filter_sort"]');

  const params = new URLSearchParams({
    page: page,
    search: searchQuery,
    category: categorySelect.value,
    sort: sortSelect.value,
  });

  try {
    const response = await fetch(`/forum/get_questions_json/?${params}`);
    const data = await response.json();

    const questionsContainer = document.getElementById("questionsContainer");
    const paginationContainer = document.getElementById("paginationContainer");

    if (data.questions.length === 0) {
      const selectedCategory =
        categorySelect.options[categorySelect.selectedIndex].text;
      questionsContainer.innerHTML = `
                <div class="p-8 text-center">
                    <div class="mb-4">
                        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                                d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z">
                            </path>
                        </svg>
                    </div>
                    <p class="text-gray-600 text-lg">Belum ada diskusi ${
                      categorySelect.value === ""
                        ? "untuk Semua Kategori"
                        : `untuk kategori ${selectedCategory}`
                    }</p>
                </div>
            `;
      paginationContainer.innerHTML = "";
    } else {
      questionsContainer.innerHTML = data.questions
        .map((question) => createForumCard(question))
        .join("");

      paginationContainer.innerHTML = createPagination(
        data.total_pages,
        data.current_page
      );
    }
  } catch (error) {
    console.error("Error loading questions:", error);
    questionsContainer.innerHTML = `
            <div class="p-8 text-center">
                <p class="text-red-600">Terjadi kesalahan saat memuat diskusi. Silakan coba lagi nanti.</p>
            </div>
        `;
    paginationContainer.innerHTML = "";
  }
}

async function addForumEntry() {
  try {
      const response = await fetch("/forum/create_question/", {
          method: "POST",
          body: new FormData(document.querySelector("#carEntryForm")),
      });

      if (response.ok) {
          document.getElementById("carEntryForm").reset();
          hideModal();
          loadQuestions();
      } else {
          window.location.reload();
      }
  } catch (error) {
      window.location.reload();
  }
}

document.getElementById("cancelButton").addEventListener("click", hideModal);
document.getElementById("closeModalBtn").addEventListener("click", hideModal);
