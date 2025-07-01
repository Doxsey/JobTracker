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
              name="email_from"
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
              name="email_url"
              placeholder="Email URL"
            />
          </div>
        </div>

        <div class="row">
          <div class="md-3">
            <textarea
              class="form-control"
              id="emailBrief"
                name="email_brief"
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
              name="email_date"
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
                name="closed_date"
              />
            </div>
          </div>

          <div class="row">
            <div class="md-3">
              <input
                class="form-control"
                type="text"
                name="closing_reason"
                placeholder="Closing reason"
                aria-label="default input example"
              />
            </div>
          </div>`

}

