const uploadButton = document.getElementById("upload-btn");

// listen for a click event to upload
uploadButton.addEventListener("click", uploadHandler);

/**
 * Handle the upload process for multiple files
 */
async function uploadHandler() {
  var files = document.getElementById("file-selector").files;
  for (let i = 0; i < files.length; i++) {
    let uploadURL = await fetch("/files/get-signed-url/?upload=true");
    uploadURL
      .json()
      .then((data) => uploadFile(files[i], data))
      .then((data) => sendMetadata(files[i], data));
  }
}

/**
 * Upload a single file to the given URL.
 *
 * @param {File} file - A file to be uploaded
 * @param {Object} data - Contains the URL and UUID
 */
async function uploadFile(file, data) {
  // `status` element is temporary, replace with a progress bar
  let status = document.getElementById("status");
  try {
    let res = await fetch(data.url, { method: "PUT", body: file });
    status.innerHTML += `<br>Uploaded ${file.name}`;
  } catch (error) {
    console.log(error);
  }
}

/**
 * Send metadata of the uploaded file to the app server
 *
 * @param {File} file - Uploaded file
 * @param {Object} data - Contains the upload URL and UUID
 */
async function sendMetadata(file, data) {
  // TODO: send the file metadata to the app server for database entry
}
