
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

const stars = document.querySelectorAll('input[name="rating"]');

stars.forEach(star => {
    star.addEventListener('change', () => {
        stars.forEach(s => {
            const label = document.querySelector(`label[for="${s.id}"]`);
            label.classList.remove('text-yellow-500');
            label.classList.add('text-gray-400');
        });
        
        for (let i = 0; i < star.value; i++) {
            const label = document.querySelector(`label[for="star${i + 1}"]`);
            label.classList.remove('text-gray-400');
            label.classList.add('text-yellow-500');
        }
    });
});

async function refreshReviews() {
    document.getElementById("review_cards").innerHTML = "";
    document.getElementById("review_cards").className = "";
    const reviews = await getReviews();
    let htmlString = "";
    let classNameString = "";

    if (reviews.length === 0) {
        classNameString = "flex flex-col items-center justify-center min-h-[24rem] p-6";
        htmlString = `
            <div class="flex flex-col items-center justify-center min-h-[24rem] p-6">
                <p class="text-center text-gray-600 mt-4">Belum ada yang mereview seller.</p>
            </div>
        `;
    }
    else {
        classNameString = "columns-1 sm:columns-2 lg:columns-2 gap-6 space-y-6 w-full"
        reviews.slice(0,6).forEach((item) => {
            const reviewData = item.fields;
            const rating = reviewData.rating;
            const reviewer_pfp = reviewData.reviewer.user_profile.profile_picture;
            const reviewer_name = reviewData.reviewer.user_profile.user.username;
            const review = reviewData.review;
            const can_delete = reviewData.can_delete;
            const id = reviewData.id;
            const filledStars = `<svg xmlns="http://www.w3.org/2000/svg" width="26" height="25" viewBox="0 0 26 25" fill="none">
  <path d="M13.4745 3.84228L13 2.41487L12.5255 3.84228L10.3579 10.3634L3.48606 10.4098L1.98189 10.42L3.19282 11.3123L8.72497 15.389L6.64559 21.9389L6.19043 23.3726L7.4133 22.4967L13 18.495L18.5867 22.4967L19.8096 23.3726L19.3544 21.9389L17.275 15.389L22.8072 11.3123L24.0181 10.42L22.5139 10.4098L15.6421 10.3634L13.4745 3.84228Z" fill="#FFDB43" stroke="#FFDB43"/>
</svg>`;
            const emptyStars = `<svg xmlns="http://www.w3.org/2000/svg" width="26" height="25" viewBox="0 0 26 25" fill="none">
  <path d="M13.4745 3.84228L13 2.41487L12.5255 3.84228L10.3579 10.3634L3.48606 10.4098L1.98189 10.42L3.19282 11.3123L8.72497 15.389L6.64559 21.9389L6.19043 23.3726L7.4133 22.4967L13 18.495L18.5867 22.4967L19.8096 23.3726L19.3544 21.9389L17.275 15.389L22.8072 11.3123L24.0181 10.42L22.5139 10.4098L15.6421 10.3634L13.4745 3.84228Z" stroke="#FFDB43"/>
</svg>`;
            const starsHtml = 
                filledStars.repeat(rating) + 
                emptyStars.repeat(5 - rating);
            htmlString += `
                <div class="w-full bg-white shadow-md rounded-3xl p-6 max-h-64 overflow-hidden">
                    <div class="w-full flex justify-between items-center">
                        <div class="w-fit space-x-2 flex items-center">
                            <img src="${reviewer_pfp}" class="w-8 h-8 rounded-full">
                            <p class="albert-sans-semibold">${reviewer_name}</p>
                        </div>
                        <div class="w-fit space-x-1 flex">
                            ${starsHtml}
                        </div>
                    </div>
                    <div class="mt-4 max-h-full overflow-hidden">
                        <p class="overflow-hidden text-ellipsis" style="font-family:'Albert Sans', sans-serif; display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical;">
                            ${review}
                        </p>
                    </div>

                    ${can_delete ? `<button onclick="deleteReview('${id}')" class="text-red-500 hover:text-red-700 text-sm font-semibold">Delete</button>` : ""}
                </div>
                `;
            });
            htmlString +=`<div class="mt-4">
                        <a href="/profile/${sellerUsername}/reviews" class="albert-sans-semibold text-blue-600 font-semibold hover:underline">Selengkapnya →</a>
                    </div>`;
        }
        document.getElementById("review_cards").className = classNameString;
        document.getElementById("review_cards").innerHTML = htmlString;
    }
refreshReviews();



let reviewIdToDelete = null;

function deleteReview(reviewId) {
    reviewIdToDelete = reviewId;
    showConfirmDeleteModal();
}

function showConfirmDeleteModal() {
    const modal = document.getElementById("deleteReviewModal");
    const modalContent = document.getElementById("deleteReviewModalContent");

    modal.classList.remove("hidden");
    setTimeout(() => {
        modalContent.classList.remove("opacity-0", "scale-95");
        modalContent.classList.add("opacity-100", "scale-100");
    }, 50);
}

function hideConfirmDeleteModal() {
    const modal = document.getElementById("deleteReviewModal");
    const modalContent = document.getElementById("deleteReviewModalContent");

    modalContent.classList.remove("opacity-100", "scale-100");
    modalContent.classList.add("opacity-0", "scale-95");

    setTimeout(() => {
        modal.classList.add("hidden");
    }, 150);
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("confirmDeleteButton").addEventListener("click", async () => {
        try {
            const response = await fetch(`/profile/delete_review/${reviewIdToDelete}/`, { method: "POST" });
            if (response.ok) {
                refreshReviews();
            } else {
                alert("Failed to delete the review.");
            }
        } catch (error) {
            console.error("Error deleting review:", error);
        }
        hideConfirmDeleteModal();
    });

    document.getElementById("cancelDeleteButton").addEventListener("click", hideConfirmDeleteModal);
});

async function addReview() {
    try {
        const formData = new FormData(document.querySelector("#reviewForm"));
        formData.append("reviewee_username", sellerUsername); 

        const response = await fetch(`/profile/${sellerUsername}/add_review/`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) {
            throw new Error("Failed to add entry");
        }

        document.getElementById("reviewForm").reset();
        hideModal();
        refreshReviews();
    } catch (error) {
        console.error("Error creating forum entry:", error);
    }
}


document.getElementById("cancelButton").addEventListener("click", hideModal);
document.getElementById("closeModalBtn").addEventListener("click", hideModal);
document.getElementById("reviewForm").addEventListener("submit", (e) => {
    e.preventDefault();
    addReview();
  })