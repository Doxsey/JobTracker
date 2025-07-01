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

            const request_data = {
                job_id: this.jobId,
                activity_type: this.selectedActivity,
                activity_date: data.activity_date || new Date().toISOString().split('T')[0], // Default to today if not provided
                activity_json_data: JSON.stringify(data)

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
            this.dynamicFieldsContainer.innerHTML = activityTemplates[activityType];

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