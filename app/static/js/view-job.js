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

  deleteFile(job_id, file_name, file_description) {
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
        // reload the file cards section
        fetch(window.location.href, {
          headers: { "X-Requested-With": "XMLHttpRequest" },
        })
          .then((response) => response.text())
          .then((html) => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const newFilesContainer = doc.getElementById(
              "edit-files-container"
            );
            const currentFilesContainer = document.getElementById(
              "edit-files-container"
            );
            if (newFilesContainer && currentFilesContainer) {
              currentFilesContainer.innerHTML = newFilesContainer.innerHTML;
            }
          });
        //location.reload();
      })
      .catch((error) => {
        console.error(`Error deleting ${file_description}:`, error);
      });
    console.log("Delete Resume Button clicked");
  }
}
