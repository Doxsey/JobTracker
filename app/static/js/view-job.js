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
    this.editBtn.addEventListener("click", this.onEdit.bind(this));
    this.cancelEditBtn.addEventListener("click", this.onCancelEdit.bind(this));
    this.confirmDeleteBtn.addEventListener(
      "click",
      this.onConfirmDelete.bind(this)
    );

    if (this.deleteResumeBtn) {
      this.deleteResumeBtn.addEventListener(
        "click",
        this.onDeleteResume.bind(this)
      );
    }
    if (this.deleteCoverLetterBtn) {
      this.deleteCoverLetterBtn.addEventListener(
        "click",
        this.onDeleteCoverLetter.bind(this)
      );
    }
    if (this.deleteJobDescriptionBtn) {
      this.deleteJobDescriptionBtn.addEventListener(
        "click",
        this.onDeleteJobDescription.bind(this)
      );
    }
    if (this.replaceCoverLetterBtn) {
      this.replaceCoverLetterBtn.addEventListener(
        "click",
        this.onReplaceCoverLetter.bind(this)
      );
    }
    if (this.replaceJobDescriptionBtn) {
      this.replaceJobDescriptionBtn.addEventListener(
        "click",
        this.onReplaceJobDescription.bind(this)
      );
    }
    if (this.replaceResumeBtn) {
      this.replaceResumeBtn.addEventListener(
        "click",
        this.onReplaceResume.bind(this)
      );
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

    this.deleteResumeBtn = document.getElementById("delete-resume-btn");
    this.deleteCoverLetterBtn = document.getElementById(
      "delete-cover_letter-btn"
    );
    this.deleteJobDescriptionBtn = document.getElementById(
      "delete-job_description-btn"
    );

    this.replaceCoverLetterBtn = document.getElementById(
      "replace-cover_letter-btn"
    );
    this.replaceJobDescriptionBtn = document.getElementById(
      "replace-job_description-btn"
    );
    this.replaceResumeBtn = document.getElementById("replace-resume-btn");

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
    this.deleteFile(
      this.jobViewData.job_id,
      this.jobViewData.resume_file,
      "resume"
    );
  }

  onDeleteCoverLetter() {
    this.deleteFile(
      this.jobViewData.job_id,
      this.jobViewData.cover_letter_file,
      "cover letter"
    );
  }

  onDeleteJobDescription() {
    this.deleteFile(
      this.jobViewData.job_id,
      this.jobViewData.job_description_file,
      "job description"
    );
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
    // const jobId = this.jobViewData.job_id;
    // const fileName = this.jobViewData.file_name; // Assuming you have the file name in jobViewData
    // const fileDescription = this.jobViewData.file_description; // Assuming you have the file description in jobViewData

    // this.deleteFile(jobId, fileName, fileDescription);
  }

  deleteFile(job_id, file_name, file_description) {
    // this.confirmDeleteModal.classList.add("active");
    var modal = new bootstrap.Modal(
      document.getElementById("confirmDeleteModal")
    );
    modal.show();

    return;

    fetch(this.jobViewData.delete_file_url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        job_id: job_id,
        file_name: file_name,
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

              // Re-cache DOM elements and setup event listeners for new buttons
              this.cacheDomElements();
              this.setupEventListeners();
            });
        } else {
          console.error("Error deleting file:", data.error);
        }
      })
      .catch((error) => {
        console.error(`Error deleting ${file_description}:`, error);
      });
    console.log("Delete Resume Button clicked");
  }
}
