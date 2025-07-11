document.addEventListener("DOMContentLoaded", function () {
  const generateBranchBtn = document.getElementById("generate_branch_button");
  const submitBtn = document.getElementById("submit");
  const companyInput = document.querySelector('input[name="company"]');
  const titleInput = document.querySelector('input[name="title"]');
  const branchNameInput = document.querySelector(
    'input[name="github_branch_name"]'
  );
  const branchFeedbackDiv = document.createElement("div");
  branchFeedbackDiv.id = "branch-feedback";
  branchFeedbackDiv.className = "mt-2";

  // Insert feedback div after branch name input
  if (branchNameInput && branchNameInput.parentNode) {
    branchNameInput.parentNode.appendChild(branchFeedbackDiv);
  }

  if (generateBranchBtn) {
    generateBranchBtn.addEventListener("click", async function () {
      // Clear previous feedback
      branchFeedbackDiv.textContent = "";
      branchFeedbackDiv.className = "mt-2";

      const company = companyInput ? companyInput.value.trim() : "";
      const title = titleInput ? titleInput.value.trim() : "";

      if (!company || !title) {
        branchFeedbackDiv.textContent =
          "Company and Job Title are required to generate a GitHub branch.";
        branchFeedbackDiv.classList.add("text-danger");
        return;
      }

      generateBranchBtn.disabled = true;
      submitBtn.disabled = true;
      generateBranchBtn.textContent = "Generating...";

      try {
        const response = await fetch("/jobs/create-github-branch", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify({
            company: company,
            title: title,
            github_branch_name: branchNameInput
              ? branchNameInput.value.trim()
              : "",
          }),
        });

        const data = await response.json();

        if (response.ok && data.github_branch) {
          branchFeedbackDiv.innerHTML = `
            <span class="text-success">GitHub branch created: <strong>${data.github_branch}</strong></span>
            <br>
            <a href="${data.github_branch_url}" target="_blank">View branch on GitHub</a>
          `;
          if (branchNameInput) {
            branchNameInput.value = data.github_branch;
          }
          // Set job_id hidden input value from response
          const jobIdInput = document.getElementById("job_id");
          if (jobIdInput && data.job_id) {
            jobIdInput.value = data.job_id;
            console.log("Job ID set to:", data.job_id);
          }
          const existingIdInput = document.getElementById("existing_id");
          if (existingIdInput && data.job_id) {
            existingIdInput.value = data.job_id;
            console.log("Existing ID set to:", data.job_id);
          }
          generateBranchBtn.disabled = true;
        } else {
          branchFeedbackDiv.textContent =
            data.error || "Failed to create GitHub branch.";
          branchFeedbackDiv.classList.add("text-danger");
        }
      } catch (err) {
        branchFeedbackDiv.textContent = "Error communicating with server.";
        branchFeedbackDiv.classList.add("text-danger");
      } finally {
        submitBtn.disabled = false;
        generateBranchBtn.disabled = false;
        generateBranchBtn.textContent = "Generate Branch Now";
      }
    });
  }
});
