// ========================================
// MERGE PDF
// ========================================

const pdfInput = document.getElementById("pdfFiles");
const mergeButton = document.getElementById("mergeButton");

const fileList = document.getElementById("fileList");
const status = document.getElementById("status");


pdfInput.addEventListener("change", function () {

    fileList.innerHTML = "";

    const files = pdfInput.files;

    for (const file of files) {

        const item = document.createElement("p");

        item.innerText = file.name;

        fileList.appendChild(item);
    }

});


mergeButton.addEventListener("click", async function () {

    const files = pdfInput.files;


    if (files.length < 2) {

        status.innerText =
            "Please select at least 2 PDF files.";

        return;
    }


    const formData = new FormData();


    for (const file of files) {

        formData.append("files", file);

    }


    status.innerText = "Merging PDFs...";


    try {

        const response = await fetch(
            "http://127.0.0.1:8000/merge/",
            {
                method: "POST",
                body: formData
            }
        );


        if (!response.ok) {

            const error = await response.json();

            status.innerText =
                error.detail || "Merge failed.";

            return;
        }


        const blob = await response.blob();


        const url =
            window.URL.createObjectURL(blob);


        const link =
            document.createElement("a");


        link.href = url;

        link.download = "merged.pdf";


        document.body.appendChild(link);

        link.click();

        link.remove();


        window.URL.revokeObjectURL(url);


        status.innerText =
            "PDFs merged successfully!";


    } catch (error) {

        console.error(error);

        status.innerText =
            "Could not connect to backend.";

    }

});


// ========================================
// EXTRACT PDF
// ========================================

const extractPdf =
    document.getElementById("extractPdf");

const pdfInfo =
    document.getElementById("pdfInfo");

const pdfPreview =
    document.getElementById("pdfPreview");

const previewContainer =
    document.getElementById("previewContainer");

const previousPage =
    document.getElementById("previousPage");

const nextPage =
    document.getElementById("nextPage");

const pageNumber =
    document.getElementById("pageNumber");

const startPage =
    document.getElementById("startPage");

const endPage =
    document.getElementById("endPage");

const extractButton =
    document.getElementById("extractButton");


let selectedPdf = null;

let totalPages = 0;

let currentPage = 1;


// ========================================
// PDF SELECTED
// ========================================

extractPdf.addEventListener(
    "change",
    async function () {

        const file = extractPdf.files[0];


        if (!file) {

            return;

        }


        selectedPdf = file;

        currentPage = 1;


        pdfInfo.innerText =
            "Loading PDF...";


        try {

            // Get total pages

            const formData =
                new FormData();

            formData.append(
                "file",
                file
            );


            const response =
                await fetch(
                    "http://127.0.0.1:8000/extract/info",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Could not read PDF"
                );

            }


            const data =
                await response.json();


            totalPages =
                data.total_pages;


            pdfInfo.innerText =
                `Total Pages: ${totalPages}`;


            // Set range inputs

            startPage.max =
                totalPages;

            endPage.max =
                totalPages;

            endPage.value =
                totalPages;


            // Enable navigation

            previousPage.disabled = true;

            nextPage.disabled =
                totalPages <= 1;


            updatePageNumber();


            // Show first page

            await loadPreview();


        } catch (error) {

            console.error(error);

            pdfInfo.innerText =
                "Could not load PDF.";

        }

    }
);


// ========================================
// LOAD PDF PREVIEW
// ========================================

async function loadPreview() {

    if (!selectedPdf) {

        return;

    }


    const formData =
        new FormData();


    formData.append(
        "file",
        selectedPdf
    );


    try {

        const response =
            await fetch(
                `http://127.0.0.1:8000/extract/preview?page=${currentPage}`,
                {
                    method: "POST",
                    body: formData
                }
            );


        if (!response.ok) {

            throw new Error(
                "Preview failed"
            );

        }


        const blob =
            await response.blob();


        const imageUrl =
            window.URL.createObjectURL(blob);


        pdfPreview.src =
            imageUrl;


        previewContainer.style.display =
            "block";


        updatePageNumber();


    } catch (error) {

        console.error(error);

        status.innerText =
            "Could not preview PDF.";

    }

}


// ========================================
// UPDATE PAGE NUMBER
// ========================================

function updatePageNumber() {

    pageNumber.innerText =
        `Page ${currentPage} / ${totalPages}`;


    previousPage.disabled =
        currentPage <= 1;


    nextPage.disabled =
        currentPage >= totalPages;

}


// ========================================
// PREVIOUS PAGE
// ========================================

previousPage.addEventListener(
    "click",
    async function () {

        if (currentPage <= 1) {

            return;

        }


        currentPage--;

        updatePageNumber();

        await loadPreview();

    }
);


// ========================================
// NEXT PAGE
// ========================================

nextPage.addEventListener(
    "click",
    async function () {

        if (currentPage >= totalPages) {

            return;

        }


        currentPage++;

        updatePageNumber();

        await loadPreview();

    }
);


// ========================================
// EXTRACT PAGES
// ========================================

extractButton.addEventListener(
    "click",
    async function () {

        if (!selectedPdf) {

            status.innerText =
                "Please select a PDF.";

            return;

        }


        const start =
            parseInt(startPage.value);

        const end =
            parseInt(endPage.value);


        if (
            isNaN(start) ||
            isNaN(end)
        ) {

            status.innerText =
                "Please enter valid page numbers.";

            return;

        }


        if (
            start < 1 ||
            end > totalPages ||
            start > end
        ) {

            status.innerText =
                `Please enter a valid range between 1 and ${totalPages}.`;

            return;

        }


        const formData =
            new FormData();


        formData.append(
            "file",
            selectedPdf
        );


        status.innerText =
            "Extracting pages...";


        try {

            const response =
                await fetch(
                    `http://127.0.0.1:8000/extract/pages?start_page=${start}&end_page=${end}`,
                    {
                        method: "POST",
                        body: formData
                    }
                );


            if (!response.ok) {

                const error =
                    await response.json();


                status.innerText =
                    error.detail ||
                    "Extraction failed.";

                return;

            }


            const blob =
                await response.blob();


            const url =
                window.URL.createObjectURL(blob);


            const link =
                document.createElement("a");


            link.href = url;

            link.download =
                `extracted_pages_${start}-${end}.pdf`;


            document.body.appendChild(link);

            link.click();

            link.remove();


            window.URL.revokeObjectURL(url);


            status.innerText =
                `Pages ${start} to ${end} extracted successfully!`;


        } catch (error) {

            console.error(error);

            status.innerText =
                "Could not connect to backend.";

        }

    }
);

// ========================================
// SEARCH PDF
// ========================================

const searchPdfFile =
    document.getElementById("searchPdfFile");

const searchText =
    document.getElementById("searchText");

const searchButton =
    document.getElementById("searchButton");

const searchFileName =
    document.getElementById("searchFileName");

const searchResults =
    document.getElementById("searchResults");


// Show selected PDF
searchPdfFile.addEventListener(
    "change",
    function () {

        searchResults.innerHTML = "";

        if (searchPdfFile.files.length === 0) {

            searchFileName.innerText = "";

            return;
        }

        const file =
            searchPdfFile.files[0];

        searchFileName.innerText =
            file.name;
    }
);


// Search button
searchButton.addEventListener(
    "click",
    async function () {

        const file =
            searchPdfFile.files[0];

        const query =
            searchText.value.trim();


        // Validate PDF
        if (!file) {

            searchResults.innerHTML =
                "<p>Please select a PDF file.</p>";

            return;
        }


        // Validate search text
        if (!query) {

            searchResults.innerHTML =
                "<p>Please enter text to search.</p>";

            return;
        }


        const formData =
            new FormData();


        formData.append(
            "file",
            file
        );

        formData.append(
            "search_text",
            query
        );


        searchResults.innerHTML =
            "<p>Searching PDF...</p>";


        try {

            const response =
                await fetch(
                    "http://127.0.0.1:8000/search/",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            if (!response.ok) {

                const error =
                    await response.json();

                searchResults.innerHTML =
                    `<p>${error.detail || "Search failed."}</p>`;

                return;
            }


            const data =
                await response.json();


            displaySearchResults(data);


        } catch (error) {

            console.error(error);

            searchResults.innerHTML =
                "<p>Could not connect to backend.</p>";
        }
    }
);

function displaySearchResults(data) {

    searchResults.innerHTML = "";


    // No matches
    if (data.total_matches === 0) {

        searchResults.innerHTML = `
            <div class="search-summary">
                No matches found for
                "<strong>${escapeHtml(data.query)}</strong>"
            </div>
        `;

        return;
    }


    // Summary
    const summary =
        document.createElement("div");

    summary.className =
        "search-summary";

    summary.innerHTML = `
        Found
        <strong>${data.total_matches}</strong>
        match(es) for
        "<strong>${escapeHtml(data.query)}</strong>"
    `;

    searchResults.appendChild(summary);


    // Page results
    const resultList =
        document.createElement("div");

    resultList.className =
        "search-result-list";


    data.results.forEach(
        function (result) {

            const item =
                document.createElement("div");

            item.className =
                "search-result-item";

            item.innerHTML = `
                <span>
                    Page ${result.page}
                </span>

                <span>
                    ${result.matches} match(es)
                </span>
            `;

            resultList.appendChild(item);
        }
    );


    searchResults.appendChild(resultList);
}


// Prevent HTML injection
function escapeHtml(text) {

    const div =
        document.createElement("div");

    div.innerText = text;

    return div.innerHTML;
}

// ========================================
// COMPRESS PDF
// ========================================

const compressPdfFile =
    document.getElementById("compressPdfFile");

const compressFileName =
    document.getElementById("compressFileName");

const compressionQuality =
    document.getElementById("compressionQuality");

const compressButton =
    document.getElementById("compressButton");

const compressStatus =
    document.getElementById("compressStatus");


// Show selected file
compressPdfFile.addEventListener(
    "change",
    function () {

        compressStatus.innerHTML = "";

        if (compressPdfFile.files.length === 0) {

            compressFileName.innerText = "";

            return;
        }

        const file =
            compressPdfFile.files[0];

        compressFileName.innerText =
            file.name;
    }
);


// Compress button
compressButton.addEventListener(
    "click",
    async function () {

        const file =
            compressPdfFile.files[0];


        if (!file) {

            compressStatus.innerHTML =
                "<p>Please select a PDF file.</p>";

            return;
        }


        const quality =
            compressionQuality.value;


        const formData =
            new FormData();


        formData.append(
            "file",
            file
        );


        formData.append(
            "quality",
            quality
        );


        compressStatus.innerHTML =
            "<p>Compressing PDF...</p>";


        compressButton.disabled = true;


        try {

            const response =
                await fetch(
                    "http://127.0.0.1:8000/compress/",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            if (!response.ok) {

                const error =
                    await response.json();

                compressStatus.innerHTML =
                    `<p>${error.detail || "Compression failed."}</p>`;

                return;
            }


            const blob =
                await response.blob();


            // Download compressed PDF
            const url =
                window.URL.createObjectURL(blob);


            const link =
                document.createElement("a");


            link.href = url;

            link.download =
                "compressed.pdf";


            document.body.appendChild(link);

            link.click();

            link.remove();


            window.URL.revokeObjectURL(url);


            compressStatus.innerHTML =
                "<p>PDF compressed successfully!</p>";


        } catch (error) {

            console.error(error);

            compressStatus.innerHTML =
                "<p>Could not connect to backend.</p>";

        } finally {

            compressButton.disabled = false;
        }

    }
);

// ========================================
// PDF → IMAGES
// ========================================

const convertPdfFile =
    document.getElementById("convertPdfFile");

const convertFileName =
    document.getElementById("convertFileName");

const imageFormat =
    document.getElementById("imageFormat");

const imageDpi =
    document.getElementById("imageDpi");

const convertButton =
    document.getElementById("convertButton");

const convertStatus =
    document.getElementById("convertStatus");


// ----------------------------------------
// Show selected file
// ----------------------------------------

convertPdfFile.addEventListener(
    "change",
    function () {

        convertStatus.innerHTML = "";

        if (convertPdfFile.files.length === 0) {

            convertFileName.innerText = "";

            return;
        }


        const file =
            convertPdfFile.files[0];


        convertFileName.innerText =
            file.name;
    }
);


// ----------------------------------------
// Convert button
// ----------------------------------------

convertButton.addEventListener(
    "click",
    async function () {

        const file =
            convertPdfFile.files[0];


        // Validate file

        if (!file) {

            convertStatus.innerHTML =
                "<p>Please select a PDF file.</p>";

            return;
        }


        const format =
            imageFormat.value;


        const dpi =
            imageDpi.value;


        // Create multipart request

        const formData =
            new FormData();


        formData.append(
            "file",
            file
        );


        formData.append(
            "image_format",
            format
        );


        formData.append(
            "dpi",
            dpi
        );


        convertStatus.innerHTML =
            "<p>Converting PDF pages to images...</p>";


        convertButton.disabled = true;


        try {

            const response =
                await fetch(
                    "http://127.0.0.1:8000/convert/",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            // Backend error

            if (!response.ok) {

                const error =
                    await response.json();


                convertStatus.innerHTML =
                    `<p>${error.detail || "Conversion failed."}</p>`;

                return;
            }


            // Receive ZIP

            const blob =
                await response.blob();


            // Create download URL

            const url =
                window.URL.createObjectURL(blob);


            // Create download link

            const link =
                document.createElement("a");


            link.href = url;

            link.download =
                "pdf_images.zip";


            document.body.appendChild(link);


            link.click();


            link.remove();


            window.URL.revokeObjectURL(url);


            convertStatus.innerHTML =
                "<p>PDF converted successfully!</p>";


        } catch (error) {

            console.error(error);


            convertStatus.innerHTML =
                "<p>Could not connect to backend.</p>";

        } finally {

            convertButton.disabled = false;
        }

    }
);

// =========================================
// IMAGES → PDF
// =========================================

const imageFilesInput =
    document.getElementById("imageFiles");

const imageList =
    document.getElementById("imageList");

const imageToPdfButton =
    document.getElementById("imageToPdfButton");

const pageSize =
    document.getElementById("pageSize");

const imageOrientation =
    document.getElementById("imageOrientation");


// -----------------------------------------
// Image Selection
// -----------------------------------------

if (imageFilesInput) {

    imageFilesInput.addEventListener(
        "change",
        function () {

            const files = Array.from(
                imageFilesInput.files
            );

            imageList.innerHTML = "";

            if (files.length === 0) {

                imageList.textContent =
                    "No images selected";

                imageToPdfButton.disabled = true;

                return;
            }


            files.forEach(
                function (file, index) {

                    const item =
                        document.createElement("div");

                    item.className =
                        "image-list-item";

                    item.textContent =
                        `${index + 1}. ${file.name}`;

                    imageList.appendChild(item);
                }
            );


            imageToPdfButton.disabled = false;
        }
    );
}


// -----------------------------------------
// Convert Images → PDF
// -----------------------------------------

if (imageToPdfButton) {

    imageToPdfButton.addEventListener(
        "click",
        async function () {

            const files =
                Array.from(
                    imageFilesInput.files
                );

            if (files.length === 0) {

                alert(
                    "Please select at least one image."
                );

                return;
            }


            const formData =
                new FormData();


            // Add images
            files.forEach(
                function (file) {

                    formData.append(
                        "files",
                        file
                    );
                }
            );


            // Add options
            formData.append(
                "page_size",
                pageSize.value
            );

            formData.append(
                "orientation",
                imageOrientation.value
            );


            try {

                imageToPdfButton.disabled = true;

                imageToPdfButton.textContent =
                    "Converting...";


                const response =
                    await fetch(
                        "http://127.0.0.1:8000/convert/images-to-pdf",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                if (!response.ok) {

                    throw new Error(
                        "PDF conversion failed"
                    );
                }


                const blob =
                    await response.blob();


                // Create download URL
                const url =
                    window.URL.createObjectURL(
                        blob
                    );


                const link =
                    document.createElement("a");

                link.href = url;

                link.download =
                    "images_to_pdf.pdf";

                document.body.appendChild(link);

                link.click();

                link.remove();

                window.URL.revokeObjectURL(
                    url
                );


            } catch (error) {

                console.error(error);

                alert(
                    "Failed to convert images to PDF."
                );

            } finally {

                imageToPdfButton.disabled = false;

                imageToPdfButton.textContent =
                    "Convert to PDF";
            }

        }
    );
}

