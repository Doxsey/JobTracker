const activityTemplates = {
            'Received Email': `<div class="row">
          <div class="md-3">
            <h5>Received Email Activity:</h5>
          </div>
        </div>

        <div class="row">
          <div class="md-3">
            <input
              type="text"
              class="form-control"
              id="emailFrom"
              name="email-from"
              placeholder="Sender Name"
            />
          </div>
        </div>
        <div class="row">
          <div class="md-3">
            <input
              type="text"
              class="form-control"
              id="emailUrl"
              name="email-url"
              placeholder="Email URL"
            />
          </div>
        </div>

        <div class="row">
          <div class="md-3">
            <textarea
              class="form-control"
              id="emailBrief"
                name="email-brief"
              rows="3"
              placeholder="Email Brief"
            ></textarea>
          </div>
        </div>

        <div class="row">
          <div class="md-3">
            <label for="email-date" class="form-label">Date of Email</label>
            <input
              type="date"
              class="form-control"
              id="email-date"
              name="email-date"
            />
          </div>
        </div>`,

        'Job Posting Closed': `<div class="row">
            <div class="md-3">
              <label for="closed-date" class="form-label"
                >Date Posting Closed:</label
              >
              <input
                type="date"
                class="form-control"
                id="closed-date"
                name="closed-date"
              />
            </div>
          </div>

          <div class="row">
            <div class="md-3">
              <input
                class="form-control"
                type="text"
                name="closing-reason"
                placeholder="Closing reason"
                aria-label="default input example"
              />
            </div>
          </div>`

}

