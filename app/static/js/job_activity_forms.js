const activityTemplates = {
            'Application Submitted': `
                <div class="field-row">
                    <div class="form-group">
                        <label for="company">Company <span class="required">*</span></label>
                        <input type="text" id="company" name="company" required placeholder="Company name">
                    </div>
                    <div class="form-group">
                        <label for="position">Position <span class="required">*</span></label>
                        <input type="text" id="position" name="position" required placeholder="Job title">
                    </div>
                </div>
                <div class="field-row">
                    <div class="form-group">
                        <label for="dateSubmitted">Date Submitted <span class="required">*</span></label>
                        <input type="date" id="dateSubmitted" name="dateSubmitted" required>
                    </div>
                    <div class="form-group">
                        <label for="applicationMethod">Application Method</label>
                        <select id="applicationMethod" name="applicationMethod">
                            <option value="">Select method...</option>
                            <option value="company_website">Company Website</option>
                            <option value="linkedin">LinkedIn</option>
                            <option value="indeed">Indeed</option>
                            <option value="referral">Referral</option>
                            <option value="recruiter">Recruiter</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label for="applicationUrl">Application URL</label>
                    <input type="url" id="applicationUrl" name="applicationUrl" placeholder="https://...">
                </div>
                <div class="form-group">
                    <label for="notes">Notes</label>
                    <textarea id="notes" name="notes" placeholder="Additional details about the application..."></textarea>
                </div>
            `,

}

