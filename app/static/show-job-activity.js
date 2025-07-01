class ShowJobActivity {
    constructor(selectedActivity, dynamicFieldsContainer) {
        this.selectedActivity = selectedActivity;
        this.dynamicFieldsContainer = document.getElementById(dynamicFieldsContainer);

        
        this.init();
    }

    init() {
        console.log("Initializing ShowJobActivity");
        console.log("Selected Activity:", this.selectedActivity);
        this.updateFormFields(this.selectedActivity);
    }


    updateFormFields(activityType) {
        console.log("Updating form fields for activity type:", activityType);
        this.dynamicFieldsContainer.innerHTML = ''; // Clear previous content

        if (activityType && activityTemplates[activityType]) {
            console.log("Found template for activity type:", activityType);
            this.dynamicFieldsContainer.innerHTML = activityTemplates[activityType];

        }

    }



}