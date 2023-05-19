function addFilters() {
    // console.log("Adding filters...");
    hs = document.getElementsByClassName("post");
    tags = new Set();
    for (let h of hs) {
        local_tags = h.dataset['tags'].split(' ');
        console.log(local_tags);
        local_tags.forEach((tag) => {
            tags.add(tag);
        });
    }
    // console.log(tags);

    sorted_tags = Array.from(tags);
    sorted_tags.sort();

    let intro = document.getElementById("filter-list");
    // console.log(intro);
    sorted_tags.forEach((tag) => {
        tag_input = document.createElement("input");
        tag_input.classList.add("tag-filter");

        tag_input.type = "button";
        tag_input.value = tag;
        tag_input.onclick = toggleButton;
        intro.appendChild(tag_input);
    });
}

function toggleButton(event) {
    event.target.classList.toggle("selected");
    filterContentItems();
}

function filterContentItems(tag, resetFilters=false) {
    let allContent = document.querySelectorAll("article.post");
    allContent.forEach((element) => {
        element.classList.remove("hidden");
    });
    
    let enabledFilters = document.querySelectorAll("input[type='button'].tag-filter.selected");
        
    if (resetFilters) {
        enabledFilters.forEach((element) => {
            element.classList.remove("selected");
        });
    }
    if (tag === undefined) {
        // console.log("Enabled filter count:", enabledFilters.length);
        if (enabledFilters.length > 0) {
            for (let enabledFilter of enabledFilters) {
                filterContentItemByTag(enabledFilter.value);
            }
        }
    } else {
        filterContentItemByTag(tag);
    }
}

function filterContentItemByTag(tag) {
    let allContent = document.querySelectorAll("article.post");
    for (let contentItem of allContent) {
        let tags = contentItem.dataset['tags'];
        if (tags.search(tag) === -1) {
            contentItem.classList.add("hidden");
        }
    }
}

window.onload = function(event) {
    console.log("Document has finished loading...");
    addFilters();
}
console.log("Loaded...");