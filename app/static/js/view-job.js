class JobView {
  constructor(jobViewData) {
    this.jobViewData = jobViewData;
    this.init();
  }

  init() {
    document.addEventListener(
      "DOMContentLoaded",
      function () {
        this.cacheDomElements();
        this.setupEventListeners();
      }.bind(this)
    );
  }

  setupEventListeners() {
    // Use event delegation for file-related buttons that get dynamically updated
    document.addEventListener("click", this.handleDynamicClicks.bind(this));

    // Static elements that don't change
    this.editBtn.addEventListener("click", this.onEdit.bind(this));
    this.cancelEditBtn.addEventListener("click", this.onCancelEdit.bind(this));
    this.confirmDeleteBtn.addEventListener(
      "click",
      this.onConfirmDelete.bind(this)
    );
  }

  handleDynamicClicks(event) {
    // Handle delete buttons
    if (event.target.id === "delete-resume-btn") {
      this.onDeleteResume();
    } else if (event.target.id === "delete-cover_letter-btn") {
      this.onDeleteCoverLetter();
    } else if (event.target.id === "delete-job_description-btn") {
      this.onDeleteJobDescription();
    }
    // Handle replace buttons
    else if (event.target.id === "replace-resume-btn") {
      this.onReplaceResume();
    } else if (event.target.id === "replace-cover_letter-btn") {
      this.onReplaceCoverLetter();
    } else if (event.target.id === "replace-job_description-btn") {
      this.onReplaceJobDescription();
    }
    // Handle upload buttons
    else if (event.target.id === "upload-resume-btn") {
      this.onUploadResume();
    } else if (event.target.id === "upload-cover_letter-btn") {
      this.onUploadCoverLetter();
    } else if (event.target.id === "upload-job_description-btn") {
      this.onUploadJobDescription();
    }
  }

  cacheDomElements() {
    this.editBtn = document.getElementById("edit-btn");
    this.finishEditBtn = document.getElementById("finish-edit-btn");
    this.cancelEditBtn = document.getElementById("cancel-edit-btn");
    this.fileDropdown = document.getElementById("file-dropdown");
    this.fileEditContainer = document.getElementById("edit-files-container");
    this.pageHeading = document.getElementById("page-heading");
    this.confirmDeleteModal = document.getElementById("deleteModal");
    this.confirmDeleteBtn = document.getElementById("confirm-delete-btn");
    this.form = document.getElementById("job-view-form");
  }

  updateJobData(updates) {
    Object.assign(this.jobViewData, updates);
    // console.log("Updated job data:", this.jobViewData);
  }

  setFormDisabled(disabled) {
    const elements = this.form.querySelectorAll("input, textarea, select");
    elements.forEach((el) => {
      if (el.name !== "csrf_token") {
        el.disabled = disabled;
      }
    });
  }

  onEdit() {
    this.setFormDisabled(false);
    this.editBtn.style.display = "none";
    if (this.fileDropdown) {
      this.fileDropdown.style.display = "none";
    }
    this.finishEditBtn.style.display = "inline-block";
    this.cancelEditBtn.style.display = "inline-block";
    if (this.fileEditContainer) {
      this.fileEditContainer.classList.remove("d-none");
    }
    this.pageHeading.textContent = "Editing Job";
    this.pageHeading.classList.add("text-warning");
    this.refreshFileCards();
  }

  onCancelEdit() {
    // location.reload(true);
    location.replace(window.location.href);
  }

  onDeleteResume() {
    this.onDeleteFile(this.jobViewData.resume_file, "resume");
  }

  onDeleteCoverLetter() {
    this.onDeleteFile(this.jobViewData.cover_letter_file, "cover letter");
  }

  onDeleteJobDescription() {
    this.onDeleteFile(this.jobViewData.job_description_file, "job description");
  }

  onUploadResume() {
    this.uploadFile("resume_file");
  }

  onUploadCoverLetter() {
    this.uploadFile("cover_letter_file");
  }

  onUploadJobDescription() {
    this.uploadFile("job_description_file");
  }

  // Updated replace button handlers (same functionality, but with replace flag)
  onReplaceResume() {
    this.uploadFile("resume_file", true);
  }

  onReplaceCoverLetter() {
    this.uploadFile("cover_letter_file", true);
  }

  onReplaceJobDescription() {
    this.uploadFile("job_description_file", true);
  }

  onConfirmDelete() {
    this.confirmDeleteModal.hide();
    this.deleteFile();
  }

  onDeleteFile(file_name, file_description) {
    this.file_name = file_name;
    this.file_description = file_description;
    this.confirmDeleteModal = new bootstrap.Modal(
      document.getElementById("confirmDeleteModal")
    );
    this.confirmDeleteModal.show();
  }

  deleteFile() {
    // console.log(
    //   "deleteFile called with:",
    //   this.file_name,
    //   this.file_description
    // );
    if (!this.file_name || !this.file_description) {
      console.error("File name or description is missing.");
      return;
    }
    fetch(this.jobViewData.delete_file_url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        job_id: this.jobViewData.job_id,
        file_name: this.file_name,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        // console.log("Response from deleteFile:", data);
        if (data.success) {
          const fileTypeMap = {
            [this.jobViewData.resume_file]: "resume_file",
            [this.jobViewData.cover_letter_file]: "cover_letter_file",
            [this.jobViewData.job_description_file]: "job_description_file",
          };

          const deletedFileType = fileTypeMap[this.file_name];
          if (deletedFileType) {
            this.updateJobData({
              [deletedFileType]: null,
            });
          }

          this.refreshFileCards();
        } else {
          this.showFileAlert("Error deleting file:", data.error);
        }
      })
      .catch((error) => {
        console.error(`Error deleting ${this.file_description}:`, error);
      });
  }

  uploadFile(fileType, replaceExisting = false) {
    const fileInput = document.createElement("input");
    fileInput.type = "file";
    fileInput.accept = ".pdf,.doc,.docx,.txt,.tex,";
    fileInput.style.display = "none";
    document.body.appendChild(fileInput);

    fileInput.addEventListener("change", async (event) => {
      const file = event.target.files[0];
      if (!file) {
        document.body.removeChild(fileInput);
        return;
      }

      // Show loading state (optional)
      this.showLoadingState(fileType, true);

      try {
        const result = await this.performFileUpload(
          file,
          fileType,
          replaceExisting
        );

        if (result.success) {
          // Refresh file cards to show the new file
          this.refreshFileCards();
          this.showFileAlert(
            "Success!",
            `${fileType.replace("_", " ")} uploaded successfully.`,
            "success"
          );
        } else {
          this.showFileAlert("Error uploading file:", result.error);
        }
      } catch (error) {
        this.showFileAlert("Error uploading file:", error.message);
      } finally {
        this.showLoadingState(fileType, false);
        document.body.removeChild(fileInput);
      }
    });

    // Trigger the file picker
    fileInput.click();
  }

  async performFileUpload(file, fileType, replaceExisting = false) {
    const formData = new FormData();
    formData.append("job_id", this.jobViewData.job_id);
    formData.append("file_type", fileType);
    formData.append("file", file);
    formData.append("replace_existing", replaceExisting.toString());

    const response = await fetch("/files/upload", {
      method: "POST",
      body: formData,
    });

    const result = await response.json();

    if (!response.ok) {
      throw new Error(result.error || "Upload failed");
    }

    this.updateJobData({
      [fileType]: result.stored_filename,
    });

    return result;
  }

  refreshFileCards() {
    fetch(`/jobs/${this.jobViewData.job_id}/file-cards`)
      .then((response) => response.text())
      .then((html) => {
        const container = document.getElementById("edit-files-container");
        container.innerHTML = html;

        // No need to re-setup event listeners - event delegation handles it!
      });
  }

  // Show loading state
  showLoadingState(fileType, isLoading) {
    const buttonId = isLoading
      ? `upload-${fileType.replace("_file", "")}-btn`
      : `replace-${fileType.replace("_file", "")}-btn`;

    const button = document.getElementById(buttonId);
    if (button) {
      if (isLoading) {
        button.disabled = true;
        button.textContent = "Uploading...";
      } else {
        button.disabled = false;
        // Reset button text based on whether file exists
        const hasFile = this.jobViewData[fileType];
        button.textContent = hasFile ? "Replace" : "Upload";
      }
    }
  }

  // Updated showFileAlert to support success messages
  showFileAlert(boldText, message, type = "danger") {
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

    // Auto-dismiss success alerts after 3 seconds
    if (type === "success") {
      setTimeout(() => {
        if (alertDiv.parentNode) {
          alertDiv.remove();
        }
      }, 5000);
    }
  }
}
