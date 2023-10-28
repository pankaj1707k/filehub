const downloadButton = document.getElementById("download-btn");
const fileKey = document.querySelector("input[name='fileID']").value;

// listen for click event on download button and trigger download
downloadButton.addEventListener("click", downloadHandler);

/**
 * Handle the download process for a file
 */
async function downloadHandler() {
  let downloadURL = await fetch(
    `/get-signed-url/?download=true&key=${fileKey}`
  );
  downloadURL
    .json()
    .then((data) => downloadFile(data))
    .catch((error) => console.log(error));
}

/**
 * Download a file from the given URL.
 *
 * @param {Object} data - Contains the URL and UUID
 */
async function downloadFile(data) {
  let res = await fetch(data.url, {
    method: "GET",
  });
  let blob = await res.blob();
  let url = window.URL.createObjectURL(blob);
  let a = document.createElement("a");
  a.href = url;
  a.download = document.getElementById("fileName").innerHTML;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
