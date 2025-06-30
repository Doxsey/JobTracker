class ShowJobActivity {
    constructor(slectedActivity, activityDetailsId) {
        this.slectedActivity = slectedActivity;
        this.detailsRow = document.getElementById(activityDetailsId);

        
        this.init();
    }

    init() {
        console.log("Initializing ShowJobActivity");
        console.log("Selected Activity:", this.slectedActivity);
    }

}