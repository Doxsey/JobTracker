class JobView {
  constructor(jobViewData) {
    this.jobViewData = jobViewData;
    this.init();
  }

  init() {
    console.log("Initializing JobView with job:", this.jobViewData);
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
  }

  onCancelEdit() {
    location.reload(true);
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

  onReplaceResume() {
    // Add your replace logic here
    console.log("Replace Resume Button clicked");
  }

  onReplaceCoverLetter() {
    // Add your replace logic here
    console.log("Replace Cover Letter Button clicked");
  }

  onReplaceJobDescription() {
    // Add your replace logic here
    console.log("Replace Job Description Button clicked");
  }

  onConfirmDelete() {
    console.log("Confirm Delete Button clicked");
    this.confirmDeleteModal.hide();
    this.deleteFile();
  }

  onDeleteFile(file_name, file_description) {
    console.log("onDeleteFile called with:", file_name, file_description);
    this.file_name = file_name;
    this.file_description = file_description;
    this.confirmDeleteModal = new bootstrap.Modal(
      document.getElementById("confirmDeleteModal")
    );
    this.confirmDeleteModal.show();
  }

  deleteFile() {
    console.log(
      "deleteFile called with:",
      this.file_name,
      this.file_description
    );
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
        console.log("Response from deleteFile:", data);
        if (data.success) {
          console.log("Inside of deleteFile() success block");
          // Fetch updated file cards
          fetch(`/jobs/${this.jobViewData.job_id}/file-cards`)
            .then((response) => response.text())
            .then((html) => {
              const container = document.getElementById("edit-files-container");
              container.innerHTML = html;

              // No need to re-setup event listeners - event delegation handles it!
            });
        } else {
          this.showFileAlert("Error deleting file:", data.error);
        }
      })
      .catch((error) => {
        console.error(`Error deleting ${this.file_description}:`, error);
      });
    console.log("Delete Resume Button clicked");
  }

  showFileAlert(boldText, message) {
    const alertDiv = document.createElement("div");
    alertDiv.className = "alert alert-danger alert-dismissible fade show";
    alertDiv.role = "alert";
    alertDiv.innerHTML = `
      <strong>${boldText}</strong> ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      `;
    const container =
      document.getElementById("file-alert-container") || document.body;
    container.prepend(alertDiv);
  }
}
