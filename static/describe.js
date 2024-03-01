const descriptionInput = document.getElementById('description-input');
const tagContainer = document.getElementById('tag-container');
let tagsArray = [];

// Initialize tags from the session
try {
    tagsArray = JSON.parse(document.getElementById('tags-data').textContent);
} catch (e) {
    console.error('Error parsing tags:', e);
}

// Event listener for handling Enter key press in the description input
descriptionInput.addEventListener('keyup', function(event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Prevent the default action to handle the event within the custom function
        updateTagsFromInput();
        document.getElementById('description_form').submit(); // Submit the form directly
    }
});

// Updates tags based on the input field and displays them
function updateTagsFromInput() {
    const newTags = descriptionInput.value.split(',').map(tag => tag.trim().toLowerCase());
    newTags.forEach(tag => {
        if (!tagsArray.includes(tag) && tag !== "") {
            tagsArray.push(tag);
        }
    });
    displayTags();
}

// Displays tags as clickable elements in the tag container
function displayTags() {
    tagContainer.innerHTML = '';
    tagsArray.forEach(tag => {
        const tagElement = document.createElement('span');
        tagElement.className = 'tag';
        tagElement.innerText = tag;
        tagElement.onclick = function() {
            // Append tag to the description input when clicked, with comma only if input is not empty
            descriptionInput.value = descriptionInput.value ? descriptionInput.value + ', ' + tag : tag;
        };
        tagContainer.appendChild(tagElement);
    });
}

// Initial display of tags when the page loads
document.addEventListener('DOMContentLoaded', function() {
    displayTags();
});