const API_URL = "http://127.0.0.1:8000";


let currentFilePath = null;
let totalPages = 0;
let selectedPage = 1;


/* =========================================
   ELEMENTS
========================================= */

const pdfInput =
    document.getElementById("pdfInput");

const pdfInputLarge =
    document.getElementById("pdfInputLarge");

const pageList =
    document.getElementById("pageList");

const pageImage =
    document.getElementById("pageImage");

const emptyPreview =
    document.getElementById("emptyPreview");

const pdfPreview =
    document.getElementById("pdfPreview");

const pageCount =
    document.getElementById("pageCount");

const currentPageText =
    document.getElementById("currentPageText");

const editorStatus =
    document.getElementById("editorStatus");


const rotateLeftButton =
    document.getElementById(
        "rotateLeftButton"
    );

const rotateRightButton =
    document.getElementById(
        "rotateRightButton"
    );

const insertButton =
    document.getElementById(
        "insertButton"
    );

const deleteButton =
    document.getElementById(
        "deleteButton"
    );

const saveButton =
    document.getElementById(
        "saveButton"
    );

const insertInput =
    document.getElementById(
        "insertInput"
    );


/* =========================================
   BACK BUTTON
========================================= */

document
    .getElementById("backButton")
    .addEventListener(
        "click",
        function () {

            window.location.href =
                "index.html";

        }
    );


/* =========================================
   OPEN PDF
========================================= */

pdfInput.addEventListener(
    "change",
    function () {

        if (this.files.length === 0) {
            return;
        }

        openPDF(
            this.files[0]
        );

    }
);


pdfInputLarge.addEventListener(
    "change",
    function () {

        if (this.files.length === 0) {
            return;
        }

        openPDF(
            this.files[0]
        );

    }
);


async function openPDF(file) {

    editorStatus.textContent =
        "Opening PDF...";


    const formData =
        new FormData();


    formData.append(
        "file",
        file
    );


    try {

        const response =
            await fetch(
                `${API_URL}/editor/open`,
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {

            const error =
                await response.json();

            throw new Error(
                error.detail ||
                "Unable to open PDF"
            );

        }


        const data =
            await response.json();


        currentFilePath =
            data.file_path;

        totalPages =
            data.total_pages;


        pageCount.textContent =
            totalPages;


        editorStatus.textContent =
            `${data.filename} opened`;


        enableEditorButtons();


        emptyPreview.style.display =
            "none";


        pdfPreview.style.display =
            "flex";


        createPageList();


        selectPage(1);


    } catch (error) {

        console.error(error);

        alert(
            "Could not open PDF: " +
            error.message
        );

        editorStatus.textContent =
            "Failed to open PDF";

    }

}


/* =========================================
   CREATE PAGE LIST
========================================= */

function createPageList() {

    pageList.innerHTML = "";


    for (
        let i = 1;
        i <= totalPages;
        i++
    ) {

        const pageItem =
            document.createElement("div");


        pageItem.className =
            "page-item";


        pageItem.dataset.page =
            i;


        const thumbnail =
            document.createElement("div");


        thumbnail.className =
            "page-thumbnail";


        const image =
            document.createElement("img");


        image.alt =
            `Page ${i}`;


        /*
         * Page endpoint uses 0-based
         * page number.
         */

        const imageURL =
            getPageURL(i - 1);


        image.src =
            imageURL;


        thumbnail.appendChild(
            image
        );


        const pageNumber =
            document.createElement("span");


        pageNumber.className =
            "page-number";


        pageNumber.textContent =
            `Page ${i}`;


        pageItem.appendChild(
            thumbnail
        );


        pageItem.appendChild(
            pageNumber
        );


        pageItem.addEventListener(
            "click",
            function () {

                selectPage(i);

            }
        );


        pageList.appendChild(
            pageItem
        );

    }

}


/* =========================================
   SELECT PAGE
========================================= */

function selectPage(pageNumber) {

    if (
        pageNumber < 1 ||
        pageNumber > totalPages
    ) {
        return;
    }


    selectedPage =
        pageNumber;


    document
        .querySelectorAll(
            ".page-item"
        )
        .forEach(
            item => {

                item.classList.toggle(
                    "selected",
                    Number(
                        item.dataset.page
                    ) === pageNumber
                );

            }
        );


    currentPageText.textContent =
        `Page ${pageNumber} of ${totalPages}`;


    pageImage.src =
        getPageURL(
            pageNumber - 1
        );

}


/* =========================================
   PAGE URL
========================================= */

function getPageURL(pageNumber) {

    return (
        `${API_URL}/editor/page` +
        `?file_path=${encodeURIComponent(
            currentFilePath
        )}` +
        `&page_number=${pageNumber}` +
        `&t=${Date.now()}`
    );

}


/* =========================================
   ENABLE BUTTONS
========================================= */

function enableEditorButtons() {

    rotateLeftButton.disabled =
        false;

    rotateRightButton.disabled =
        false;

    insertButton.disabled =
        false;

    deleteButton.disabled =
        totalPages <= 1;

    saveButton.disabled =
        false;

}


/* =========================================
   ROTATE LEFT
========================================= */

rotateLeftButton.addEventListener(
    "click",
    async function () {

        await rotatePage(
            "counterclockwise"
        );

    }
);


/* =========================================
   ROTATE RIGHT
========================================= */

rotateRightButton.addEventListener(
    "click",
    async function () {

        await rotatePage(
            "clockwise"
        );

    }
);


/* =========================================
   ROTATE PAGE
========================================= */

async function rotatePage(direction) {

    if (!currentFilePath) {
        return;
    }


    editorStatus.textContent =
        "Rotating page...";


    const formData =
        new FormData();


    formData.append(
        "file_path",
        currentFilePath
    );


    formData.append(
        "page_number",
        selectedPage
    );


    formData.append(
        "direction",
        direction
    );


    try {

        const response =
            await fetch(
                `${API_URL}/editor/rotate`,
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {

            const error =
                await response.json();

            throw new Error(
                error.detail
            );

        }


        const data =
            await response.json();


        currentFilePath =
            data.file_path;


        totalPages =
            data.total_pages;


        pageCount.textContent =
            totalPages;


        createPageList();


        selectPage(
            selectedPage
        );


        editorStatus.textContent =
            "Page rotated successfully";


    } catch (error) {

        console.error(error);

        alert(
            "Rotation failed: " +
            error.message
        );

    }

}


/* =========================================
   DELETE PAGE
========================================= */

deleteButton.addEventListener(
    "click",
    async function () {

        if (!currentFilePath) {
            return;
        }


        const confirmed =
            confirm(
                `Delete page ${selectedPage}?`
            );


        if (!confirmed) {
            return;
        }


        editorStatus.textContent =
            "Deleting page...";


        const formData =
            new FormData();


        formData.append(
            "file_path",
            currentFilePath
        );


        formData.append(
            "page_numbers",
            selectedPage
        );


        try {

            const response =
                await fetch(
                    `${API_URL}/editor/delete`,
                    {
                        method: "POST",
                        body: formData
                    }
                );


            if (!response.ok) {

                const error =
                    await response.json();

                throw new Error(
                    error.detail
                );

            }


            const data =
                await response.json();


            currentFilePath =
                data.file_path;


            totalPages =
                data.total_pages;


            pageCount.textContent =
                totalPages;


            createPageList();


            /*
             * If deleted last page,
             * select previous page.
             */

            if (
                selectedPage >
                totalPages
            ) {

                selectedPage =
                    totalPages;

            }


            selectPage(
                selectedPage
            );


            editorStatus.textContent =
                "Page deleted successfully";


        } catch (error) {

            console.error(error);

            alert(
                "Delete failed: " +
                error.message
            );

        }

    }
);


/* =========================================
   INSERT PDF
========================================= */

insertButton.addEventListener(
    "click",
    function () {

        insertInput.click();

    }
);


insertInput.addEventListener(
    "change",
    async function () {

        if (this.files.length === 0) {
            return;
        }


        const file =
            this.files[0];


        /*
         * Insert BEFORE selected page.
         *
         * Example:
         * selected page = 3
         * inserted PDF goes before page 3.
         */

        const position =
            selectedPage;


        editorStatus.textContent =
            "Inserting PDF...";


        const formData =
            new FormData();


        formData.append(
            "file_path",
            currentFilePath
        );


        formData.append(
            "position",
            position
        );


        formData.append(
            "file",
            file
        );


        try {

            const response =
                await fetch(
                    `${API_URL}/editor/insert`,
                    {
                        method: "POST",
                        body: formData
                    }
                );


            if (!response.ok) {

                const error =
                    await response.json();

                throw new Error(
                    error.detail
                );

            }


            const data =
                await response.json();


            currentFilePath =
                data.file_path;


            totalPages =
                data.total_pages;


            pageCount.textContent =
                totalPages;


            createPageList();


            selectPage(
                selectedPage
            );


            editorStatus.textContent =
                "PDF inserted successfully";


        } catch (error) {

            console.error(error);

            alert(
                "Insert failed: " +
                error.message
            );

        }


        /*
         * Reset input so the same PDF
         * can be selected again.
         */

        this.value = "";

    }
);


/* =========================================
   SAVE PDF
========================================= */

saveButton.addEventListener(
    "click",
    function () {

        if (!currentFilePath) {
            return;
        }


        const url =
            `${API_URL}/editor/save` +
            `?file_path=${encodeURIComponent(
                currentFilePath
            )}`;


        const link =
            document.createElement("a");


        link.href =
            url;


        link.download =
            "edited.pdf";


        document.body.appendChild(
            link
        );


        link.click();


        link.remove();


        editorStatus.textContent =
            "PDF downloaded";

    }
);