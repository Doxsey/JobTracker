document.addEventListener("DOMContentLoaded", function () {
  console.log("Settings page loaded");
  const uploadNewBtn = document.getElementById("upload-new-btn");
  const deleteResumeBtn = document.getElementById("delete-resume-btn");
  const downloadResumeBtn = document.getElementById("download-resume-btn");
  if (uploadNewBtn) {
    uploadNewBtn.addEventListener("click", function () {
      handleUploadNewClick();
    });
  }
  if (deleteResumeBtn) {
    deleteResumeBtn.addEventListener("click", function () {
      handleDeleteResumeClick();
    });
  }
  if (downloadResumeBtn) {
    downloadResumeBtn.addEventListener("click", function () {
      handleDownloadResumeClick();
    });
  }
});

function handleUploadNewClick() {
  console.log("Upload new resume button clicked");
  const fileInput = document.createElement("input");
  fileInput.type = "file";
  fileInput.accept = ".pdf, .doc, .docx, .tex";
  fileInput.onchange = function (event) {
    const file = event.target.files[0];
    if (file) {
      const formData = new FormData();
      formData.append("default_resume_file", file);

      fetch("/settings/api/upload_default_resume", {
        method: "POST",
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            showAlert(
              "Success!",
              "Default resume uploaded successfully.",
              "success"
            );
            location.reload(true);
          } else {
            showAlert("Error!", "Error uploading resume: " + data.error);
          }
        })
        .catch((error) => {
          console.error("Error:", error);
          showAlert("Error!", "An error occurred while uploading the resume.");
        });
    }
  };
  fileInput.click();
}

function handleDeleteResumeClick() {
  console.log("Delete resume button clicked");
  if (confirm("Are you sure you want to delete the default resume?")) {
    fetch("/settings/api/delete_default_resume", {
      method: "DELETE",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          showAlert(
            "Success!",
            "Default resume deleted successfully.",
            "success"
          );
          //   alert("Default resume deleted successfully.");
          location.reload(true); // Force a full refresh of the page to update the UI
        } else {
          showAlert("Error!", "Error deleting resume: " + data.error);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        showAlert("Error!", "An error occurred while deleting the resume.");
      });
  }
}

function handleDownloadResumeClick() {
  console.log("Download resume button clicked");

  fetch("/settings/api/download_default_resume", {
    method: "GET",
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Check if the response is actually a file (not JSON)
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        // If it's JSON, handle it as before
        return response.json().then((data) => {
          if (data.success) {
            console.log("Resume download URL:", data.file_url);
            const link = document.createElement("a");
            link.href = data.file_url;
            link.download = "Default Resume.pdf";
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
          } else {
            showAlert("Error!", "Error downloading resume: " + data.error);
          }
        });
      } else {
        // If it's a file, handle it as a blob
        return response.blob().then((blob) => {
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.download = "Default Resume.pdf";
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url); // Clean up
        });
      }
    })
    .catch((error) => {
      console.error("Error:", error);
      showAlert("Error!", "An error occurred while downloading the resume.");
    });
}

function showAlert(boldText, message, type = "danger") {
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.role = "alert";
  alertDiv.innerHTML = `
    <strong>${boldText}</strong> ${message}
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
  `;
  const container =
    document.getElementById("file-alert-container") || document.body;
  container.prepend(alertDiv);

  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    alertDiv.classList.remove("show");
    setTimeout(() => alertDiv.remove(), 150); // Wait for fade out
  }, 5000);
}
