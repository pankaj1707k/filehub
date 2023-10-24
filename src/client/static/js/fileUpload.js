/**
 * Extract cookie value by its name
 *
 * @param {string} name - Name of the cookie
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie("csrftoken");
const uploadButton = document.getElementById("upload-btn");
const fileInput = document.getElementById("file-selector");

// listen for a click event to upload and trigger a file input
uploadButton.addEventListener("click", () => {
  fileInput.click();
});

// start upload process after selecting files
fileInput.addEventListener("change", uploadHandler);

/**
 * Handle the upload process for multiple files
 */
async function uploadHandler() {
  var files = fileInput.files;
  for (let i = 0; i < files.length; i++) {
    let uploadURL = await fetch("/get-signed-url/?upload=true");
    uploadURL
      .json()
      .then((data) => uploadFile(files[i], data))
      .then((data) => sendMetadata(files[i], data))
      .then(() => {
        htmx.trigger("body", "contentChange");
      });
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
    let res = await fetch(data.url, {
      method: "PUT",
      body: file,
      headers: { "X-CSRFToken": csrftoken },
    });
    status.innerHTML += `<br>Uploaded ${file.name}`;
  } catch (error) {
    console.log(error);
  }
  return data;
}

/**
 * Send metadata of the uploaded file to the app server
 *
 * @param {File} file - Uploaded file
 * @param {Object} data - Contains the upload URL and UUID
 */
async function sendMetadata(file, data) {
  try {
    let res = await fetch("/f/new/", {
      method: "POST",
      body: JSON.stringify({
        id: data.key,
        name: file.name,
        size: file.size,
        type: file.type,
        directory: document.getElementById("currDir").value,
      }),
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrftoken,
      },
    });
    if (res.status === 400) {
      console.log("Metadata update failed");
    }
  } catch (error) {
    console.log(error);
  }
}
