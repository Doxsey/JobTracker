class ShowJobActivity {
    constructor(selectedActivity, dynamicFieldsContainer, dynamicFieldsForm, jobId) {
        this.selectedActivity = selectedActivity;
        this.dynamicFieldsContainer = document.getElementById(dynamicFieldsContainer);
        this.dynamicFieldsForm = document.getElementById(dynamicFieldsForm);
        this.jobId = jobId;

        this.init();
    }

    init() {
        this.updateFormFields(this.selectedActivity);

        const addActivityButton = document.getElementById('addActivityButton');

        const dateInputs = this.dynamicFieldsForm.querySelectorAll('input[type="date"]');
            const today = new Date().toISOString().split('T')[0]; // Format: YYYY-MM-DD

            dateInputs.forEach(input => {
                input.value = today;
            });

        addActivityButton.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent form submission
            // console.log("Add Activity Button Clicked");

            if (!this.dynamicFieldsForm) {
                console.error("Dynamic fields form not found");
                return;
            }

            const formData = new FormData(this.dynamicFieldsForm);
            const data = Object.fromEntries(formData.entries());
            console.log("Form Data:", JSON.stringify(data, null, 2));

            // Exclude "activity_date" from data before stringifying
            const { activity_date, ...dataWithoutDate } = data;
            const request_data = {
                job_id: this.jobId,
                activity_type: this.selectedActivity,
                activity_date: data.activity_date || new Date().toISOString().split('T')[0], // Default to today if not provided
                activity_json_data: JSON.stringify(dataWithoutDate)
            };
            console.log("Request Data:", JSON.stringify(request_data, null, 2));


            fetch('/job_activities/api/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(request_data)
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(result => {
                console.log('Activity added:', result);
                // Optionally, update UI or reset form here
            })
            .catch(error => {
                console.error('Error adding activity:', error);
            });

            // this.updateFormFields(this.selectedActivity);
        });
    }


    updateFormFields(activityType) {
        this.dynamicFieldsContainer.innerHTML = ''; // Clear previous content

        if (activityType && activityTemplates[activityType]) {
            const activityDateRow = document.createElement('div');
            activityDateRow.className = 'row';

            const activityDateCol = document.createElement('div');
            activityDateCol.className = 'md-3';

            const activityDateLabel = document.createElement('label');
            activityDateLabel.setAttribute('for', 'activity-date');
            activityDateLabel.className = 'form-label';
            activityDateLabel.textContent = 'Date of Activity';

            const emailDateInput = document.createElement('input');
            emailDateInput.type = 'date';
            emailDateInput.className = 'form-control';
            emailDateInput.id = 'activity-date';
            emailDateInput.name = 'activity_date';

            activityDateCol.appendChild(activityDateLabel);
            activityDateCol.appendChild(emailDateInput);
            activityDateRow.appendChild(activityDateCol);

            this.dynamicFieldsContainer.appendChild(activityDateRow);


            // Instead of replacing, append the template content
            const templateDiv = document.createElement('div');
            templateDiv.innerHTML = activityTemplates[activityType];
            // Append all child nodes to preserve structure
            while (templateDiv.firstChild) {
                this.dynamicFieldsContainer.appendChild(templateDiv.firstChild);
            }

            const rowDiv = document.createElement('div');
            rowDiv.className = 'row';

            const colDiv = document.createElement('div');
            colDiv.className = 'col-auto';

            const button = document.createElement('button');
            button.type = 'submit';
            button.className = 'btn btn-primary mb-3';
            button.id = 'addActivityButton';
            button.textContent = 'Add Activity';

            colDiv.appendChild(button);
            rowDiv.appendChild(colDiv);
            this.dynamicFieldsContainer.appendChild(rowDiv);


        }

    }



}