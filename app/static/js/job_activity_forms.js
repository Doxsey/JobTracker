const activityTemplates = {
            'Received Email': `<div class="row">
          <div class="md-3">
            <h6>Received Email Info:</h6>
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
        </div>`,

        'Job Posting Closed': `<div class="row">
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

