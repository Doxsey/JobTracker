class GitHubBranchCreator {
  constructor() {
    this.companyInput = document.getElementById("quick-company");
    this.titleInput = document.getElementById("quick-title");
    this.branchNameInput = document.getElementById("quick-branch-name");
    this.createBtn = document.getElementById("create-github-branch-btn");
    this.creationCard = document.getElementById("github-branch-creation");
    this.successAlert = document.getElementById("branch-created-alert");
    this.mainForm = document.getElementById("job-form");

    this.init();
  }

  init() {
    if (this.createBtn) {
      this.createBtn.addEventListener(
        "click",
        this.handleCreateBranch.bind(this)
      );
    }

    // Auto-populate main form fields when quick inputs change
    if (this.companyInput) {
      this.companyInput.addEventListener(
        "input",
        this.syncToMainForm.bind(this)
      );
    }
    if (this.titleInput) {
      this.titleInput.addEventListener("input", this.syncToMainForm.bind(this));
    }

    // Generate branch name preview
    if (this.branchNameInput) {
      this.setupBranchNameGeneration();
    }
  }

  syncToMainForm() {
    const mainCompany = document.getElementById("company");
    const mainTitle = document.getElementById("title");

    if (mainCompany && this.companyInput.value) {
      mainCompany.value = this.companyInput.value;
    }
    if (mainTitle && this.titleInput.value) {
      mainTitle.value = this.titleInput.value;
    }
  }

  setupBranchNameGeneration() {
    const updatePreview = () => {
      if (
        !this.branchNameInput.value &&
        this.companyInput.value &&
        this.titleInput.value
      ) {
        const preview = this.generateBranchName(
          this.companyInput.value,
          this.titleInput.value
        );
        this.branchNameInput.placeholder = `Preview: ${preview}`;
      } else {
        this.branchNameInput.placeholder = "Auto-generated if empty";
      }
    };

    this.companyInput?.addEventListener("input", updatePreview);
    this.titleInput?.addEventListener("input", updatePreview);
  }

  generateBranchName(company, title) {
    // Simple client-side branch name generation for preview
    const cleanCompany = company
      .replace(/[^a-zA-Z0-9\s-]/g, "")
      .trim()
      .replace(/\s+/g, "-")
      .toLowerCase()
      .substring(0, 30);
    const cleanTitle = title
      .replace(/[^a-zA-Z0-9\s-]/g, "")
      .trim()
      .replace(/\s+/g, "-")
      .toLowerCase()
      .substring(0, 30);
    const date = new Date().toISOString().split("T")[0].replace(/-/g, "");

    return `job/${cleanCompany}/${cleanTitle}-${date}`;
  }

  async handleCreateBranch() {
    const company = this.companyInput.value.trim();
    const title = this.titleInput.value.trim();
    const branchName = this.branchNameInput.value.trim();

    if (!company || !title) {
      this.showAlert(
        "Error",
        "Company and job title are required to create a GitHub branch.",
        "danger"
      );
      return;
    }

    this.setLoadingState(true);

    try {
      const response = await fetch("/jobs/create-github-branch", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company: company,
          title: title,
          github_branch_name: branchName,
        }),
      });

      const data = await response.json();

      if (data.success) {
        this.handleSuccess(data);
      } else {
        this.showAlert("Error", data.error, "danger");
      }
    } catch (error) {
      console.error("Error:", error);
      this.showAlert(
        "Error",
        "Failed to create GitHub branch. Please try again.",
        "danger"
      );
    } finally {
      this.setLoadingState(false);
    }
  }

  handleSuccess(data) {
    // Hide creation card
    if (this.creationCard) {
      this.creationCard.style.display = "none";
    }

    // Show success alert
    if (this.successAlert) {
      this.successAlert.classList.remove("d-none");

      const branchNameSpan = document.getElementById("created-branch-name");
      const viewLink = document.getElementById("view-branch-link");

      if (branchNameSpan) branchNameSpan.textContent = data.github_branch;
      if (viewLink) viewLink.href = data.github_branch_url;
    }

    // Update the GitHub Integration section
    this.updateGitHubIntegrationSection(data);

    // Update URL with draft job ID
    const url = new URL(window.location);
    url.searchParams.set("draft_job_id", data.job_id);
    window.history.replaceState({}, "", url);

    // Add hidden field for draft job ID
    const hiddenField = document.createElement("input");
    hiddenField.type = "hidden";
    hiddenField.name = "draft_job_id";
    hiddenField.value = data.job_id;
    this.mainForm.appendChild(hiddenField);

    // Update submit button text
    const submitBtn = this.mainForm.querySelector('input[type="submit"]');
    if (submitBtn) {
      submitBtn.value = "Complete Job";
    }

    // Scroll to main form
    this.mainForm.scrollIntoView({ behavior: "smooth", block: "start" });

    this.showAlert("Success", data.message, "success");
  }

  updateGitHubIntegrationSection(data) {
    // Find the GitHub integration content container
    const githubIntegrationContent = document.getElementById(
      "github-integration-content"
    );
    if (!githubIntegrationContent) return;

    // Create the new branch info HTML
    const branchInfoHtml = `
      <div class="alert alert-info" id="existing-branch-info">
        <i class="bi bi-info-circle-fill me-2"></i>
        <strong>GitHub branch already created:</strong> 
        <code>${data.github_branch}</code>
        <a href="${data.github_branch_url}" 
           target="_blank" class="btn btn-sm btn-outline-primary ms-2">
          <i class="bi bi-box-arrow-up-right me-1"></i>View on GitHub
        </a>
      </div>
    `;

    // Replace the entire content of the GitHub integration section
    githubIntegrationContent.innerHTML = branchInfoHtml;
  }

  setLoadingState(loading) {
    if (!this.createBtn) return;

    this.createBtn.disabled = loading;

    if (loading) {
      this.createBtn.innerHTML =
        '<span class="spinner-border spinner-border-sm me-2"></span>Creating...';
    } else {
      this.createBtn.innerHTML =
        '<i class="bi bi-github me-2"></i>Create GitHub Branch';
    }
  }

  showAlert(title, message, type = "info") {
    const alertContainer = document.getElementById("github-alert-container");
    if (!alertContainer) return;

    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
      <strong>${title}:</strong> ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    alertContainer.appendChild(alertDiv);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      alertDiv.remove();
    }, 5000);
  }
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", function () {
  new GitHubBranchCreator();
});
