class QuillEditor {
  constructor(options = {}) {
    this.options = {
      // Default configuration
      editorId: options.editorId || "editor",
      hiddenFieldId: options.hiddenFieldId || "description",
      displayElementId: options.displayElementId || null,
      theme: options.theme || "snow",
      placeholder: options.placeholder || "Enter text...",
      height: options.height || "200px",
      toolbar: options.toolbar || [
        ["bold", "italic", "underline"],
        ["blockquote", "code-block"],
        [{ header: [1, 2, 3, false] }],
        [{ list: "ordered" }, { list: "bullet" }],
        ["link"],
        ["clean"],
      ],
      initialContent: options.initialContent || "",
      onChange: options.onChange || null,
      onReady: options.onReady || null,
      autoSync: options.autoSync !== false, // Default to true
      ...options,
    };

    this.quill = null;
    this.isInitialized = false;
    this.isVisible = false;

    this.init();
  }

  init() {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", () => this.createEditor());
    } else {
      this.createEditor();
    }
  }

  createEditor() {
    const editorContainer = document.getElementById(this.options.editorId);
    if (!editorContainer) {
      console.error(
        `QuillEditor: Editor container #${this.options.editorId} not found`
      );
      return;
    }

    // Set height if specified
    if (this.options.height) {
      editorContainer.style.height = this.options.height;
    }

    // Initialize Quill
    this.quill = new Quill(`#${this.options.editorId}`, {
      theme: this.options.theme,
      modules: {
        toolbar: this.options.toolbar,
      },
      placeholder: this.options.placeholder,
    });

    // Hide editor initially if displayElementId is provided
    if (this.options.displayElementId) {
      this.hide();
    } else {
      this.isVisible = true;
    }

    this.isInitialized = true;

    // Set initial content AFTER Quill is fully initialized
    if (this.options.initialContent) {
      // Use setTimeout to ensure Quill is fully ready
      setTimeout(() => {
        console.log(
          "Setting initial content after timeout:",
          this.options.initialContent.substring(0, 100) + "..."
        );
        this.setContent(this.options.initialContent);
      }, 50);
    }

    // Setup auto-sync if enabled
    if (this.options.autoSync) {
      this.setupAutoSync();
    }

    // Setup event listeners
    this.setupEventListeners();

    // Call ready callback
    if (this.options.onReady) {
      // Call onReady after a small delay to ensure content is set
      setTimeout(() => {
        this.options.onReady(this);
      }, 100);
    }

    console.log(`QuillEditor initialized: #${this.options.editorId}`);
  }

  setupAutoSync() {
    if (!this.options.hiddenFieldId) return;

    this.quill.on("text-change", () => {
      const hiddenField = document.getElementById(this.options.hiddenFieldId);
      if (hiddenField) {
        hiddenField.value = this.getContent();
      }

      // Call custom onChange callback
      if (this.options.onChange) {
        this.options.onChange(this.getContent(), this);
      }
    });
  }

  setupEventListeners() {
    // Add any additional event listeners here
    this.quill.on("selection-change", (range) => {
      if (range && this.options.onFocus) {
        this.options.onFocus(this);
      } else if (!range && this.options.onBlur) {
        this.options.onBlur(this);
      }
    });
  }

  // Content management methods
  setContent(htmlContent) {
    if (!this.isInitialized) {
      this.options.initialContent = htmlContent;
      return;
    }

    console.log(
      "Setting content:",
      htmlContent ? htmlContent.substring(0, 100) + "..." : "empty"
    );

    try {
      if (htmlContent && htmlContent.trim()) {
        // Method 1: Try using clipboard.convert (Quill 2.0 preferred method)
        const delta = this.quill.clipboard.convert({ html: htmlContent });
        this.quill.setContents(delta);
      } else {
        this.quill.setText("");
      }
    } catch (error) {
      console.warn("Quill clipboard.convert failed, trying fallback:", error);
      try {
        // Method 2: Fallback to direct HTML insertion
        this.quill.root.innerHTML = htmlContent || "";
      } catch (fallbackError) {
        console.error("Both content setting methods failed:", fallbackError);
      }
    }

    // Update hidden field if auto-sync is enabled
    if (this.options.autoSync && this.options.hiddenFieldId) {
      const hiddenField = document.getElementById(this.options.hiddenFieldId);
      if (hiddenField) {
        hiddenField.value = this.getContent();
      }
    }
  }

  getContent() {
    if (!this.isInitialized) return "";
    return this.quill.getSemanticHTML();
  }

  getText() {
    if (!this.isInitialized) return "";
    return this.quill.getText();
  }

  isEmpty() {
    if (!this.isInitialized) return true;
    return this.quill.getText().trim().length === 0;
  }

  // Visibility management
  show() {
    if (!this.isInitialized) return;

    const editorContainer = document.getElementById(this.options.editorId);
    const toolbar = editorContainer?.previousElementSibling;

    // Show toolbar
    if (toolbar && toolbar.classList.contains("ql-toolbar")) {
      toolbar.style.display = "block";
    }

    // Show editor
    editorContainer.style.display = "block";

    // Hide display element if specified
    if (this.options.displayElementId) {
      const displayElement = document.getElementById(
        this.options.displayElementId
      );
      if (displayElement) {
        displayElement.style.display = "none";
      }
    }

    this.isVisible = true;
    this.focus();
  }

  hide() {
    if (!this.isInitialized) return;

    const editorContainer = document.getElementById(this.options.editorId);
    const toolbar = editorContainer?.previousElementSibling;

    // Hide toolbar
    if (toolbar && toolbar.classList.contains("ql-toolbar")) {
      toolbar.style.display = "none";
    }

    // Hide editor
    editorContainer.style.display = "none";

    // Show display element if specified
    if (this.options.displayElementId) {
      const displayElement = document.getElementById(
        this.options.displayElementId
      );
      if (displayElement) {
        // Update display content before showing
        this.updateDisplayContent();
        displayElement.style.display = "block";
      }
    }

    this.isVisible = false;
  }

  toggle() {
    if (this.isVisible) {
      this.hide();
    } else {
      this.show();
    }
  }

  updateDisplayContent() {
    if (!this.options.displayElementId) return;

    const displayElement = document.getElementById(
      this.options.displayElementId
    );
    if (!displayElement) return;

    const content = this.getContent();

    // Check if display element has a specific content container
    const contentContainer =
      displayElement.querySelector(".quill-content") ||
      displayElement.querySelector(".rich-text-content") ||
      displayElement;

    contentContainer.innerHTML = content;
  }

  loadContentFromDisplay() {
    if (!this.options.displayElementId) return;

    const displayElement = document.getElementById(
      this.options.displayElementId
    );
    if (!displayElement) return;

    // Get content from display element
    const contentContainer =
      displayElement.querySelector(".quill-content") ||
      displayElement.querySelector(".rich-text-content") ||
      displayElement;

    const content = contentContainer.innerHTML.trim();
    this.setContent(content);
  }

  // Utility methods
  focus() {
    if (this.isInitialized && this.isVisible) {
      this.quill.focus();
    }
  }

  blur() {
    if (this.isInitialized) {
      this.quill.blur();
    }
  }

  enable() {
    if (this.isInitialized) {
      this.quill.enable();
    }
  }

  disable() {
    if (this.isInitialized) {
      this.quill.disable();
    }
  }

  // Validation
  validate(options = {}) {
    const content = this.getText().trim();
    const minLength = options.minLength || 0;
    const maxLength = options.maxLength || Infinity;
    const required = options.required || false;

    const errors = [];

    if (required && content.length === 0) {
      errors.push("This field is required");
    }

    if (content.length < minLength) {
      errors.push(`Minimum length is ${minLength} characters`);
    }

    if (content.length > maxLength) {
      errors.push(`Maximum length is ${maxLength} characters`);
    }

    return {
      isValid: errors.length === 0,
      errors: errors,
    };
  }

  // Cleanup
  destroy() {
    if (this.quill) {
      // Remove event listeners
      this.quill.off("text-change");
      this.quill.off("selection-change");

      // Remove Quill instance
      const container = document.getElementById(this.options.editorId);
      if (container) {
        container.innerHTML = "";
      }

      this.quill = null;
    }

    this.isInitialized = false;
    this.isVisible = false;
  }

  // Static method to create multiple editors
  static createMultiple(editorsConfig) {
    const editors = {};

    editorsConfig.forEach((config) => {
      const editorName = config.name || config.editorId;
      editors[editorName] = new QuillEditor(config);
    });

    return editors;
  }

  // Static method for form integration
  static setupForm(formId, editorConfigs) {
    const form = document.getElementById(formId);
    if (!form) {
      console.error(`Form #${formId} not found`);
      return null;
    }

    const editors = QuillEditor.createMultiple(editorConfigs);

    // Setup form submission
    form.addEventListener("submit", (e) => {
      // Validate all editors
      let allValid = true;
      const validationResults = {};

      Object.keys(editors).forEach((editorName) => {
        const editor = editors[editorName];
        const validation = editor.validate(editor.options.validation || {});
        validationResults[editorName] = validation;

        if (!validation.isValid) {
          allValid = false;
          console.error(
            `Validation failed for ${editorName}:`,
            validation.errors
          );
        }
      });

      if (!allValid) {
        e.preventDefault();
        // Handle validation errors
        if (window.showValidationErrors) {
          window.showValidationErrors(validationResults);
        }
      }
    });

    return { form, editors };
  }
}
